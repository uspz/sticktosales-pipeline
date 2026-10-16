#!/usr/bin/env python3
"""Gera relatórios HTML (prontos para virar Google Doc no Drive).

  relatorio.py metricas <dados.json> <saida.html>
  relatorio.py tarefa <ID|atual> [saida.html]

dados.json (métricas):
{
 "periodo": "2026-10-11 a 2026-10-16",
 "agora": "2026-10-16T22:00:00-03:00",          # opcional, para tirar vídeos < 24 h das médias
 "redes": {
   "tiktok":    [{"data":"20261015190223","titulo":"...","duracao":64,"views":572,"curtidas":35,
                  "comentarios":0,"compartilhamentos":1,"completos":null}],
   "instagram": [{"data":"...","titulo":"...","views":214,"curtidas":1,"salvos":0}],
   "youtube":   [{"data":"...","titulo":"...","views":null,"curtidas":null}]
 },
 "seguidores": {"tiktok":[233,262], "instagram":[null,null], "youtube":[4,8]},
 "acao": "Fazer a próxima aula sobre lucro e preço e tirar dela um corte 'exemplo real'."
}
"""
import html, json, os, sys, time
from datetime import datetime, timedelta, timezone

DIR = os.path.dirname(os.path.abspath(__file__))
NOMES = {"tiktok": "TikTok", "instagram": "Instagram Reels", "youtube": "YouTube"}
CORTE_MAX = 35
E = html.escape


def n(v):
    return "sem dado" if v is None else f"{v:,.0f}".replace(",", ".")


def curto(t, k=60):
    t = (t or "").split("|")[0].split("#")[0].strip()
    return t if len(t) <= k else t[:k - 1] + "…"


def quando(s):
    try:
        return datetime.strptime(str(s)[:14], "%Y%m%d%H%M%S")
    except ValueError:
        return None


def doc(titulo, corpo):
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>{E(titulo)}</title></head>
<body style="font-family:Arial,Helvetica,sans-serif;color:#15202B;max-width:900px">
{corpo}
<p style="color:#6B7780;font-size:11px">Gerado pelo Escritório de Agentes em {time.strftime('%d/%m/%Y %H:%M')}.</p>
</body></html>"""


def tabela(cab, linhas):
    th = "".join(f'<th style="text-align:left;border-bottom:2px solid #15202B;padding:6px 10px">{E(c)}</th>' for c in cab)
    tr = "".join("<tr>" + "".join(f'<td style="border-bottom:1px solid #D5DBD8;padding:6px 10px">{c}</td>' for c in l) + "</tr>" for l in linhas)
    return f'<table style="border-collapse:collapse;width:100%;font-size:13px"><tr>{th}</tr>{tr}</table>'


def metricas(dados_p, saida):
    d = json.load(open(dados_p))
    agora = datetime.now()
    if d.get("agora"):
        try:
            agora = datetime.fromisoformat(d["agora"]).replace(tzinfo=None)
        except ValueError:
            pass
    redes = d.get("redes", {})
    linhas_tot, blocos, destaque = [], [], None
    tk = redes.get("tiktok") or []
    for rede, vids in redes.items():
        vs = [v for v in vids if v.get("views") is not None]
        tot = sum(v["views"] for v in vs)
        seg = (d.get("seguidores") or {}).get(rede) or [None, None]
        dif = (seg[1] - seg[0]) if None not in seg else None
        linhas_tot.append([E(NOMES.get(rede, rede)), str(len(vids)), n(tot) if vs else "sem dado",
                           f"{n(seg[0])} → {n(seg[1])}" + (f" ({dif:+d})" if dif is not None else "")])
        if not vs:
            blocos.append(f"<h3>{E(NOMES.get(rede, rede))}</h3><p>Sem views no período (rede sem dados ainda).</p>")
            continue
        maduros = [v for v in vs if (quando(v.get("data")) or agora) <= agora - timedelta(hours=24)] or vs
        top = sorted(vs, key=lambda v: -v["views"])[:3]
        pior = min(maduros, key=lambda v: v["views"])
        if destaque is None or top[0]["views"] > destaque[1]["views"]:
            destaque = (rede, top[0])
        rows = [[E(curto(v.get("titulo"))), n(v["views"]), n(v.get("curtidas")),
                 (f'{v["completos"]:.0f}%' if v.get("completos") is not None else "sem dado")] for v in top]
        blocos.append(f"<h3>{E(NOMES.get(rede, rede))}</h3>" + tabela(["Top 3", "Views", "Curtidas", "% assistiu inteiro"], rows)
                      + f"<p>Pior com mais de 24 h no ar: <b>{E(curto(pior.get('titulo')))}</b>, {n(pior['views'])} views.</p>")
    # corte x aula (TikTok tem a duração)
    ca = ""
    if tk:
        mad = [v for v in tk if v.get("views") is not None and v.get("duracao") and
               (quando(v.get("data")) or agora) <= agora - timedelta(hours=24)]
        c = [v["views"] for v in mad if v["duracao"] <= CORTE_MAX]
        a = [v["views"] for v in mad if v["duracao"] > CORTE_MAX]
        if c or a:
            ca = "<h2>Corte (até 35 s) x aula (acima de 35 s), TikTok</h2>" + tabela(
                ["Formato", "Vídeos", "Views médias"],
                [["Corte", str(len(c)), n(sum(c) / len(c)) if c else "sem dado"],
                 ["Aula", str(len(a)), n(sum(a) / len(a)) if a else "sem dado"]]) + \
                "<p style='font-size:12px;color:#6B7780'>Vídeos com menos de 24 h ficam fora das médias.</p>"
    top_txt = (f"Melhor vídeo: <b>{E(curto(destaque[1].get('titulo')))}</b> com {n(destaque[1]['views'])} views no "
               f"{E(NOMES.get(destaque[0], destaque[0]))}.") if destaque else "Sem views no período."
    corpo = (f"<h1>Relatório de métricas · {E(d.get('periodo', ''))}</h1><p style='font-size:16px'>{top_txt}</p>"
             "<h2>Resumo por rede</h2>" + tabela(["Rede", "Vídeos", "Views", "Seguidores"], linhas_tot)
             + ca + "<h2>Detalhe</h2>" + "".join(blocos)
             + (f"<h2>Ação recomendada</h2><p style='font-size:15px'><b>{E(d['acao'])}</b></p>" if d.get("acao") else ""))
    open(saida, "w").write(doc(f"Métricas {d.get('periodo', '')}", corpo))
    print(saida)


def tarefa(tid, saida=None):
    e = json.load(open(os.path.join(DIR, "estado.json")))
    if tid == "atual":
        tid = e.get("atual")
    t = next((x for x in e["tarefas"] if x["id"] == tid), None)
    if not t:
        sys.exit(f"tarefa não encontrada: {tid}")
    evs = [x for x in e["eventos"] if x.get("tarefa") == tid]
    hm = lambda s: time.strftime("%H:%M:%S", time.localtime(s))
    dur = {}
    abertos = {}
    for x in evs:
        if x["tipo"] == "inicio":
            abertos[x["de"]] = x["t"]
        elif x["tipo"] in ("fim", "devolve", "bloqueio", "conclui") and x["de"] in abertos:
            dur[x["de"]] = dur.get(x["de"], 0) + x["t"] - abertos.pop(x["de"])
    total = ((t.get("fim") or time.time()) - t["criada"])
    rotulo = {"passa": "passou", "inicio": "começou", "fim": "terminou", "devolve": "devolveu", "bloqueio": "bloqueou",
              "conclui": "concluiu", "tarefa": "abriu a tarefa", "tokens": "economizou", "pedido": "pedido", "faz": "faz"}
    linhas = [[hm(x["t"]), E(rotulo.get(x["tipo"], x["tipo"])),
               E(x["de"] or "usuário") + (f" → {E(x['para'])}" if x.get("para") else ""), E(x.get("texto") or "")]
              for x in evs if x["tipo"] != "inicio"]
    pasta = os.path.join(DIR, "tarefas", tid)
    entregas = sorted(f for f in os.listdir(pasta) if f[:2].isdigit()) if os.path.isdir(pasta) else []
    corpo = (f"<h1>{E(t['titulo'])}</h1><p>Status: <b>{'concluída' if t['status'] == 'concluida' else 'em andamento'}</b> · "
             f"duração {int(total // 60)} min {int(total % 60)} s · "
             f"{sum(x['tipo'] == 'passa' for x in evs)} passagens · {sum(x['tipo'] == 'devolve' for x in evs)} devoluções</p>"
             f"<p>Caminho: {' → '.join(E(s) for s in t['etapas']) or '-'}</p>"
             "<h2>Tempo por setor</h2>" + tabela(["Setor", "Tempo"], [[E(k), f"{int(v // 60)} min {int(v % 60)} s"] for k, v in sorted(dur.items(), key=lambda kv: -kv[1])])
             + "<h2>Linha do tempo</h2>" + tabela(["Hora", "O quê", "Quem", "Detalhe"], linhas)
             + ("<h2>Entregas</h2><ul>" + "".join(f"<li>{E(f)}</li>" for f in entregas) + "</ul>" if entregas else ""))
    saida = saida or os.path.join(pasta, "relatorio.html")
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    open(saida, "w").write(doc(t["titulo"], corpo))
    print(saida)


if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) >= 3 and a[0] == "metricas":
        metricas(a[1], a[2])
    elif len(a) >= 2 and a[0] == "tarefa":
        tarefa(a[1], a[2] if len(a) > 2 else None)
    else:
        print(__doc__)

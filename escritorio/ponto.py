#!/usr/bin/env python3
"""Bate-ponto do escritório: grava o estado que o painel mostra ao vivo.

  ponto.py tarefa "<título>"            cria tarefa (imprime o ID) e a torna atual
  ponto.py inicio <agente> "<texto>"    agente começa a trabalhar
  ponto.py faz <agente> "<texto>"       atualiza o que o agente está fazendo
  ponto.py fim <agente> "<texto>" [--conclui]   termina (com --conclui fecha a tarefa)
  ponto.py passa <de> <para> "<texto>"  passa o trabalho (papel andando no painel)
  ponto.py devolve <de> <para> "<motivo>"
  ponto.py bloqueio <agente> "<motivo>"
  ponto.py tokens <agente> <n>          registra tokens economizados
  ponto.py resumo                       resumo em texto
  ponto.py zera                         limpa o estado
  ponto.py demo                         simula um dia de trabalho (para testar o painel)
  ponto.py hook                         usado pelos hooks do Claude Code (lê JSON no stdin)
"""
import fcntl, json, os, re, sys, time
from contextlib import contextmanager

DIR = os.path.dirname(os.path.abspath(__file__))
ESTADO = os.path.join(DIR, "estado.json")
TAREFAS = os.path.join(DIR, "tarefas")
AGENTES = ["aria", "enxuto", "analista", "crescimento", "metricas", "roteirista", "conteudo",
           "programador", "editor", "revisor", "juridico", "postador", "administrador"]
# subagentes nativos do Claude Code → setor mais parecido
APELIDOS = {"explore": "analista", "plan": "analista", "general-purpose": "programador",
            "claude": "programador", "fork": "aria",
            "advogado": "juridico", "diretor-conteudo": "conteudo", "growth": "crescimento"}
MAX_EVENTOS = 300


def agora():
    return round(time.time(), 3)


def vazio():
    return {"versao": 0, "atualizado": agora(), "atual": None, "ultimo": None,
            "agentes": {a: {"status": "livre", "faz": "", "desde": agora(), "tarefa": None} for a in AGENTES},
            "tarefas": [], "eventos": [], "tokens": {"economizados": 0, "por_agente": {}}}


@contextmanager
def estado():
    os.makedirs(DIR, exist_ok=True)
    with open(ESTADO + ".lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        try:
            with open(ESTADO) as f:
                e = json.load(f)
        except (OSError, ValueError):
            e = vazio()
        for a in AGENTES:
            e["agentes"].setdefault(a, {"status": "livre", "faz": "", "desde": agora(), "tarefa": None})
        yield e
        e["versao"] += 1
        e["atualizado"] = agora()
        e["eventos"] = e["eventos"][-MAX_EVENTOS:]
        tmp = ESTADO + ".tmp"
        with open(tmp, "w") as f:
            json.dump(e, f, ensure_ascii=False, separators=(",", ":"))
        os.replace(tmp, ESTADO)


def norm(nome):
    n = (nome or "").strip().lower()
    n = APELIDOS.get(n, n)
    return n if n in AGENTES else None


def evento(e, tipo, de=None, para=None, texto=""):
    e["eventos"].append({"t": agora(), "tipo": tipo, "de": de, "para": para,
                         "texto": texto[:200], "tarefa": e.get("atual")})


def tarefa_atual(e):
    for t in e["tarefas"]:
        if t["id"] == e.get("atual"):
            return t
    return None


def marca(e, ag, status, faz=None):
    a = e["agentes"][ag]
    if a["status"] != status:
        a["desde"] = agora()
    a["status"] = status
    if faz is not None:
        a["faz"] = faz[:140]
    a["tarefa"] = e.get("atual")
    t = tarefa_atual(e)
    if t and ag != "aria" and status == "trabalhando" and (not t["etapas"] or t["etapas"][-1] != ag):
        t["etapas"].append(ag)


def nova_tarefa(e, titulo):
    slug = re.sub(r"[^a-z0-9]+", "-", titulo.lower())[:30].strip("-") or "tarefa"
    tid = time.strftime("T-%Y%m%d-%H%M%S-") + slug
    os.makedirs(os.path.join(TAREFAS, tid), exist_ok=True)
    with open(os.path.join(TAREFAS, tid, "00-pedido.md"), "w") as f:
        f.write(f"# {titulo}\n\ncriada: {time.strftime('%Y-%m-%d %H:%M')}\n")
    e["tarefas"].append({"id": tid, "titulo": titulo[:80], "status": "aberta",
                         "criada": agora(), "etapas": [], "fim": None})
    e["tarefas"] = e["tarefas"][-30:]
    e["atual"], e["ultimo"] = tid, None
    evento(e, "tarefa", "aria", None, titulo)
    return tid


# ---------- ações ----------
def inicio(e, ag, texto, de=None):
    de = de or e.get("ultimo") or ("aria" if ag != "aria" else None)
    if de and de != ag:
        evento(e, "passa", de, ag, texto)
        e["eventos"][-1]["volta"] = e.get("ult_status") == "devolvido"
    e["ult_status"] = None
    evento(e, "inicio", ag, None, texto)
    marca(e, ag, "trabalhando", texto)


def fim(e, ag, texto, conclui=False, status="ok"):
    novo = {"ok": "livre", "devolvido": "livre", "bloqueado": "bloqueado"}[status]
    tipo = {"ok": "fim", "devolvido": "devolve", "bloqueado": "bloqueio"}[status]
    evento(e, tipo, ag, None, texto)
    marca(e, ag, novo, texto if status != "ok" else "")
    e["ultimo"], e["ult_status"] = ag, status
    if conclui:
        t = tarefa_atual(e)
        if t:
            t["status"], t["fim"] = "concluida", agora()
        evento(e, "conclui", ag, None, texto)
        for a in e["agentes"].values():
            if a["status"] != "bloqueado":
                a["status"], a["faz"] = "livre", ""
        e["ultimo"] = None


def texto_de(resp):
    if isinstance(resp, str):
        return resp
    if isinstance(resp, dict):
        return "\n".join(texto_de(v) for v in resp.values())
    if isinstance(resp, list):
        return "\n".join(texto_de(v) for v in resp)
    return ""


def status_da_resposta(resp):
    s = texto_de(resp)
    m = re.search(r"status:\s*(ok|devolvido|bloqueado)[^\n]*\n?([^\n]*)", s, re.I)
    if not m:
        return "ok", ""
    return m.group(1).lower(), re.sub(r"^\w+:\s*", "", m.group(2)).strip()


def hook():
    try:
        d = json.load(sys.stdin)
    except ValueError:
        return
    ev = d.get("hook_event_name", "")
    with estado() as e:
        if ev == "UserPromptSubmit":
            p = (d.get("prompt") or "").strip().replace("\n", " ")
            evento(e, "pedido", None, "aria", p[:120])
            marca(e, "aria", "trabalhando", "lendo o pedido: " + p[:80])
        elif ev == "Stop":
            if e["agentes"]["aria"]["status"] == "trabalhando":
                marca(e, "aria", "livre", "")
        elif ev in ("PreToolUse", "PostToolUse") and d.get("tool_name") in ("Task", "Agent"):
            ti = d.get("tool_input") or {}
            ag = norm(ti.get("subagent_type") or "general-purpose")
            if not ag:
                return
            desc = ti.get("description") or ""
            if ev == "PreToolUse":
                inicio(e, ag, desc)
                marca(e, "aria", "aguardando", f"esperando {ag}")
            else:
                st, motivo = status_da_resposta(d.get("tool_response"))
                fim(e, ag, (motivo if st != "ok" and motivo else desc), status=st)
                if not any(a["status"] == "trabalhando" for a in e["agentes"].values()):
                    marca(e, "aria", "trabalhando", "lendo a entrega de " + ag)


def resumo():
    with estado() as e:
        t = tarefa_atual(e)
        print("tarefa atual:", t["titulo"] if t else "-", f"({t['status']})" if t else "")
        for a, v in e["agentes"].items():
            print(f"  {a:14} {v['status']:12} {v['faz']}")
        print("tokens economizados:", e["tokens"]["economizados"])
        print("tarefas:", sum(x["status"] == "concluida" for x in e["tarefas"]), "concluídas /", len(e["tarefas"]))


def demo():
    passos = [
        ("tarefa", "Lição 28: lucro de verdade"),
        ("inicio", "aria", "montando o plano"), ("fim", "aria", "plano pronto"),
        ("inicio", "enxuto", "encurtando plano e briefings"), ("tokens", "enxuto", 1840),
        ("fim", "enxuto", "-42% no plano"),
        ("inicio", "metricas", "puxando Metricool 7 dias"), ("fim", "metricas", "lucro é o tema campeão"),
        ("inicio", "crescimento", "tema tem potencial?"), ("fim", "crescimento", "potencial alto + 1 teste"),
        ("inicio", "roteirista", "roteiro PT 140 palavras"), ("fim", "roteirista", "roteiro + 3 ganchos"),
        ("inicio", "conteudo", "nota do roteiro"), ("devolve", "conteudo", "gancho 5/10: abrir com a conta"),
        ("inicio", "roteirista", "novo gancho"), ("fim", "roteirista", "gancho com a conta"),
        ("inicio", "conteudo", "nota de novo"), ("fim", "conteudo", "média 8,4"),
        ("inicio", "revisor", "conferindo roteiro"), ("fim", "revisor", "ok, 140 palavras"),
        ("inicio", "juridico", "promessa de ganho?"), ("fim", "juridico", "sem risco relevante"),
        ("inicio", "editor", "render aula + cortes"), ("fim", "editor", "3 mp4 prontos"),
        ("inicio", "revisor", "LUFS, frames, voz no 1º s"),
        ("devolve", "revisor", "pico em −0,1 dB no corte 2"),
        ("inicio", "editor", "corrigindo pico do corte 2"), ("fim", "editor", "pico −0,8 dB"),
        ("inicio", "revisor", "reconferindo"), ("fim", "revisor", "tudo ok"),
        ("inicio", "postador", "verificando aprovação"), ("bloqueio", "postador", "aguardando aprovação do Ninety"),
        ("inicio", "administrador", "registrando decisões e commit"), ("fim", "administrador", "branch atualizada"),
        ("inicio", "aria", "fechando entrega"), ("conclui", "aria", "lição 28 pronta, falta aprovar post"),
    ]
    for p in passos:
        with estado() as e:
            k = p[0]
            if k == "tarefa":
                nova_tarefa(e, p[1])
            elif k == "inicio":
                inicio(e, p[1], p[2])
            elif k == "fim":
                fim(e, p[1], p[2])
            elif k == "devolve":
                fim(e, p[1], p[2], status="devolvido")
            elif k == "bloqueio":
                fim(e, p[1], p[2], status="bloqueado")
            elif k == "tokens":
                e["tokens"]["economizados"] += p[2]
                evento(e, "tokens", p[1], None, f"{p[2]} tokens economizados")
            elif k == "conclui":
                fim(e, p[1], p[2], conclui=True)
        print(*p)
        time.sleep(3.5)


def main(a):
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        return
    cmd, r = a[0], a[1:]
    if cmd == "hook":
        try:
            hook()
        except Exception as ex:  # hook nunca pode travar o Claude
            print(f"ponto: {ex}", file=sys.stderr)
        return
    if cmd == "resumo":
        return resumo()
    if cmd == "demo":
        return demo()
    if cmd == "zera":
        with estado() as e:
            e.clear()
            e.update(vazio())
        return print("estado zerado")
    with estado() as e:
        if cmd == "tarefa":
            print(nova_tarefa(e, " ".join(r) or "tarefa"))
            return
        ag = norm(r[0]) if r else None
        if not ag:
            sys.exit(f"agente desconhecido: {r[:1]}. Use: {', '.join(AGENTES)}")
        if cmd in ("inicio", "faz"):
            (inicio(e, ag, " ".join(r[1:])) if cmd == "inicio" or e["agentes"][ag]["status"] != "trabalhando"
             else marca(e, ag, "trabalhando", " ".join(r[1:])))
            if cmd == "faz":
                evento(e, "faz", ag, None, " ".join(r[1:]))
        elif cmd == "fim":
            conc = "--conclui" in r
            fim(e, ag, " ".join(x for x in r[1:] if x != "--conclui"), conclui=conc)
        elif cmd in ("passa", "devolve"):
            para = norm(r[1]) if len(r) > 1 else None
            if not para:
                sys.exit("uso: ponto.py %s <de> <para> \"texto\"" % cmd)
            txt = " ".join(r[2:])
            if cmd == "devolve":
                fim(e, ag, txt, status="devolvido")
            else:
                fim(e, ag, txt)
            inicio(e, para, txt, de=ag)
        elif cmd == "bloqueio":
            fim(e, ag, " ".join(r[1:]), status="bloqueado")
        elif cmd == "tokens":
            n = int(r[1]) if len(r) > 1 else 0
            e["tokens"]["economizados"] += n
            e["tokens"]["por_agente"][ag] = e["tokens"]["por_agente"].get(ag, 0) + n
            evento(e, "tokens", ag, None, f"{n} tokens economizados")
        else:
            sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])

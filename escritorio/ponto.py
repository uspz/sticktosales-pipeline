#!/usr/bin/env python3
"""Bate-ponto do escritório: grava o estado que o painel mostra ao vivo.

Tarefas e passagens
  ponto.py tarefa "<título>"                cria tarefa (imprime o ID) e a torna atual
  ponto.py inicio <agente> "<texto>"        agente começa a trabalhar
  ponto.py faz <agente> "<texto>"           atualiza o que o agente está fazendo
  ponto.py fim <agente> "<texto>" [--conclui]
  ponto.py passa <de> <para> "<texto>"      passa o trabalho (a pessoa leva o papel)
  ponto.py devolve <de> <para> "<motivo>"
  ponto.py bloqueio <agente> "<motivo>"
Jornada (estilo CLT)
  ponto.py pausa <agente|todos> "<motivo>"  pausa (tokens acabaram, economia, café…)
  ponto.py volta <agente|todos>             fim da pausa
  ponto.py humor <agente> <feliz|bravo|triste|cansado|focado|neutro>
  ponto.py ensina <instrutor> <para> "<lição>"   grava em licoes.md e o instrutor vai até a mesa
  ponto.py expediente [HH:MM-HH:MM] [almoço HH:MM-HH:MM]
  ponto.py folha                            horas trabalhadas e tokens gastos hoje
Tokens
  ponto.py tokens <agente> <n>              tokens economizados (Enxuto)
  ponto.py gasto <agente> <n>               tokens gastos
  ponto.py orcamento <n>                    orçamento diário de tokens (0 = sem limite)
Outros
  ponto.py resumo | zera | demo | hook
"""
import fcntl, json, os, re, sys, time
from contextlib import contextmanager

DIR = os.path.dirname(os.path.abspath(__file__))
ESTADO = os.path.join(DIR, "estado.json")
TAREFAS = os.path.join(DIR, "tarefas")
LICOES = os.path.join(DIR, "licoes.md")
AGENTES = ["aria", "instrutor", "enxuto", "analista", "crescimento", "metricas", "juridico", "financeiro",
           "roteirista", "conteudo", "designer", "editor", "programador", "revisor",
           "postador", "administrador", "atendimento"]
APELIDOS = {"explore": "analista", "plan": "analista", "general-purpose": "programador",
            "claude": "programador", "fork": "aria", "advogado": "juridico", "diretor-conteudo": "conteudo",
            "growth": "crescimento", "rh": "instrutor", "treinador": "instrutor", "custos": "financeiro",
            "suporte": "atendimento", "comunidade": "atendimento"}
HUMORES = {"feliz", "bravo", "triste", "cansado", "focado", "neutro"}
MAX_EVENTOS = 300


def agora():
    return round(time.time(), 3)


def hoje():
    return time.strftime("%Y-%m-%d")


def novo_agente():
    return {"status": "livre", "faz": "", "desde": agora(), "tarefa": None, "humor": "neutro", "humor_desde": agora()}


def vazio():
    return {"versao": 0, "atualizado": agora(), "atual": None, "ultimo": None,
            "agentes": {a: novo_agente() for a in AGENTES},
            "tarefas": [], "eventos": [], "tokens": {"economizados": 0, "por_agente": {}},
            "pausa": {"ativo": False, "motivo": "", "desde": None, "tipo": None},
            "expediente": {"inicio": "08:00", "fim": "18:00", "almoco": ["12:00", "13:00"]},
            "folha": {}, "orcamento": 0}


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
        base = vazio()
        for k, v in base.items():
            e.setdefault(k, v)
        for a in AGENTES:
            e["agentes"].setdefault(a, novo_agente())
            for k, v in novo_agente().items():
                e["agentes"][a].setdefault(k, v)
        yield e
        e["versao"] += 1
        e["atualizado"] = agora()
        e["eventos"] = e["eventos"][-MAX_EVENTOS:]
        dias = sorted(e["folha"])
        for d in dias[:-7]:  # guarda só 7 dias de folha
            e["folha"].pop(d, None)
        tmp = ESTADO + ".tmp"
        with open(tmp, "w") as f:
            json.dump(e, f, ensure_ascii=False, separators=(",", ":"))
        os.replace(tmp, ESTADO)


def norm(nome):
    n = (nome or "").strip().lower()
    n = APELIDOS.get(n, n)
    return n if n in AGENTES else None


def evento(e, tipo, de=None, para=None, texto="", **extra):
    ev = {"t": agora(), "tipo": tipo, "de": de, "para": para, "texto": str(texto)[:200], "tarefa": e.get("atual")}
    ev.update(extra)
    e["eventos"].append(ev)


def tarefa_atual(e):
    return next((t for t in e["tarefas"] if t["id"] == e.get("atual")), None)


def folha(e, ag):
    return e["folha"].setdefault(hoje(), {}).setdefault(ag, {"seg": 0, "gasto": 0, "entregas": 0, "devolvidas": 0})


def humor(e, ag, h):
    a = e["agentes"][ag]
    a["humor"], a["humor_desde"] = h, agora()


def marca(e, ag, status, faz=None):
    a = e["agentes"][ag]
    if a["status"] != status:
        if a["status"] == "trabalhando":  # banco de horas
            folha(e, ag)["seg"] += max(0, agora() - a["desde"])
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
    e["tarefas"].append({"id": tid, "titulo": titulo[:80], "status": "aberta", "criada": agora(), "etapas": [], "fim": None})
    e["tarefas"] = e["tarefas"][-30:]
    e["atual"], e["ultimo"] = tid, None
    evento(e, "tarefa", "aria", None, titulo)
    return tid


# ---------- ações ----------
def inicio(e, ag, texto, de=None):
    de = de or e.get("ultimo") or ("aria" if ag != "aria" else None)
    volta = e.get("ult_status") == "devolvido"
    if de and de != ag:
        evento(e, "passa", de, ag, texto, volta=volta)
    e["ult_status"] = None
    evento(e, "inicio", ag, None, texto)
    marca(e, ag, "trabalhando", texto)
    humor(e, ag, "bravo" if volta else "focado")


def fim(e, ag, texto, conclui=False, status="ok"):
    novo = {"ok": "livre", "devolvido": "livre", "bloqueado": "bloqueado"}[status]
    tipo = {"ok": "fim", "devolvido": "devolve", "bloqueado": "bloqueio"}[status]
    evento(e, tipo, ag, None, texto)
    marca(e, ag, novo, texto if status != "ok" else "")
    humor(e, ag, {"ok": "feliz", "devolvido": "neutro", "bloqueado": "triste"}[status])
    folha(e, ag)["entregas"] += 1
    if status == "devolvido" and e.get("ultimo") and e["ultimo"] != ag:
        folha(e, e["ultimo"])["devolvidas"] += 1
    e["ultimo"], e["ult_status"] = ag, status
    if conclui:
        t = tarefa_atual(e)
        if t:
            t["status"], t["fim"] = "concluida", agora()
        evento(e, "conclui", ag, None, texto)
        for k, a in e["agentes"].items():
            if a["status"] != "bloqueado":
                marca(e, k, "livre", "")
                humor(e, k, "feliz")
        e["ultimo"] = None


def pausa(e, alvo, motivo, tipo="manual"):
    alvos = AGENTES if alvo == "todos" else [alvo]
    if alvo == "todos":
        e["pausa"] = {"ativo": True, "motivo": motivo, "desde": agora(), "tipo": tipo, "dia": hoje()}
    for a in alvos:
        st = e["agentes"][a]
        st["antes"] = {"status": st["status"], "faz": st["faz"]} if st["status"] != "pausa" else st.get("antes")
        marca(e, a, "pausa", motivo)
    evento(e, "pausa", None if alvo == "todos" else alvo, None, motivo, modo=tipo)


def volta(e, alvo):
    alvos = AGENTES if alvo == "todos" else [alvo]
    if alvo == "todos":
        e["pausa"] = {"ativo": False, "motivo": "", "desde": None, "tipo": None}
    for a in alvos:
        st = e["agentes"][a]
        if st["status"] == "pausa":
            antes = st.pop("antes", None) or {"status": "livre", "faz": ""}
            marca(e, a, antes["status"], antes["faz"])
    evento(e, "volta", None if alvo == "todos" else alvo, None, "fim da pausa")


def ensina(e, de, para, licao):
    os.makedirs(DIR, exist_ok=True)
    nova = not os.path.exists(LICOES)
    with open(LICOES, "a") as f:
        if nova:
            f.write("# Lições aprendidas\n\nUma linha por lição. O instrutor mantém; a Aria consulta antes dos briefings.\n\n")
        f.write(f"- [{para}] {licao} ({hoje()}, tarefa {e.get('atual') or '-'})\n")
    evento(e, "ensina", de, para, licao)


def gasto(e, ag, n):
    if n <= 0:
        return
    folha(e, ag)["gasto"] += n
    orc = e.get("orcamento") or 0
    total = sum(v.get("gasto", 0) for v in e["folha"].get(hoje(), {}).values())
    if orc and total >= orc and not e["pausa"]["ativo"]:
        pausa(e, "todos", f"orçamento do dia atingido ({total:,} tokens)".replace(",", "."), tipo="economia")


# ---------- hooks do Claude Code ----------
def texto_de(resp):
    if isinstance(resp, str):
        return resp
    if isinstance(resp, dict):
        return "\n".join(texto_de(v) for v in resp.values())
    if isinstance(resp, list):
        return "\n".join(texto_de(v) for v in resp)
    return ""


def tokens_de(resp):
    """Procura o total de tokens na resposta da ferramenta Agent/Task (formato varia por versão)."""
    if isinstance(resp, dict):
        for k in ("totalTokens", "total_tokens", "subagent_tokens"):
            if isinstance(resp.get(k), (int, float)):
                return int(resp[k])
        for v in resp.values():
            n = tokens_de(v)
            if n:
                return n
    if isinstance(resp, list):
        for v in resp:
            n = tokens_de(v)
            if n:
                return n
    if isinstance(resp, str):
        m = re.search(r"(?:total_tokens|subagent_tokens|totalTokens)\D{0,4}(\d{3,})", resp)
        if m:
            return int(m.group(1))
    return 0


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
        return 0
    ev = d.get("hook_event_name", "")
    bloquear = None
    with estado() as e:
        p = e["pausa"]
        if p["ativo"] and p.get("tipo") == "economia" and p.get("dia") != hoje():
            volta(e, "todos")  # pausa econômica acaba no dia seguinte
        if ev == "UserPromptSubmit":
            if e["pausa"]["ativo"] and e["pausa"].get("tipo") == "tokens":
                volta(e, "todos")  # o Ninety voltou: os tokens renovaram
            pr = (d.get("prompt") or "").strip().replace("\n", " ")
            evento(e, "pedido", None, "aria", pr[:120])
            if not e["pausa"]["ativo"]:
                marca(e, "aria", "trabalhando", "lendo o pedido: " + pr[:80])
                humor(e, "aria", "focado")
        elif ev == "Stop":
            if e["agentes"]["aria"]["status"] == "trabalhando":
                marca(e, "aria", "livre", "")
        elif ev in ("StopFailure", "Notification"):
            txt = json.dumps(d, ensure_ascii=False).lower()
            if re.search(r"rate.?limit|usage limit|limite|quota|overloaded|credit", txt):
                pausa(e, "todos", "tokens acabaram: aguardando renovar", tipo="tokens")
        elif ev in ("PreToolUse", "PostToolUse") and d.get("tool_name") in ("Task", "Agent"):
            ti = d.get("tool_input") or {}
            ag = norm(ti.get("subagent_type") or "general-purpose")
            if ag:
                desc = ti.get("description") or ""
                if ev == "PreToolUse":
                    if e["pausa"]["ativo"]:
                        bloquear = (f"Escritório em pausa: {e['pausa']['motivo']}. Nenhum agente trabalha agora. "
                                    "Avise o Ninety. Para retomar: python3 escritorio/ponto.py volta todos")
                    else:
                        inicio(e, ag, desc)
                        marca(e, "aria", "aguardando", f"esperando {ag}")
                else:
                    st, motivo = status_da_resposta(d.get("tool_response"))
                    fim(e, ag, (motivo if st != "ok" and motivo else desc), status=st)
                    gasto(e, ag, tokens_de(d.get("tool_response")))
                    if not e["pausa"]["ativo"] and not any(a["status"] == "trabalhando" for a in e["agentes"].values()):
                        marca(e, "aria", "trabalhando", "lendo a entrega de " + ag)
    if bloquear:
        print(bloquear, file=sys.stderr)
        return 2
    return 0


# ---------- relatórios em texto ----------
def hm(seg):
    seg = int(seg)
    return f"{seg // 3600}h{(seg % 3600) // 60:02d}"


def folha_txt():
    with estado() as e:
        dia = e["folha"].get(hoje(), {})
        print(f"Folha de ponto de {hoje()} (expediente {e['expediente']['inicio']}–{e['expediente']['fim']})")
        print(f"  {'agente':14} {'horas':>6} {'entregas':>8} {'devolvidas':>10} {'tokens':>9}")
        tot = 0
        for a in AGENTES:
            v = dict(dia.get(a, {"seg": 0, "gasto": 0, "entregas": 0, "devolvidas": 0}))
            st = e["agentes"][a]
            if st["status"] == "trabalhando":
                v["seg"] += agora() - st["desde"]
            tot += v["gasto"]
            print(f"  {a:14} {hm(v['seg']):>6} {v['entregas']:>8} {v['devolvidas']:>10} {v['gasto']:>9,}".replace(",", "."))
        orc = e.get("orcamento") or 0
        print(f"  total de tokens gastos hoje: {tot:,}".replace(",", ".") + (f" de {orc:,} (orçamento)".replace(",", ".") if orc else ""))
        if e["pausa"]["ativo"]:
            print(f"  EM PAUSA: {e['pausa']['motivo']}")


def resumo():
    with estado() as e:
        t = tarefa_atual(e)
        if e["pausa"]["ativo"]:
            print(f"*** ESCRITÓRIO EM PAUSA: {e['pausa']['motivo']} (desde {time.strftime('%H:%M', time.localtime(e['pausa']['desde']))}) ***")
        print("tarefa atual:", t["titulo"] if t else "-", f"({t['status']})" if t else "")
        for a, v in e["agentes"].items():
            print(f"  {a:14} {v['status']:12} {v['humor']:8} {v['faz']}")
        print("tokens economizados:", e["tokens"]["economizados"])
        print("tarefas:", sum(x["status"] == "concluida" for x in e["tarefas"]), "concluídas /", len(e["tarefas"]))


def demo():
    passos = [
        ("tarefa", "Lição 28: lucro de verdade"),
        ("inicio", "aria", "montando o plano"), ("fim", "aria", "plano pronto"),
        ("inicio", "instrutor", "lições para esta tarefa"), ("fim", "instrutor", "3 lições no briefing"),
        ("inicio", "enxuto", "encurtando plano e briefings"), ("tokens", "enxuto", 1840), ("fim", "enxuto", "-42% no plano"),
        ("inicio", "metricas", "puxando Metricool 7 dias"), ("fim", "metricas", "lucro é o tema campeão"),
        ("inicio", "crescimento", "tema tem potencial?"), ("fim", "crescimento", "potencial alto + 1 teste"),
        ("inicio", "roteirista", "roteiro PT 140 palavras"), ("fim", "roteirista", "roteiro + 3 ganchos"),
        ("inicio", "conteudo", "nota do roteiro"), ("devolve", "conteudo", "gancho 5/10: abrir com a conta"),
        ("ensina", "instrutor", "roteirista", "abra o gancho com o número, não com a pergunta"),
        ("inicio", "roteirista", "novo gancho"), ("fim", "roteirista", "gancho com a conta"),
        ("inicio", "conteudo", "nota de novo"), ("fim", "conteudo", "média 8,4"),
        ("inicio", "juridico", "promessa de ganho?"), ("fim", "juridico", "sem risco relevante"),
        ("inicio", "designer", "capa da lição"), ("fim", "designer", "capa 1080x1920"),
        ("inicio", "editor", "render aula + cortes"), ("fim", "editor", "3 mp4 prontos"),
        ("inicio", "revisor", "LUFS, frames, voz no 1º s"), ("devolve", "revisor", "pico em −0,1 dB no corte 2"),
        ("inicio", "editor", "corrigindo pico do corte 2"), ("fim", "editor", "pico −0,8 dB"),
        ("inicio", "revisor", "reconferindo"), ("fim", "revisor", "tudo ok"),
        ("pausa", "todos", "tokens acabaram: aguardando renovar"), ("volta", "todos"),
        ("inicio", "postador", "verificando aprovação"), ("bloqueio", "postador", "aguardando aprovação do Ninety"),
        ("inicio", "financeiro", "custo da tarefa"), ("fim", "financeiro", "38 mil tokens, dentro do orçamento"),
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
            elif k == "ensina":
                evento(e, "ensina", p[1], p[2], p[3])  # demo não grava licoes.md
            elif k == "pausa":
                pausa(e, p[1], p[2], tipo="tokens")
            elif k == "volta":
                volta(e, p[1])
            elif k == "conclui":
                fim(e, p[1], p[2], conclui=True)
        print(*p)
        time.sleep(8 if k == "pausa" else 3.5)


def main(a):
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        return
    cmd, r = a[0], a[1:]
    if cmd == "hook":
        try:
            sys.exit(hook())
        except SystemExit:
            raise
        except Exception as ex:  # hook nunca pode travar o Claude
            print(f"ponto: {ex}", file=sys.stderr)
        return
    simples = {"resumo": resumo, "demo": demo, "folha": folha_txt}
    if cmd in simples:
        return simples[cmd]()
    if cmd == "zera":
        with estado() as e:
            e.clear()
            e.update(vazio())
        return print("estado zerado")
    with estado() as e:
        if cmd == "tarefa":
            print(nova_tarefa(e, " ".join(r) or "tarefa"))
            return
        if cmd == "orcamento":
            e["orcamento"] = int(r[0]) if r else 0
            return print("orçamento diário:", e["orcamento"] or "sem limite")
        if cmd == "expediente":
            txt = " ".join(r)
            hs = re.findall(r"(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})", txt)
            if hs:
                e["expediente"]["inicio"], e["expediente"]["fim"] = hs[0]
            if len(hs) > 1:
                e["expediente"]["almoco"] = list(hs[1])
            return print("expediente:", e["expediente"])
        if cmd in ("pausa", "volta") and r and r[0] == "todos":
            return pausa(e, "todos", " ".join(r[1:]) or "pausa", tipo="manual") if cmd == "pausa" else volta(e, "todos")
        ag = norm(r[0]) if r else None
        if not ag:
            sys.exit(f"agente desconhecido: {r[:1]}. Use: {', '.join(AGENTES)} (ou 'todos' em pausa/volta)")
        txt = " ".join(r[1:])
        if cmd in ("inicio", "faz"):
            if cmd == "inicio" or e["agentes"][ag]["status"] != "trabalhando":
                inicio(e, ag, txt)
            else:
                marca(e, ag, "trabalhando", txt)
            if cmd == "faz":
                evento(e, "faz", ag, None, txt)
        elif cmd == "fim":
            fim(e, ag, " ".join(x for x in r[1:] if x != "--conclui"), conclui="--conclui" in r)
        elif cmd in ("passa", "devolve", "ensina"):
            para = norm(r[1]) if len(r) > 1 else None
            if not para:
                sys.exit(f"uso: ponto.py {cmd} <de> <para> \"texto\"")
            txt = " ".join(r[2:])
            if cmd == "ensina":
                ensina(e, ag, para, txt)
            else:
                fim(e, ag, txt, status="devolvido" if cmd == "devolve" else "ok")
                inicio(e, para, txt, de=ag)
        elif cmd == "bloqueio":
            fim(e, ag, txt, status="bloqueado")
        elif cmd == "pausa":
            pausa(e, ag, txt or "pausa")
        elif cmd == "volta":
            volta(e, ag)
        elif cmd == "humor":
            h = (r[1] if len(r) > 1 else "").lower()
            if h not in HUMORES:
                sys.exit(f"humor: {', '.join(sorted(HUMORES))}")
            humor(e, ag, h)
            evento(e, "humor", ag, None, h)
        elif cmd == "tokens":
            n = int(r[1]) if len(r) > 1 else 0
            e["tokens"]["economizados"] += n
            e["tokens"]["por_agente"][ag] = e["tokens"]["por_agente"].get(ag, 0) + n
            evento(e, "tokens", ag, None, f"{n} tokens economizados")
        elif cmd == "gasto":
            gasto(e, ag, int(r[1]) if len(r) > 1 else 0)
        else:
            sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])

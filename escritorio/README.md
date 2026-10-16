# Escritório: time de agentes

Treze agentes em 7 áreas, cada um com um setor, que passam o trabalho de um para o outro até a entrega. Serve para qualquer pedido (vídeo, código, análise, organização), não só para o canal.

```
Ninety ──pedido──▶ Aria ──▶ Enxuto ──▶ [setores na ordem do plano] ──▶ Revisor ──▶ Postador* ──▶ Aria ──entrega──▶ Ninety
                                          ▲                              │
                                          └──────── devolvido ───────────┘   (*só com aprovação)
```

| agente | setor |
|---|---|
| **aria** | coordenação: plano, chamadas e entrega final (é quem fala com você) |
| **enxuto** | economia de tokens: encurta planos, briefings, prompts, comandos e código |
| analista | pesquisa e análise |
| metricas | Metricool e números: relatório no Drive + notificação a cada análise |
| roteirista | roteiros, ganchos, legendas, textos |
| programador | código em qualquer linguagem |
| editor | render, áudio, imagem, ffmpeg |
| conteudo | diretor de conteúdo: nota o roteiro (gancho, utilidade, ritmo) e devolve se ficar abaixo de 7 |
| crescimento | estrategista: isso escala? propõe 1 experimento com meta |
| revisor | qualidade técnica: testa, mede, aprova ou devolve |
| juridico | advogado: publicidade (CDC/CONAR), direito autoral, LGPD, marcas, contratos |
| postador | publicação e deploy, só com "aprovado" |
| administrador | git, arquivos, registro de decisões, custos |

As definições estão em `.claude/agents/`. As regras comuns ficam em `escritorio/PROTOCOLO.md`, lidas uma vez por tarefa, para economizar tokens.

## Como usar
- **Pedir algo**: abra o Claude Code neste repositório e peça normalmente. O `CLAUDE.md` manda a sessão principal agir como a Aria e delegar. Para forçar, use `claude --agent aria`.
- **Ver ao vivo**: `python3 escritorio/servidor.py` e abra http://localhost:8787. É um escritório em 3D: cada área tem as mesas da equipe, as pessoas digitam quando estão trabalhando e levantam para levar o papel ao próximo setor (papel vermelho é devolução). Arraste para girar, role para aproximar e clique numa pessoa para focar nela. O telão da diretoria mostra a tarefa e o painel de números mostra passagens, devoluções e tokens poupados. O three.js vem do CDN, com uma cópia em `escritorio/vendor/` para funcionar sem internet.
- **Relatórios**: `python3 escritorio/relatorio.py metricas dados.json saida.html` (métricas) e `python3 escritorio/relatorio.py tarefa <ID|atual>` (linha do tempo da tarefa). Os dois vão para a pasta do Drive "Stick To Sales · Relatórios" quando a ferramenta do Drive está disponível.
- **Testar o painel sem Claude**: `python3 escritorio/ponto.py demo`, com o servidor aberto.
- **Ver em texto**: `python3 escritorio/ponto.py resumo`.

## Como o painel sabe o que acontece
1. Os hooks em `.claude/settings.json` chamam `ponto.py hook` quando você manda um pedido, quando um agente é chamado, quando ele termina e quando a sessão para. Ninguém precisa lembrar de bater ponto.
2. Se a entrega de um agente traz `status: devolvido` ou `status: bloqueado`, o painel mostra a devolução (papel vermelho) ou o bloqueio ("!").
3. `ponto.py faz <agente> "<texto>"` só acrescenta detalhe ao balão.
4. O estado fica em `escritorio/estado.json` e as tarefas em `escritorio/tarefas/<ID>/` (plano e entregas). As duas coisas ficam fora do git.

## Limites
- Um subagente não chama outro: quem encadeia é sempre a Aria, na sessão principal.
- A voz PT continua manual (site de voz). O editor para em `bloqueado: aguardando voz PT`.

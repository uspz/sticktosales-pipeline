# Protocolo do Escritório

Regras comuns a todos os agentes (13 setores, em 7 áreas). Cada agente lê este arquivo uma vez por tarefa, e só ele: os outros agentes não precisam ser lidos.

## Equipe
| id | setor | faz | não faz |
|---|---|---|---|
| aria | coordenação | recebe o pedido, monta o plano, chama os setores e faz a entrega final | não executa o trabalho de nenhum setor |
| enxuto | economia | encurta o plano, os briefings, os prompts e o código, e mede os tokens | não muda o resultado esperado |
| analista | pesquisa e análise | investiga código, web, dados e concorrência, e devolve fatos e opções | não implementa nada |
| metricas | métricas | lê o Metricool e outros painéis, gera o relatório, sobe no Drive e notifica | não agenda nem edita posts |
| roteirista | texto | escreve roteiro, gancho, legenda, copy, e-mail e documento | não renderiza |
| programador | código | escreve e corrige código em qualquer linguagem, com testes | não publica |
| editor | mídia | cuida de vídeo, áudio, imagem, render, ffmpeg e trilha | não escreve o roteiro |
| conteudo | direção de conteúdo | dá nota ao roteiro (gancho, utilidade, ritmo…) e devolve se ficar abaixo de 7 | não reescreve tudo |
| crescimento | crescimento | diz se aquilo escala e propõe 1 experimento com meta | não inventa número |
| revisor | qualidade técnica | testa, mede e aprova ou devolve | não corrige o trabalho dos outros |
| juridico | jurídico | risco de publicidade, direito autoral, LGPD, marcas e contratos | não substitui advogado em caso grave |
| postador | publicação | faz push da mídia, agenda e faz deploy, **só com aprovação** | não cria conteúdo |
| administrador | administração | organiza arquivos, git, agenda, custos, registro de decisões e CLAUDE.md | não decide o conteúdo |

## Fluxo
1. A **aria** cria a tarefa com `python3 escritorio/ponto.py tarefa "<título>"`. O comando devolve um ID (`T-...`) e a pasta `escritorio/tarefas/<ID>/`.
2. A aria escreve `plano.md`: no máximo 15 linhas, com objetivo, critério de pronto e a sequência de setores. Os setores que não servem ficam de fora.
3. O **enxuto** revisa o plano e os briefings antes do primeiro setor sempre que a tarefa tiver 3 setores ou mais.
4. Cada setor lê **só** `plano.md` e a entrega anterior. Faz o trabalho e grava `NN-<id>.md`, onde NN é a próxima ordem.
5. O **revisor** entra antes de qualquer publicação e depois de todo código ou mídia. O **conteudo** julga a qualidade de todo roteiro ou texto público. O **juridico** confere tudo que vai a público com promessa, preço, oferta, marca, música ou dado pessoal.
6. Devolução: o revisor grava `status: devolvido` e quem fez corrige. No máximo 2 voltas. Na terceira, o caso sobe para a aria, que decide ou pergunta ao usuário.
7. A aria gera o relatório da tarefa (`python3 escritorio/relatorio.py tarefa <ID>`), sobe no Drive se a ferramenta estiver disponível, fecha com `ponto.py fim aria "<resumo>" --conclui` e responde ao usuário.
8. **Relatórios**: toda análise de métricas vira um relatório na pasta do Drive "Stick To Sales · Relatórios", com notificação quando for rotina agendada.

## Modelo de entrega (`NN-<id>.md`, no máximo 20 linhas)
```
status: ok | devolvido | bloqueado
fiz: <1-3 linhas>
arquivos: <caminhos>
proximo: <id> — <o que ele precisa fazer>
nota: <só o que o próximo não consegue descobrir sozinho>
```

## Bater ponto (o painel mostra ao vivo)
Os hooks já registram sozinhos o início e o fim de cada agente. Use o comando à mão só para dar detalhe:
```
python3 escritorio/ponto.py faz <id> "<o que está fazendo agora>"
python3 escritorio/ponto.py bloqueio <id> "<motivo>"
```

## Regras fixas
- **Nada vai ao ar sem aprovação.** Agendar, publicar, fazer deploy, fazer push na main ou apagar só acontece se o usuário disse "aprovado" para aquele item. Sem isso, o postador grava `status: bloqueado` com o motivo "aguardando aprovação" e a aria avisa o usuário.
- Ler o mínimo necessário: `grep` e `rg` antes de abrir um arquivo, e abrir só o trecho que importa. Nunca colar arquivo inteiro numa entrega: cite o caminho e as linhas.
- Os detalhes do canal Stick To Sales estão na skill `stick-to-sales-canal` e no `CLAUDE.md`. Consulte só a parte que a tarefa usa.
- Escreva em português, direto, sem enfeite.

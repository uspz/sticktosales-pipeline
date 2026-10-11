from board import RED, GREEN, MARK, INK
HOOK = 'Nunca dê *desconto* *de* *graça*'
CUT_HOOKS = {'dicas': 'Cliente pediu *desconto*? Faz isso', 'exemplo': 'Ela transformou desconto em *venda* *dupla*'}
CAP = {'aula': ('Nunca dê desconto de graça', 'como negociar desconto sem perder dinheiro 💸 Salva pra usar no próximo cliente'),
       'dicas': ('Cliente pediu desconto? Faz isso', '3 respostas que protegem seu preço 💰 Aula completa no perfil'),
       'exemplo': ('Como transformar desconto em venda dupla', 'exemplo real de negociação 🧥 Você dá desconto fácil? 👇')}
HT = '#desconto #negociacao #vendasonline'
TITLES = ['DESCONTO DE GRAÇA', 'O PROBLEMA', 'DICA 1: TROQUE, NÃO DÊ', 'DICA 2: BÔNUS NO LUGAR', 'DICA 3: O QUE FALTA?',
          'EXEMPLO', 'UMA REGRA', 'NESTA SEMANA', 'POR HOJE É SÓ!']
MARKED = [
    "{brow}*Nunca dê {draw:tag}{point:tag}desconto de {draw:nox}{neg}graça. Desconto sem troca ensina o cliente a {draw:again}{point:again}pedir de novo.",
    "O problema não é o {draw:ok1}desconto. É o desconto {draw:nomot}{point:nomot}sem motivo, que faz seu preço {draw:falso}{shrug}parecer falso.",
    "Dica um: troque, não dê. Desconto só se ele {draw:c1}{count1}levar mais, {draw:c2}{count2}pagar à vista, ou {draw:c3}{count3}fechar hoje.",
    "Dica dois: ofereça bônus no lugar. Um {draw:gift}{point:gift}brinde ou {draw:truck}{point:truck}frete grátis custa menos pra você e {draw:vale}{present_hi}vale mais pra ele.",
    "{walk:610}Dica três: {draw:falta}{present}pergunte o que falta. Às vezes ele não quer {draw:xdesc}{neg}desconto, quer {draw:seg}{point:seg}segurança pra comprar.",
    "{walk:480}Exemplo: o cliente {draw:b1}{look:b1}pede dez por cento numa jaqueta. A vendedora diz: {draw:b2}{present}consigo, se levar a calça junto. Ele {draw:duas}{wide}leva as duas.",
    "{walk:540}Uma regra: se você der desconto, {draw:uma}{serious}{count1}dê uma vez só, e {draw:motivo}{point:motivo}diga o motivo.",
    "{walk:420}Nesta semana, {draw:ck1}{point:ck1!}antes de dar qualquer desconto, {draw:ck2}{point:ck2!}peça algo em troca.",
    "{walk:540}Por hoje é só. {draw:follow}{wave}Segue o canal pra uma lição de venda nova todo dia.",
]
ITEMS = {
    'tag': ('icon', 'tag', 540, 540, 1.5, '-10%'), 'nox': ('x', 540, 540, 150),
    'again': ('t', 540, 850, 'sem troca = ele pede de novo', 54, RED),
    'ok1': ('t', 540, 480, 'desconto COM motivo', 58, GREEN),
    'nomot': ('strike', 540, 640, 'desconto sem motivo', 58), 'falso': ('stamp', 540, 830, 'PREÇO FALSO?', -0.08),
    'c1': ('check', 430, 'Levou mais'), 'c2': ('check', 560, 'Pagou à vista'), 'c3': ('check', 690, 'Fechou hoje'),
    'gift': ('icon', 'gift', 300, 560, 1.2, 'brinde'), 'truck': ('icon', 'truck', 770, 570, 1.2, 'frete grátis'),
    'vale': ('bar', 900, 'CUSTA MENOS, VALE MAIS', 60),
    'falta': ('bub', 140, 400, 940, 530, 'O que falta pra você fechar?', 'l', True),
    'xdesc': ('strike', 640, 720, 'desconto', 60), 'seg': ('bar', 880, 'ELE QUER SEGURANÇA', 62),
    'b1': ('bub', 110, 390, 640, 500, 'Faz 10% na jaqueta?', 'l', False, INK),
    'b2': ('bub', 360, 570, 970, 690, 'Consigo, se levar a calça!', 'r', False, MARK),
    'duas': ('stamp', 540, 860, 'LEVOU AS DUAS', -0.08, GREEN),
    'uma': ('big', 520, 'DESCONTO? 1 VEZ SÓ', RED), 'motivo': ('t', 540, 720, '+ diga o motivo', 64, INK),
    'ck1': ('check', 450, 'Antes de dar desconto...'), 'ck2': ('check', 610, 'peça algo em troca'),
    'follow': ('follow',),
}

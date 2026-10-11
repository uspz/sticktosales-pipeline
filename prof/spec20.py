from board import RED, GREEN, MARK, INK
HOOK = 'Explica o que você vende em *10* *segundos*'
CUT_HOOKS = {'dicas': 'A fórmula pra explicar seu produto em *10* *segundos*', 'exemplo': 'Não diga "eu faço sites". *Diga* *isso*'}
CAP = {'aula': ('Explica o que você vende em 10 segundos', 'a fórmula do pitch rápido ⏱️ Comenta sua frase 👇'),
       'dicas': ('A fórmula pra explicar seu produto em 10 segundos', 'pra quem, problema e resultado 🎯 Aula completa no perfil'),
       'exemplo': ('Não diga eu faço sites. Diga isso', 'exemplo de pitch que vende 💡 Qual é a sua frase? 👇')}
HT = '#pitch #comunicacao #empreendedorismo'
TITLES = ['10 SEGUNDOS', 'CONFUSO NÃO COMPRA', 'A FÓRMULA', 'A FÓRMULA', 'A FÓRMULA', 'EXEMPLO', 'UMA REGRA', 'NESTA SEMANA', 'POR HOJE É SÓ!']
GROUPS = [(2, 4)]
MARKED = [
    "{brow}Me explica o que você vende em {draw:sw}{point:sw}dez segundos. {draw:nc}{shrug}Não conseguiu? Então {draw:cli}{neg}o cliente também não entendeu.",
    "Se a sua {draw:scr}{point:scr}explicação é longa, o cliente se perde. {draw:conf}{neg}Cliente confuso não compra.",
    "Dica um: {draw:f1}{count1}diga pra quem é. {draw:g1}Eu ajudo donos de loja pequena...",
    "Dica dois: {draw:f2}{count2}diga o problema. {draw:g2}...que perdem vendas no Instagram...",
    "Dica três: {draw:f3}{count3}diga o resultado. {draw:g3}{present_hi}...a vender todo dia pelo direct.",
    "{walk:480}Exemplo: em vez de dizer {draw:sites}{neg}que você faz sites, diga: {draw:b1}{present}eu ajudo dentistas a lotar a agenda com um site que traz pacientes.",
    "{walk:540}Uma regra: fale do {draw:res}{serious}resultado do cliente, {draw:proc}{neg}não do seu processo.",
    "{walk:420}Nesta semana, {draw:ck1}{point:ck1!}escreva sua frase de dez segundos e {draw:ck2}{point:ck2!}use em toda apresentação.",
    "{walk:540}Por hoje é só. {draw:follow}{wave}Segue o canal pra uma lição de venda nova todo dia.",
]
ITEMS = {
    'sw': ('icon', 'stopwatch', 540, 520, 1.2, '0:10', MARK, 700, 64), 'nc': ('t', 540, 810, 'não conseguiu?', 60, RED),
    'cli': ('t', 540, 905, 'o cliente também não entendeu', 50, INK),
    'scr': ('icon', 'scribble', 540, 520, 1.6), 'conf': ('bar', 820, 'CONFUSO NÃO COMPRA', 66, RED),
    'f1': ('t', 120, 460, '1. PRA QUEM', 56, MARK, 'P', 'l'), 'g1': ('t', 140, 535, '"Eu ajudo donos de loja pequena..."', 46, INK, 'C', 'l'),
    'f2': ('t', 120, 650, '2. O PROBLEMA', 56, MARK, 'P', 'l'), 'g2': ('t', 140, 725, '"...que perdem vendas no Instagram..."', 46, INK, 'C', 'l'),
    'f3': ('t', 120, 840, '3. O RESULTADO', 56, MARK, 'P', 'l'), 'g3': ('t', 140, 915, '"...a vender todo dia pelo direct."', 46, GREEN, 'C', 'l'),
    'sites': ('strike', 540, 460, '"Eu faço sites."', 62),
    'b1': ('bub', 110, 570, 970, 790, 'Eu ajudo dentistas a lotar a agenda\ncom um site que traz pacientes.', 'l', False, MARK, 46),
    'res': ('big', 520, 'O RESULTADO DO CLIENTE', GREEN), 'proc': ('strike', 540, 700, 'o seu processo', 58),
    'ck1': ('check', 450, 'Escreva sua frase de 10s'), 'ck2': ('check', 610, 'Use em toda apresentação'),
    'follow': ('follow',),
}

from board import RED, GREEN, MARK, INK, ORANGE
HOOK = 'Quem *lê* *o* *cliente* vende mais'
CUT_HOOKS = {'dicas': 'Os *3* *tipos* de cliente (e como vender pra cada um)', 'exemplo': 'Ela perguntou 3 vezes se servia. *Veja* *o* *que* *ele* *fez*'}
CAP = {'aula': ('Quem lê o cliente vende mais', 'os 3 tipos de cliente e como falar com cada um 👀 Qual você mais atende? 👇'),
       'dicas': ('Os 3 tipos de cliente e como vender pra cada um', 'apressado, detalhista e inseguro 🎯 Aula completa no perfil'),
       'exemplo': ('Como vender pro cliente inseguro', 'exemplo real 👗 Você já perdeu venda por insegurança do cliente? 👇')}
HT = '#perfildecliente #atendimento #vendasonline'
TITLES = ['LEIA O CLIENTE', 'O ERRO', '1: O APRESSADO', '2: O DETALHISTA', '3: O INSEGURO', 'EXEMPLO', 'UMA REGRA', 'NESTA SEMANA', 'POR HOJE É SÓ!']
MARKED = [
    "{brow}Quem {draw:eye}{point:eye}lê o cliente vende *mais. Existem {draw:tres}{count3}três tipos de cliente, e cada um compra de um jeito.",
    "Se você fala {draw:igual}{neg}igual com todo mundo, você só vende pra {draw:clone}{point:clone}quem é parecido com você.",
    "Dica um: o {draw:clock}{point:clock}apressado. Vá direto ao ponto: {draw:p1}{count1}preço, {draw:p2}{count2}prazo e {draw:p3}{count3}pronto. {draw:longa}{neg}Explicação longa faz ele ir embora.",
    "Dica dois: o detalhista. Ele quer {draw:chart}{point:chart}números e comparação. Mande a {draw:doc}{point:doc}ficha técnica {draw:antes}antes que ele peça.",
    "{walk:610}Dica três: o inseguro. Ele tem {draw:medo}medo de errar. Mostre {draw:stars}{point:stars}avaliações e ofereça {draw:shield}{point:shield}garantia.",
    "{walk:480}Exemplo: a cliente {draw:b1}{look:b1}pergunta {draw:x3}três vezes se o tamanho serve. {draw:inseg}{shrug}Insegura. O vendedor manda {draw:fotos}{point:fotos}fotos de clientes com o mesmo tamanho, e ela {draw:fechou}{wide}fecha.",
    "{walk:540}Uma regra: fale no {draw:ritmo}{serious}ritmo do cliente, {draw:seu}{neg}não no seu.",
    "{walk:420}Nesta semana, {draw:ck1}{point:ck1!}antes de responder, pergunte a si mesmo: {draw:qual}{present}qual desses três é ele?",
    "{walk:540}Por hoje é só. {draw:follow}{wave}Segue o canal pra uma lição de venda nova todo dia.",
]
ITEMS = {
    'eye': ('icon', 'eye', 540, 520, 1.3), 'tres': ('icon', 'people', 540, 760, 1.0, '3 TIPOS', MARK, 890, 56),
    'igual': ('strike', 540, 520, 'a mesma conversa pra todos', 54),
    'clone': ('t', 540, 740, 'só vende pra quem é igual a você', 52, RED),
    'clock': ('icon', 'clock', 280, 560, 1.1, 'apressado'),
    'p1': ('t', 720, 470, 'preço', 62, GREEN, 'P'), 'p2': ('t', 720, 580, 'prazo', 62, GREEN, 'P'), 'p3': ('t', 720, 690, 'pronto', 62, GREEN, 'P'),
    'longa': ('strike', 540, 880, 'explicação longa', 56),
    'chart': ('icon', 'chart', 290, 570, 1.1, 'números'), 'doc': ('icon', 'doc', 770, 570, 1.0, 'ficha técnica'),
    'antes': ('bar', 900, 'ANTES QUE ELE PEÇA', 60),
    'stars': ('icon', 'stars', 300, 520, 0.9, 'avaliações', ORANGE, 610), 'shield': ('icon', 'shield', 780, 540, 1.0, 'garantia', MARK, 700),
    'medo': ('t', 540, 860, 'medo de errar', 60, RED),
    'b1': ('bub', 110, 390, 680, 500, 'O tamanho M serve mesmo?', 'l', True, INK),
    'x3': ('t', 830, 470, 'x3', 90, RED, 'P'), 'inseg': ('stamp', 800, 610, 'INSEGURA', -0.1),
    'fotos': ('icon', 'photos', 560, 770, 1.0), 'fechou': ('stamp', 560, 920, 'FECHOU!', -0.06, GREEN),
    'ritmo': ('big', 540, 'NO RITMO DO CLIENTE', GREEN), 'seu': ('strike', 540, 730, 'no seu ritmo', 58),
    'ck1': ('check', 430, 'Antes de responder...'),
    'qual': ('t', 540, 680, 'apressado · detalhista · inseguro', 50, MARK, 'P'),
    'follow': ('follow',),
}

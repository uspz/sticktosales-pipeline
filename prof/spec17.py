from board import RED, GREEN, MARK, INK
HOOK = 'Ele veio comprar 1 coisa e *saiu* *com* *3*'
CUT_HOOKS = {'dicas': 'Como fazer o cliente *levar* *mais* (sem ser chato)', 'exemplo': 'Uma frase que fez ela levar *mais* *um*'}
CAP = {'aula': ('Como fazer o cliente levar mais', 'venda adicional sem ser chato 🛍️ Salva pra usar no balcão'),
       'dicas': ('Como fazer o cliente levar mais sem ser chato', '3 dicas de venda adicional ➕ Aula completa no perfil'),
       'exemplo': ('Uma frase que fez a cliente levar mais um', 'exemplo real de venda adicional 👟 Você oferece complemento? 👇')}
HT = '#vendaadicional #ticketmedio #vendasonline'
TITLES = ['1 VIROU 3', 'O MELHOR MOMENTO', 'DICA 1: O QUE COMPLETA', 'DICA 2: COMBO', 'DICA 3: SÓ UMA COISA',
          'EXEMPLO', 'UMA REGRA', 'NESTA SEMANA', 'POR HOJE É SÓ!']
MARKED = [
    "{brow}O cliente veio comprar {draw:bag1}{point:bag1}uma coisa e saiu com {draw:bag3}{count3}três. E ainda {draw:thanks}{smile:1}agradeceu. Isso é {draw:va}{present_hi}venda adicional.",
    "Quem {draw:dec}{point:dec}já decidiu comprar está aberto a ouvir. É o {draw:facil}{present}momento mais fácil de vender de novo.",
    "Dica um: ofereça o que completa. Quem compra {draw:cel}{point:cel}celular precisa de {draw:capa}{count1}capinha e {draw:pel}{count2}película.",
    "Dica dois: monte um {draw:combo}{point:combo}combo com vantagem. Os dois juntos {draw:conta}{present_hi}saem mais em conta que separados.",
    "{walk:610}Dica três: ofereça {draw:um}{count1}só uma coisa. Se você oferecer {draw:dez}{point:dez}dez, ele {draw:nenhuma}{neg}não leva nenhuma.",
    "{walk:480}Exemplo: a cliente compra um {draw:shoe}{point:shoe}tênis branco. O vendedor diz: {draw:fala}{present}quem leva esse costuma levar o {draw:limp}{point:limp}limpador, pra ele continuar branco. Ela {draw:leva}{wide}leva.",
    "{walk:540}Uma regra: {draw:ajuda}{serious}só ofereça o que ajuda o cliente. {draw:empurra}{neg}Empurrar qualquer coisa {draw:queima}queima a confiança.",
    "{walk:420}Nesta semana, {draw:ck1}{point:ck1!}escolha um complemento pro seu produto mais vendido e {draw:ck2}{point:ck2!}ofereça em toda venda.",
    "{walk:540}Por hoje é só. {draw:follow}{wave}Segue o canal pra uma lição de venda nova todo dia.",
]
ITEMS = {
    'bag1': ('icon', 'bag', 280, 560, 1.0, 'veio por 1'), 'bag3': ('icon', 'boxes', 760, 560, 1.0, 'saiu com 3', MARK, 700),
    'thanks': ('t', 760, 450, 'obrigado!', 50, GREEN), 'va': ('bar', 880, 'VENDA ADICIONAL', 70),
    'dec': ('t', 540, 520, 'cliente que já decidiu comprar', 56, INK), 'facil': ('bar', 740, 'MOMENTO MAIS FÁCIL', 66, GREEN),
    'cel': ('icon', 'phone', 280, 600, 1.3, 'celular', MARK, 810),
    'capa': ('t', 730, 520, '+ capinha', 64, GREEN, 'P'), 'pel': ('t', 730, 680, '+ película', 64, GREEN, 'P'),
    'combo': ('icon', 'gift', 540, 560, 1.2, 'COMBO', MARK, 720, 60), 'conta': ('bar', 880, 'JUNTOS SAEM MAIS EM CONTA', 56, GREEN),
    'um': ('t', 290, 640, '1', 200, GREEN, 'P'), 'dez': ('icon', 'boxes', 760, 590, 1.2),
    'nenhuma': ('x', 760, 590, 150),
    'shoe': ('icon', 'shoe', 760, 470, 0.9, 'tênis branco', MARK, 610),
    'fala': ('bub', 110, 620, 970, 790, 'Quem leva esse costuma levar\no limpador, pra continuar branco', 'l', False, MARK, 44),
    'limp': ('icon', 'bottle', 270, 470, 0.7), 'leva': ('stamp', 560, 905, '+1 VENDA', -0.06, GREEN),
    'ajuda': ('big', 500, 'SÓ O QUE AJUDA', GREEN), 'empurra': ('strike', 540, 680, 'empurrar qualquer coisa', 56),
    'queima': ('stamp', 540, 850, 'CONFIANÇA PERDIDA', -0.06),
    'ck1': ('check', 450, 'Escolha 1 complemento'), 'ck2': ('check', 610, 'Ofereça em toda venda'),
    'follow': ('follow',),
}

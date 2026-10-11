from board import RED, GREEN, MARK, INK
HOOK = 'Vende por 100, comprou por 50. *Lucra* *50?*'
CUT_HOOKS = {'dicas': 'Você *acha* que lucra. Mas *não* lucra', 'exemplo': 'Ela achava que lucrava R$~10. *Era* *R$~2*'}
CAP = {'aula': ('Você acha que lucra, mas não lucra', 'como calcular o lucro de verdade 🧮 Salva pra refazer suas contas'),
       'dicas': ('Os custos escondidos que comem seu lucro', 'taxa, frete, embalagem e anúncio 📦 Aula completa no perfil'),
       'exemplo': ('Ela achava que lucrava R$ 10. Era R$ 2', 'exemplo real de precificação 📱 Você já fez essa conta? 👇')}
HT = '#precificacao #lucro #vendasonline'
TITLES = ['LUCRA METADE?', 'FATURAR NÃO É LUCRAR', 'DICA 1: CUSTOS ESCONDIDOS', 'DICA 2: A CONTA CERTA', 'DICA 3: NÃO COPIE',
          'EXEMPLO', 'UMA REGRA', 'NESTA SEMANA', 'POR HOJE É SÓ!']
MARKED = [
    "{brow}Você vende por {draw:t100}{point:t100}cem o que comprou por {draw:t50}{point:t50}cinquenta e acha que {draw:metade}lucra metade? {draw:nao}{neg}Provavelmente não.",
    "{draw:fat}Faturar não é lucrar. Lucro é o que sobra depois de {draw:custos}{point:custos}todos os {draw:lucro}custos.",
    "Dica um: some os custos escondidos. {draw:card}{count1}Taxa da maquininha, {draw:truck}{count2}frete, {draw:box}{count3}embalagem e o {draw:ad}anúncio entram no preço.",
    "Dica dois: calcule a margem, não só o dobro. Comprou por {draw:l2}cinquenta, custos de {draw:l3}vinte, vendeu por {draw:l1}cem: {draw:l4}{present_hi}sobram trinta.",
    "{walk:610}Dica três: {draw:copy}{neg}não copie o preço do concorrente. Ele pode estar {draw:prej}{point:prej}perdendo dinheiro sem saber.",
    "{walk:480}Exemplo: uma loja vendia {draw:capa}{point:capa}capinha a vinte reais achando que {draw:l10}lucrava dez. Com frete e taxa, {draw:dois}{neg}sobravam dois. {draw:up}{present_hi}Subiu pra vinte e cinco e continuou vendendo.",
    "{walk:540}Uma regra: {draw:sem}preço baixo sem lucro é só {draw:gratis}{serious}trabalho de graça.",
    "{walk:420}Nesta semana, {draw:ck1}{point:ck1!}refaça a conta de um produto {draw:ck2}{point:ck2!}com todos os custos.",
    "{walk:540}Por hoje é só. {draw:follow}{wave}Segue o canal pra uma lição de venda nova todo dia.",
]
ITEMS = {
    't100': ('icon', 'tag', 770, 520, 1.2, 'R$ 100'), 't50': ('icon', 'tag', 300, 520, 1.2, 'R$ 50'),
    'metade': ('t', 540, 740, 'lucro de R$ 50?', 66, INK, 'P'), 'nao': ('stamp', 540, 880, 'PROVAVELMENTE NÃO', -0.06),
    'fat': ('t', 540, 470, 'faturamento', 64, INK, 'P'), 'custos': ('t', 540, 590, '− todos os custos', 60, RED, 'P'),
    'lucro': ('bar', 790, '= LUCRO', 72, GREEN),
    'card': ('icon', 'card', 290, 510, 0.8, 'taxa', MARK, 640), 'truck': ('icon', 'truck', 780, 510, 0.9, 'frete', MARK, 640),
    'box': ('icon', 'box', 290, 770, 0.8, 'embalagem', MARK, 900), 'ad': ('icon', 'ad', 780, 770, 0.9, 'anúncio', MARK, 900),
    'l1': ('t', 540, 450, 'vendeu:  100', 62, INK, 'P'), 'l2': ('t', 540, 560, 'comprou:  − 50', 62, RED, 'P'),
    'l3': ('t', 540, 670, 'custos:  − 20', 62, RED, 'P'), 'l4': ('bar', 830, 'SOBRAM 30', 80, GREEN),
    'copy': ('icon', 'tag', 540, 520, 1.3, 'R$ 20'), 'prej': ('t', 540, 800, 'ele pode estar no prejuízo', 58, RED),
    'capa': ('icon', 'phone', 270, 600, 1.2, 'R$ 20', MARK, 800),
    'l10': ('strike', 720, 480, 'lucro: R$ 10', 56), 'dois': ('t', 720, 600, 'real: R$ 2', 64, RED, 'P'),
    'up': ('bar', 880, 'SUBIU PRA R$ 25 E VENDEU', 56, GREEN),
    'sem': ('big', 520, 'PREÇO SEM LUCRO =', RED), 'gratis': ('stamp', 540, 730, 'TRABALHO DE GRAÇA', -0.06),
    'ck1': ('check', 450, 'Refaça a conta'), 'ck2': ('check', 610, 'Com todos os custos'),
    'follow': ('follow',),
}

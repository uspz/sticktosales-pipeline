from board import RED, GREEN, MARK, INK, ORANGE
HOOK = 'Seu *melhor* *vendedor* já comprou de você'
CUT_HOOKS = {'dicas': '3 jeitos de fazer o cliente *voltar* *e* *indicar*', 'exemplo': 'Uma mensagem que virou *3* *clientes* *novos*'}
CAP = {'aula': ('Seu melhor vendedor já comprou de você', 'pós-venda que traz indicação 🔁 Salva e manda pra quem vende'),
       'dicas': ('Como fazer o cliente voltar e indicar', '3 dicas de pós-venda 💌 Aula completa no perfil'),
       'exemplo': ('Uma mensagem que virou 3 clientes novos', 'exemplo real de pós-venda 🎂 Você manda mensagem depois da entrega? 👇')}
HT = '#posvenda #fidelizacao #vendasonline'
TITLES = ['SEU MELHOR VENDEDOR', 'MAIS BARATO', 'DICA 1: DEPOIS DA ENTREGA', 'DICA 2: NA HORA DA ALEGRIA', 'DICA 3: MOTIVO PRA VOLTAR',
          'EXEMPLO', 'UMA REGRA', 'NESTA SEMANA', 'POR HOJE É SÓ!']
MARKED = [
    "{brow}O {draw:fig}{point:fig}cliente que já comprou de você é o seu melhor vendedor. E {draw:ning}{neg}quase ninguém usa ele.",
    "Vender pra {draw:c1}{point:c1}quem já {draw:l1}confia em você é muito mais {draw:bar}barato do que conquistar {draw:c2}{point:c2}alguém novo.",
    "Dica um: mande mensagem {draw:box}{point:box}depois da entrega. {draw:b1}{present}Pergunte se deu tudo certo. {draw:quase}Quase ninguém faz isso.",
    "Dica dois: peça indicação na hora da alegria, {draw:b2}{look:b2}quando ele elogiar o produto, {draw:b3}{present}não meses depois.",
    "{walk:610}Dica três: dê um motivo pra voltar. Um {draw:cupom}{point:cupom}cupom pra próxima compra {draw:volta}traz ele de volta.",
    "{walk:480}Exemplo: uma {draw:cake}{point:cake}confeiteira manda mensagem no dia seguinte: {draw:b4}{present}o bolo agradou? A cliente responde com {draw:fotos}{point:fotos}fotos da festa, e {draw:tres}{count3}indica pra três amigas.",
    "{walk:540}Uma regra: {draw:cont}{serious}a venda não termina {draw:pag}{neg}no pagamento.",
    "{walk:420}Nesta semana, {draw:ck1}{point:ck1!}mande mensagem pra cinco clientes antigos {draw:ck2}{point:ck2!}perguntando como foi a experiência.",
    "{walk:540}Por hoje é só. {draw:follow}{wave}Segue o canal pra uma lição de venda nova todo dia.",
]
ITEMS = {
    'fig': ('icon', 'fig', 540, 540, 1.3, 'quem já comprou', MARK, 760), 'ning': ('t', 540, 880, 'quase ninguém usa', 56, RED),
    'c1': ('icon', 'coin', 290, 540, 1.0, 'R$', ORANGE), 'l1': ('t', 290, 700, 'quem já confia', 50, GREEN), 'bar': ('bar', 880, 'MUITO MAIS BARATO', 62, GREEN),
    'c2': ('icon', 'boxes', 770, 540, 1.0, 'alguém novo', MARK, 700, 50),
    'box': ('icon', 'box', 270, 560, 1.0, 'entregue', MARK, 730),
    'b1': ('bub', 470, 430, 960, 560, 'Deu tudo certo?', 'r', False, MARK, 52), 'quase': ('t', 540, 880, 'quase ninguém faz isso', 54, RED),
    'b2': ('bub', 120, 400, 560, 510, 'Amei!', 'l', False, INK, 56),
    'b3': ('bub', 400, 590, 960, 710, 'Indica pra um amigo?', 'r', False, MARK, 50),
    'cupom': ('icon', 'tag', 420, 560, 1.4, 'CUPOM'), 'volta': ('icon', 'return', 800, 560, 1.2, 'volta', GREEN, 700),
    'cake': ('icon', 'cake', 260, 520, 1.0), 'b4': ('bub', 470, 420, 960, 540, 'O bolo agradou?', 'r', False, MARK, 50),
    'fotos': ('icon', 'photos', 540, 730, 1.0), 'tres': ('bar', 910, '+3 INDICAÇÕES', 60, GREEN),
    'cont': ('big', 520, 'A VENDA CONTINUA', GREEN), 'pag': ('strike', 540, 700, 'termina no pagamento', 56),
    'ck1': ('check', 450, '5 clientes antigos'), 'ck2': ('check', 610, 'Como foi a experiência?'),
    'follow': ('follow',),
}

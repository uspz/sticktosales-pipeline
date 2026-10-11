from board import RED, GREEN, MARK, INK
HOOK = '*3* *erros* no WhatsApp que fazem o cliente *sumir*'
CUT_HOOKS = {'dicas': 'Você comete o *erro* *2*? Quase todo mundo comete', 'exemplo': 'Nunca responda *só* *o* *preço* no WhatsApp'}
CAP = {'aula': ('3 erros no WhatsApp que fazem o cliente sumir', 'o segundo quase todo mundo comete 📱 Salva e revisa suas conversas'),
       'dicas': ('Erros no WhatsApp que matam sua venda', 'demora, preço seco e áudio longo ⏱️ Aula completa no perfil'),
       'exemplo': ('Nunca responda só o preço no WhatsApp', 'exemplo de resposta que vende 💬 Como você responde preço? 👇')}
HT = '#whatsapp #vendaspelowhatsapp #vendasonline'
TITLES = ['3 ERROS NO WHATSAPP', 'A DISPUTA', 'ERRO 1: DEMORAR', 'ERRO 2: SÓ O PREÇO', 'ERRO 3: ÁUDIO LONGO',
          'EXEMPLO', 'UMA REGRA', 'NESTA SEMANA', 'POR HOJE É SÓ!']
MARKED = [
    "{brow}Três erros no {draw:phone}{point:phone}WhatsApp que fazem o cliente {draw:some}sumir. O {draw:dois}{count2}segundo quase todo mundo comete.",
    "No WhatsApp o cliente fala com {draw:vend}{point:vend}vários vendedores ao mesmo tempo. {draw:melhor}{present}Quem responde melhor leva.",
    "Erro um: {draw:clock}{point:clock}demorar pra responder. Quem responde primeiro sai na frente. Responda em {draw:min}{point:min}minutos, {draw:horas}{neg}não em horas.",
    "Erro dois: mandar {draw:b1}{point:b1}só o preço. {draw:caro}Preço seco parece caro. Mande o valor junto: {draw:b2}{present}o que ele leva por esse preço.",
    "{walk:610}Erro três: {draw:audio}{point:audio}áudio de três minutos. {draw:xa}{neg}Ninguém escuta. Mande {draw:txt}texto curto ou {draw:a30}{point:a30}áudio de até trinta segundos.",
    "{walk:480}Exemplo: em vez de {draw:so}{neg}só oitenta reais, diga: {draw:b3}{present}oitenta reais, com frete grátis e troca em sete dias. Quer que eu separe o seu?",
    "{walk:540}Uma regra: {draw:tm}toda mensagem termina com uma {draw:q}{present_hi}pergunta.",
    "{walk:420}Nesta semana, {draw:ck1}{point:ck1!}revise suas últimas dez conversas e {draw:ck2}{point:ck2!}veja qual desses erros você cometeu.",
    "{walk:540}Por hoje é só. {draw:follow}{wave}Segue o canal pra uma lição de venda nova todo dia.",
]
ITEMS = {
    'phone': ('icon', 'phone', 540, 530, 1.1), 'some': ('t', 540, 790, 'e o cliente some...', 56, RED),
    'dois': ('t', 540, 900, 'o nº 2 é o mais comum', 50, MARK, 'P'),
    'vend': ('icon', 'people', 540, 560, 1.2, 'vários vendedores'), 'melhor': ('bar', 880, 'QUEM RESPONDE MELHOR LEVA', 56),
    'clock': ('icon', 'clock', 280, 580, 1.1),
    'min': ('t', 730, 520, 'minutos', 66, GREEN, 'P'), 'horas': ('strike', 730, 660, 'horas', 64),
    'b1': ('bub', 130, 400, 520, 500, 'R$ 80.', 'l', False, INK), 'caro': ('stamp', 790, 450, 'PARECE CARO', -0.1),
    'b2': ('bub', 130, 610, 950, 760, 'R$ 80 + o que ele leva\npor esse preço', 'l', False, MARK, 50),
    'audio': ('icon', 'audio', 540, 460, 1.2), 'xa': ('t', 540, 600, '3:00  ninguém escuta', 56, RED),
    'txt': ('t', 330, 800, 'texto curto', 56, GREEN, 'P'), 'a30': ('t', 750, 800, 'áudio 0:30', 56, GREEN, 'P'),
    'so': ('strike', 540, 460, 'R$ 80.', 64),
    'b3': ('bub', 110, 560, 970, 820, 'R$ 80, com frete grátis\ne troca em 7 dias.\nQuer que eu separe o seu?', 'l', False, MARK, 50),
    'q': ('t', 540, 740, '?', 300, RED, 'P'), 'tm': ('t', 540, 900, 'toda mensagem termina com pergunta', 50, INK),
    'ck1': ('check', 450, 'Revise 10 conversas'), 'ck2': ('check', 610, 'Ache o seu erro'),
    'follow': ('follow',),
}

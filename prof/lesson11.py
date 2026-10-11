"""Licao 11 (Ancoragem de preco) no formato vertical com o professor de palito.
uso:
  python3 lesson11.py stills <EN|PT> <saida.png> <t1,t2,...> [align.json]
  python3 lesson11.py render <EN|PT> <align.json> <saida.mp4>
  python3 lesson11.py cover <EN|PT> <saida.png>
"""
import sys, json, math, subprocess, re
from cairoc import Canvas
from rig2 import draw_character, Pose, hand_params, skeleton, STAND_H
from perf import Perf, simulate, FPS, sstep, clamp, word_dur
import board as Bd
from board import INK, MARK, RED, YEL, GREEN, ORANGE

W, H = 1080, 1920
FLOOR_V = 1690.0
SC = 1.2
BX, BY, BW, BH = 50, 175, 980, 810
BG = '#F3EFE6'
LESSON = 11

TXT = {
    'EN': dict(
        titles=['THE WINE LIST', 'PRICE ANCHORING', 'TIP 1: PREMIUM FIRST', 'TIP 2: THREE OPTIONS', 'TIP 3: VALUE FIRST',
                'EXAMPLE', 'ONE RULE', 'THIS WEEK', "THAT'S IT!"],
        p1='£30', p2='£90', compare='compare', first='1st number', t1='£2,000', t1l='PREMIUM', t2='£800', note='feels small!',
        opts=[('BASIC', '£19'), ('PRO', '£49'), ('PREMIUM', '£99')], most='MOST PICKED',
        prob=('PROBLEM', '-£500/month'), price=('PRICE', '£200'), vp='value > price',
        c1=('FULL PROJECT', '£5,000'), c2=('STARTER', '£1,500'), stamp='BARGAIN!',
        real='REAL ANCHORS ONLY', fake1='WAS £999', fake2='NOW £99',
        ch1='Best option first', ch2='Value before price', follow='+ FOLLOW', every='a new lesson every day',
        chip='Stick To Sales · Lesson #11', cover=['PRICE', 'ANCHORING']),
    'PT': dict(
        titles=['CARTA DE VINHOS', 'ANCORAGEM DE PREÇO', 'DICA 1: A MAIS CARA PRIMEIRO', 'DICA 2: TRÊS OPÇÕES',
                'DICA 3: VALOR PRIMEIRO', 'EXEMPLO', 'UMA REGRA', 'NESTA SEMANA', 'POR HOJE É SÓ!'],
        p1='R$ 80', p2='R$ 250', compare='compara', first='1º número', t1='R$ 2.000', t1l='PREMIUM', t2='R$ 800', note='parece pouco!',
        opts=[('BÁSICO', 'R$ 19'), ('PRO', 'R$ 49'), ('PREMIUM', 'R$ 99')], most='A MAIS ESCOLHIDA',
        prob=('PROBLEMA', '-R$ 1.000/mês'), price=('PREÇO', 'R$ 300'), vp='valor > preço',
        c1=('PROJETO COMPLETO', 'R$ 5.000'), c2=('PACOTE INICIAL', 'R$ 1.500'), stamp='BARATO!',
        real='SÓ ÂNCORA REAL', fake1='DE R$ 999', fake2='POR R$ 99',
        ch1='Melhor opção primeiro', ch2='Valor antes do preço', follow='+ SEGUIR', every='lição nova todo dia',
        chip='Stick To Sales · Lição #11', cover=['ANCORAGEM', 'DE PREÇO']),
}

MARKED = {
    'EN': [
        "{brow}Why does a {draw:bottle1}{point:bottle1}thirty pound bottle of wine look cheap on a menu? Because the one "
        "{draw:bottle2}{point:bottle2}next to it costs *ninety. Your brain {neg}never judges a price {draw:compare}alone, it {small}*compares.",
        "That's {draw:anchor}{present_hi}price anchoring: the {draw:first}{count1}first number you see becomes the "
        "{draw:ruler}{point:ruler}ruler for everything else.",
        "Tip one: show your {draw:tag1}{point:tag1}*premium option first. After two thousand, {draw:tag2}{point:tag2}eight hundred "
        "{draw:note}feels {small}small.",
        "Tip two: offer {draw:three}{count3}three options. Most people pick the {draw:mid}{point:mid}*middle one.",
        "{walk:610}Tip three: anchor on {present}*value. Show what the {draw:problem}{point:problem!}problem costs them every month "
        "before you {draw:price}{point:price!}mention your price.",
        "{walk:480}Example: a designer shows a {draw:card1}{point:card1}five thousand pound project first. Suddenly, the "
        "{draw:card2}{point:card2}fifteen hundred pound package {draw:stamp}looks like a {wide}*bargain.",
        "{walk:540}One rule: the anchor must be {draw:real}{count1}*real. {draw:fake}{serious}{neg}Fake discounts destroy trust {calm}instantly.",
        "{walk:420}This week, show your {draw:check1}{point:check1!}best option first, and the {draw:check2}{point:check2!}value "
        "before the price.",
        "{walk:540}That's it for today. {draw:follow}{wave}Follow for a new sales lesson every day.",
    ],
    'PT': [
        "{brow}Por que um vinho de {draw:bottle1}{point:bottle1}80 reais parece barato no cardápio? Porque do lado tem um de "
        "{draw:bottle2}{point:bottle2}*250. Seu cérebro {neg}não julga preço {draw:compare}sozinho, ele {small}*compara.",
        "Isso é {draw:anchor}{present_hi}ancoragem de preço: o {draw:first}{count1}primeiro número vira a {draw:ruler}{point:ruler}régua pro resto.",
        "Dica um: mostre a opção {draw:tag1}{point:tag1}*mais cara primeiro. Depois de dois mil, {draw:tag2}{point:tag2}oitocentos "
        "{draw:note}parece {small}pouco.",
        "Dica dois: ofereça {draw:three}{count3}três opções. A maioria escolhe a do {draw:mid}{point:mid}*meio.",
        "{walk:610}Dica três: ancore no {present}*valor. Mostre quanto o {draw:problem}{point:problem!}problema custa por mês {draw:price}{point:price!}antes do "
        "seu preço.",
        "{walk:480}Exemplo: o designer mostra primeiro um projeto de {draw:card1}{point:card1}cinco mil. Aí o pacote de "
        "{draw:card2}{point:card2}mil e quinhentos {draw:stamp}parece {wide}*barato.",
        "{walk:540}Uma regra: a âncora tem que ser {draw:real}{count1}*real. {draw:fake}{serious}{neg}Desconto falso destrói a confiança "
        "na {calm}hora.",
        "{walk:420}Nesta semana, mostre sua {draw:check1}{point:check1!}melhor opção primeiro, e o {draw:check2}{point:check2!}valor "
        "antes do preço.",
        "{walk:540}Por hoje é só. {draw:follow}{wave}Segue o canal pra uma lição de venda nova todo dia.",
    ],
}

ANCHORS = {'bottle1': (330, 560), 'bottle2': (750, 560), 'compare': (545, 830), 'anchor': (540, 540), 'first': (185, 829),
           'ruler': (570, 829), 'tag1': (310, 535), 'tag2': (740, 580), 'note': (745, 710), 'three': (540, 600),
           'mid': (540, 600), 'problem': (305, 580), 'price': (775, 580), 'card1': (305, 565), 'card2': (775, 585),
           'stamp': (780, 790), 'real': (540, 455), 'fake': (540, 680), 'check1': (155, 485), 'check2': (155, 645),
           'follow': (540, 560)}
for i in range(9): ANCHORS[f'title{i}'] = (540, 270)
SLIDE_ITEMS = [['bottle1', 'bottle2', 'compare'], ['anchor', 'first', 'ruler'], ['tag1', 'tag2', 'note'], ['three', 'mid'],
               ['problem', 'price'], ['card1', 'card2', 'stamp'], ['real', 'fake'], ['check1', 'check2'], ['follow']]
DUR = {'bottle1': 0.9, 'bottle2': 0.9, 'compare': 0.6, 'anchor': 0.9, 'first': 0.5, 'ruler': 0.7, 'tag1': 0.8, 'tag2': 0.7,
       'note': 0.6, 'three': 1.1, 'mid': 0.6, 'problem': 0.8, 'price': 1.1, 'card1': 0.8, 'card2': 0.8, 'stamp': 0.45,
       'real': 0.7, 'fake': 1.2, 'check1': 0.8, 'check2': 0.8, 'follow': 0.9}


# ------------------------------------------------------------------ desenho dos itens
def draw_item(c, key, p, L):
    s = Bd.sub
    if key in ('bottle1', 'bottle2'):
        cx, top, h, sd = (330, 430, 320, 1) if key == 'bottle1' else (750, 405, 345, 4)
        Bd.draw_strokes(c, Bd.bottle(cx, top, h, sd), s(p, 0, 0.65), MARK, 6.5)
        if key == 'bottle2' and p > 0.5:
            Bd.draw_strokes(c, Bd.star(cx, top + h * 0.675, 24), s(p, 0.5, 0.75), ORANGE, 5)
        x0 = cx - 95
        Bd.draw_strokes(c, Bd.price_tag(x0, 795, x0 + 190, 870, sd), s(p, 0.45, 0.8), INK, 5)
        Bd.text(c, L['p1' if key == 'bottle1' else 'p2'], cx + 22, 853, 56, INK, s(p, 0.7, 1.0), maxw=138)
    elif key == 'compare':
        Bd.draw_strokes(c, Bd.double_arrow(452, 638, 832), s(p, 0, 0.6), RED, 6)
        Bd.text(c, L['compare'], 545, 930, 50, RED, s(p, 0.4, 1.0))
    elif key == 'anchor':
        Bd.draw_strokes(c, Bd.anchor_icon(540, 565, 150), p, MARK, 10)
    elif key == 'first':
        Bd.draw_strokes(c, [Bd.circle(185, 829, 36, n=26)], s(p, 0, 0.6), RED, 6)
        Bd.text(c, '1', 185, 848, 48, RED, s(p, 0.3, 0.7), family='Poppins')
        Bd.text(c, L['first'], 120, 765, 48, RED, s(p, 0.5, 1.0), align='l')
    elif key == 'ruler':
        Bd.draw_strokes(c, Bd.ruler(230, 925, 800), p, MARK, 5)
    elif key == 'tag1':
        Bd.text(c, L['t1l'], 310, 428, 44, ORANGE, s(p, 0, 0.35))
        Bd.draw_strokes(c, Bd.price_tag(100, 450, 520, 630, 2), s(p, 0.15, 0.7), MARK, 7)
        Bd.text(c, L['t1'], 335, 572, 92, INK, s(p, 0.55, 1.0), maxw=330)
    elif key == 'tag2':
        Bd.draw_strokes(c, Bd.price_tag(600, 520, 885, 640, 6), s(p, 0, 0.6), MARK, 6)
        Bd.text(c, L['t2'], 758, 605, 68, INK, s(p, 0.45, 1.0), maxw=220)
    elif key == 'note':
        Bd.draw_strokes(c, Bd.arrow(745, 700, 745, 652, 16), s(p, 0, 0.4), GREEN, 5)
        Bd.text(c, L['note'], 745, 765, 56, GREEN, s(p, 0.3, 1.0))
    elif key == 'three':
        boxes = [(90, 450, 340, 760), (395, 420, 685, 790), (740, 450, 990, 760)]
        for i, (x0, y0, x1, y1) in enumerate(boxes):
            q = s(p, i * 0.3, i * 0.3 + 0.4)
            Bd.draw_strokes(c, [Bd.rect(x0, y0, x1, y1, i)], s(q, 0, 0.6), MARK, 6)
            name, price = L['opts'][i]
            Bd.text(c, name, (x0 + x1) / 2, y0 + 82, 46, INK, s(q, 0.45, 0.8), maxw=x1 - x0 - 30)
            Bd.text(c, price, (x0 + x1) / 2, y0 + 215, 72, MARK, s(q, 0.6, 1.0), maxw=x1 - x0 - 30)
    elif key == 'mid':
        Bd.fill_rr(c, 398, 423, 682, 787, 10, YEL, 0.5 * s(p, 0, 0.4))
        name, price = L['opts'][1]
        if p > 0:
            Bd.text(c, name, 540, 502, 46, INK, 1.0, maxw=260); Bd.text(c, price, 540, 635, 72, MARK, 1.0, maxw=260)
        Bd.draw_strokes(c, [Bd.rect(395, 420, 685, 790, 9)], s(p, 0.1, 0.6), INK, 8)
        Bd.draw_strokes(c, Bd.star(540, 412, 30), s(p, 0.3, 0.6), ORANGE, 6)
        Bd.text(c, L['most'], 540, 868, 50, ORANGE, s(p, 0.5, 1.0))
    elif key == 'problem':
        Bd.draw_strokes(c, [Bd.rrect_pts(90, 460, 520, 700, 22)], s(p, 0, 0.5), RED, 6)
        Bd.text(c, L['prob'][0], 305, 548, 52, RED, s(p, 0.35, 0.7), maxw=390)
        Bd.text(c, L['prob'][1], 305, 645, 56, RED, s(p, 0.55, 1.0), maxw=390)
    elif key == 'price':
        Bd.draw_strokes(c, [Bd.rrect_pts(560, 460, 990, 700, 22)], s(p, 0, 0.35), MARK, 6)
        Bd.text(c, L['price'][0], 775, 548, 52, MARK, s(p, 0.25, 0.5), maxw=390)
        Bd.text(c, L['price'][1], 775, 655, 84, INK, s(p, 0.4, 0.65), maxw=390)
        Bd.text(c, L['vp'], 540, 835, 66, GREEN, s(p, 0.65, 1.0))
    elif key == 'card1':
        Bd.draw_strokes(c, [Bd.rect(90, 430, 520, 700, 3)], s(p, 0, 0.5), MARK, 6)
        Bd.text(c, L['c1'][0], 305, 512, 44, INK, s(p, 0.35, 0.7), maxw=390)
        Bd.text(c, L['c1'][1], 305, 640, 88, INK, s(p, 0.55, 1.0), maxw=390)
    elif key == 'card2':
        Bd.draw_strokes(c, [Bd.rect(560, 470, 990, 700, 5)], s(p, 0, 0.5), MARK, 6)
        Bd.text(c, L['c2'][0], 775, 548, 44, INK, s(p, 0.35, 0.7), maxw=390)
        Bd.text(c, L['c2'][1], 775, 662, 80, MARK, s(p, 0.55, 1.0), maxw=390)
    elif key == 'stamp':
        Bd.stamp(c, L['stamp'], 780, 795, -0.18, p)
    elif key == 'real':
        Bd.text(c, L['real'], 540, 482, 76, GREEN, s(p, 0, 0.75))
        Bd.draw_strokes(c, [Bd.wob([(170, 508), (910, 508)], 1.2, 2)], s(p, 0.6, 1.0), GREEN, 6)
    elif key == 'fake':
        Bd.draw_strokes(c, Bd.price_tag(200, 600, 880, 760, 8), s(p, 0, 0.35), INK, 6)
        Bd.text(c, L['fake1'], 440, 702, 48, '#777777', s(p, 0.2, 0.45), maxw=280)
        Bd.draw_strokes(c, [[(340, 686), (548, 686)]], s(p, 0.4, 0.5), '#777777', 5)
        Bd.text(c, L['fake2'], 715, 702, 56, RED, s(p, 0.45, 0.6), maxw=270)
        Bd.draw_strokes(c, Bd.big_x(540, 680, 210), s(p, 0.62, 1.0), RED, 13)
    elif key in ('check1', 'check2'):
        y = 450 if key == 'check1' else 610
        Bd.draw_strokes(c, [Bd.rect(118, y, 190, y + 70, 2)], s(p, 0, 0.35), INK, 6)
        Bd.text(c, L['ch1' if key == 'check1' else 'ch2'], 222, y + 57, 64, INK, s(p, 0.2, 0.7), align='l', maxw=780)
        Bd.draw_strokes(c, Bd.check_mark(156, y + 35, 70), s(p, 0.65, 1.0), GREEN, 10)
    elif key == 'follow':
        Bd.button(c, L['follow'], 540, 560, s(p, 0, 0.6))
        Bd.text(c, L['every'], 540, 775, 60, INK, s(p, 0.5, 1.0))


def draw_board(c, pf, t, blocks, L):
    c.save()
    c.color('#000000', 0.10); c.rrect(BX + 8, BY + 12, BW, BH, 22); c.fill()
    c.color('#FFFFFF'); c.rrect(BX, BY, BW, BH, 22); c.fill(True)
    c.color('#3A3A40'); c.lw(11); c.stroke()
    c.color('#3A3A40'); c.rrect(BX + 70, BY + BH + 7, BW - 140, 14, 6); c.fill()
    c.color(MARK); c.rrect(BX + 140, BY + BH - 3, 52, 11, 4); c.fill()
    c.color(RED); c.rrect(BX + 205, BY + BH - 3, 52, 11, 4); c.fill()
    c.restore()
    starts = [b[0] for b in blocks]
    for i in range(len(SLIDE_ITEMS)):
        a = 0.0 if i == 0 else starts[i] - 0.15
        b = starts[i + 1] - 0.15 if i + 1 < len(starts) else 1e9
        alpha = (1.0 if i == 0 else sstep((t - a) / 0.25)) * (1 - sstep((t - b) / 0.25))
        if alpha <= 0.001: continue
        c.push()
        Bd.text(c, L['titles'][i], 540, 298, 76, INK, sstep((t - a) / 0.5), maxw=900)
        for key in SLIDE_ITEMS[i]:
            if key in pf.board:
                draw_item(c, key, sstep((t - pf.board[key]) / DUR[key]), L)
        c.pop_paint(alpha)


# ------------------------------------------------------------------ cena
def draw_bg(c):
    c.clear(BG)
    c.linear(0, FLOOR_V, 0, FLOOR_V + 240, [(0, '#E7E0D2', 1.0), (1, '#DDD5C5', 1.0)])
    c.rect(-500, FLOOR_V, 2100, 600); c.fill()
    c.color('#CFC6B4'); c.lw(3); c.new_path(); c.move(-500, FLOOR_V + 1); c.line(1600, FLOOR_V + 1); c.stroke()


def draw_captions(c, pf, t):
    ch = None
    for i, chunk in enumerate(pf.chunks):
        a = chunk[0]['t0'] - 0.1
        b = chunk[-1]['t1'] + 0.25
        if i + 1 < len(pf.chunks): b = min(b, pf.chunks[i + 1][0]['t0'] - 0.1)
        if a <= t < b: ch = (chunk, a, b)
    if ch is None: return
    chunk, a, b = ch
    size = 68
    c.font('Poppins', size, True)
    spw = c.extents('a a').x_advance - c.extents('aa').x_advance + 16
    widths = [c.extents(wd['text']).x_advance + spw for wd in chunk]
    total = sum(widths) - spw
    if total > 900:
        size = size * 900 / total; c.font('Poppins', size, True)
        spw = c.extents('a a').x_advance - c.extents('aa').x_advance + 14
        widths = [c.extents(wd['text']).x_advance + spw for wd in chunk]; total = sum(widths) - spw
    k_in = sstep((t - a) / 0.14)
    y = 1592 + (1 - k_in) * 16
    x = W / 2 - total / 2
    for wd, wdt in zip(chunk, widths):
        active = wd['t0'] - 0.03 <= t < wd['t1'] + 0.05
        pop = 1.0
        if active:
            u = (t - wd['t0'] + 0.03) / 0.16
            pop = 1.0 + 0.15 * math.sin(math.pi * clamp(u, 0, 1)) if u < 1 else 1.0
        tw = c.extents(wd['text']).x_advance
        c.save(); c.translate(x + tw / 2, y - size * 0.35); c.scale(pop, pop); c.translate(-tw / 2, size * 0.35)
        c.text_path(0, 0, wd['text'])
        c.color('#000000', k_in); c.lw(13); c.stroke(True)
        c.color(YEL if active else '#FFFFFF', k_in); c.fill()
        c.restore()
        x += wdt


def cam_at(t, blocks):
    for b, (s, e) in enumerate(blocks):
        nxt = blocks[b + 1][0] if b + 1 < len(blocks) else e + 2
        if t < nxt or b == len(blocks) - 1:
            u = clamp((t - s) / max(0.5, nxt - s), 0, 1)
            z = 1.0 + 0.03 * u if b % 2 == 0 else 1.03 - 0.03 * u
            return 540, 1000, z
    return 540, 1000, 1.0


def render_frame(c, pf, poses, f, blocks, L, end):
    t = f / FPS
    cx, cy, z = cam_at(t, blocks)
    c.save(); c.translate(W / 2, H / 2 + 40); c.scale(z, z); c.translate(-cx, -cy)
    draw_bg(c)
    draw_board(c, pf, t, blocks, L)
    draw_character(c, poses[min(f, len(poses) - 1)])
    c.restore()
    c.radial(W / 2, H / 2, H * 0.45, H * 0.85, [(0, '#000000', 0.0), (1, '#000000', 0.10)])
    c.rect(0, 0, W, H); c.fill()
    draw_captions(c, pf, t)
    # barra de progresso
    c.color('#E0E0E0'); c.rect(0, 0, W, 12); c.fill()
    c.color('#000000'); c.rect(0, 0, W * clamp(t / end, 0, 1), 12); c.fill()


def synth_timing(lang):
    path = f'../script_v{LESSON}_{lang.lower()}.txt'
    blocks = [b.strip() for b in open(path, encoding='utf-8').read().strip().split('\n\n')]
    t = 0.35; words = []; sid = 0
    for bi, b in enumerate(blocks):
        for s in re.split(r'(?<=[.?!])\s+', b):
            for w in s.split():
                d = word_dur(w); words.append(dict(text=w, t0=round(t, 3), t1=round(t + d, 3), block=bi, sent=sid))
                t += d + 0.06
                if w[-1] in ',:;': t += 0.18
            t += 0.35; sid += 1
        t += 0.35
    bl = []
    for bi in range(len(blocks)):
        ws = [w for w in words if w['block'] == bi]; bl.append((ws[0]['t0'], ws[-1]['t1']))
    return dict(words=words, blocks=bl, end=round(t, 2), env=None, audio=None)


def build(lang, al):
    pf = Perf(x0=540.0, sc=SC, floor=FLOOR_V, chunk_chars=18)
    pf.anchors.update(ANCHORS)
    pf.env = al.get('env')
    for b in range(9):
        ws = [w for w in al['words'] if w['block'] == b]
        pf.say_timed(MARKED[lang][b], ws)
        t0 = ws[0]['t0']
        if b > 0:
            pf.looks.append((t0 - 0.1, ('item', f'title{b}')))
            pf.looks.append((t0 + 0.55, 'cam'))
    pf.looks.sort(key=lambda x: x[0])
    poses = simulate(pf, al['end'] + 0.2)
    return pf, poses


def main():
    mode, lang = sys.argv[1], sys.argv[2]
    L = TXT[lang]
    if mode == 'stills':
        out = sys.argv[3]; times = [float(x) for x in sys.argv[4].split(',')]
        al = json.load(open(sys.argv[5])) if len(sys.argv) > 5 else synth_timing(lang)
        pf, poses = build(lang, al)
        from PIL import Image
        c = Canvas(W, H); ims = []
        for tt in times:
            f = min(len(poses) - 1, int(tt * FPS))
            render_frame(c, pf, poses, f, al['blocks'], L, al['end'])
            ims.append(Image.fromarray(c.rgb()).resize((360, 640)))
        cols = min(5, len(ims)); rows = (len(ims) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * 364, rows * 644), 'gray')
        for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * 364, (i // cols) * 644))
        sheet.save(out)
    elif mode == 'render':
        al = json.load(open(sys.argv[3])); outp = sys.argv[4]
        pf, poses = build(lang, al)
        end = al['end']; N = int(end * FPS)
        ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr0', '-s', f'{W}x{H}',
                               '-r', str(FPS), '-i', '-', '-i', al['audio'], '-map', '0:v', '-map', '1:a',
                               '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
                               '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', '-shortest', outp],
                              stdin=subprocess.PIPE)
        c = Canvas(W, H)
        for f in range(N):
            render_frame(c, pf, poses, f, al['blocks'], L, end)
            ff.stdin.write(c.bgr0_bytes())
        ff.stdin.close(); ff.wait()
        print('ok', N, 'frames')


def cover(lang, out):
    L = TXT[lang]
    c = Canvas(W, H)
    c.save(); c.translate(W / 2, H / 2 + 40); c.scale(1.0, 1.0); c.translate(-540, -1000)
    draw_bg(c)
    c.color('#000000', 0.10); c.rrect(BX + 8, BY + 12, BW, BH, 22); c.fill()
    c.color('#FFFFFF'); c.rrect(BX, BY, BW, BH, 22); c.fill(True); c.color('#3A3A40'); c.lw(11); c.stroke()
    c.color('#3A3A40'); c.rrect(BX + 70, BY + BH + 7, BW - 140, 14, 6); c.fill()
    # selo do canal
    c.font('Poppins', 40, True); txt = L['chip']; w = c.extents(txt).x_advance
    c.color('#111111'); c.rrect(540 - w / 2 - 34, 228, w + 68, 74, 37); c.fill()
    c.color('#FFFFFF'); c.text(540 - w / 2, 278, txt)
    # titulo em caixa amarela
    c.color(YEL); c.rrect(95, 345, 890, 330, 26); c.fill(True); c.color('#111111'); c.lw(8); c.stroke()
    for i, line in enumerate(L['cover']):
        size = Bd.fit(c, line, 132, 800, 'Poppins')
        e = c.extents(line); c.color('#111111'); c.text(540 - e.x_advance / 2, 488 + i * 140, line)
    # etiquetas decorativas
    Bd.draw_strokes(c, Bd.price_tag(150, 745, 460, 870, 2), 1.0, MARK, 7)
    Bd.text(c, L['t1'], 332, 832, 70, INK, 1.0, maxw=225)
    Bd.draw_strokes(c, Bd.arrow(490, 808, 600, 808, 22), 1.0, RED, 7)
    Bd.draw_strokes(c, Bd.price_tag(625, 760, 900, 860, 6), 1.0, MARK, 6)
    Bd.text(c, L['t2'], 778, 832, 60, INK, 1.0, maxw=210)
    # professor apontando
    p = Pose(px=540, py=FLOOR_V - STAND_H * SC, sc=SC)
    p.fA = (540 - 28 * SC, FLOOR_V); p.fB = (540 + 28 * SC, FLOOR_V); p.toeA = math.pi - 0.16; p.toeB = 0.16
    S = skeleton(p)['S']
    p.wB = (S[0] + 95 * SC, S[1] - 150 * SC); p.handB = dict(hand_params('point'), ang=-1.3, scale=1.0, fore=1.0)
    p.wA = (S[0] - 100 * SC, S[1] + 50 * SC); p.handA = dict(hand_params('open'), ang=math.pi + 0.35, scale=1.0, fore=1.0)
    p.mouth_w, p.mouth_h, p.smile, p.brow_raise, p.eye_x, p.eye_y = 26, 18, 0.9, 0.8, 0.5, -0.8
    p.yaw = 0.15; p.pitch = -0.25
    draw_character(c, p)
    c.restore()
    from PIL import Image
    Image.fromarray(c.rgb()).save(out)


if __name__ == '__main__':
    if sys.argv[1] == 'cover':
        cover(sys.argv[2], sys.argv[3])
    else:
        main()

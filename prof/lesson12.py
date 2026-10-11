"""Licao 12 (Escassez e urgencia) no formato vertical com o professor de palito.
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
LESSON = 12

TXT = {
    'EN': dict(
        titles=['LIMITED DROP', 'NO DEADLINE', 'TIP 1: A REAL DEADLINE', "TIP 2: SHOW WHAT'S LIMITED", 'TIP 3: THE COST OF WAITING',
                'EXAMPLE', 'ONE RULE', 'THIS WEEK', "THAT'S IT!"],
        limited='LIMITED', lose='fear of losing it', scarce='SCARCITY', later="I'll buy later...", never='LATER = NEVER',
        month='OCTOBER', day='17', deadline='DEADLINE: FRIDAY', date='DATE', maybe='MAYBE',
        spots='10 spots', units='5 units', urgent='URGENCY', competitor='COMPETITOR', perm='every month',
        taken='12 taken', update='Only 8 left!', soldout='SOLD OUT', fake='NEVER FAKE IT', clock='00:59:59',
        ch1='One real deadline', ch2='Say when it ends', follow='+ FOLLOW', every='a new lesson every day',
        chip='Stick To Sales · Lesson #12', cover=['SCARCITY', '& URGENCY'], cstamp='ONLY 8 LEFT!'),
    'PT': dict(
        titles=['EDIÇÃO LIMITADA', 'SEM PRAZO', 'DICA 1: PRAZO REAL', 'DICA 2: MOSTRE O LIMITE', 'DICA 3: O CUSTO DE ESPERAR',
                'EXEMPLO', 'UMA REGRA', 'NESTA SEMANA', 'POR HOJE É SÓ!'],
        limited='LIMITADO', lose='medo de perder', scarce='ESCASSEZ', later='compro depois...', never='DEPOIS = NUNCA',
        month='OUTUBRO', day='17', deadline='PRAZO: SEXTA', date='DATA', maybe='TALVEZ',
        spots='10 vagas', units='5 unidades', urgent='URGÊNCIA', competitor='CONCORRENTE', perm='todo mês',
        taken='12 vendidas', update='Só 8 vagas!', soldout='ESGOTADO', fake='NUNCA FINJA', clock='00:59:59',
        ch1='Um prazo real', ch2='Diga quando acaba', follow='+ SEGUIR', every='lição nova todo dia',
        chip='Stick To Sales · Lição #12', cover=['ESCASSEZ', 'E URGÊNCIA'], cstamp='SÓ 8 VAGAS!'),
}

MARKED = {
    'EN': [
        "{brow}Why do people {draw:queue}{point:queue}queue for hours for a {draw:shoe}{point:shoe}limited sneaker drop? Because "
        "{chest}we want what we {draw:lose}might lose. {draw:scarce}{present_hi}That's *scarcity.",
        "Without a {neg}deadline, the customer {draw:later}{look:later}thinks: I'll buy later. And {draw:never}{point:never}later "
        "usually means *never.",
        "Tip one: give a {draw:calendar}{point:calendar}real *deadline. People {draw:dates}act on {count1}dates, not on maybe.",
        "Tip two: show what's limited. {draw:spots}{point:spots}Ten spots or {draw:units}{point:units}five {draw:urgent}units create *urgency.",
        "{walk:610}Tip three: show what they {draw:hourglass}{point:hourglass}lose by waiting. Every month without a website is "
        "{draw:clients}{point:clients!}clients going to your {wide}competitor.",
        "{walk:480}Example: a coach opens {draw:seats}{point:seats}twenty spots. When {draw:taken}{point:taken!}twelve are taken, she "
        "{draw:update}{present_hi}shares the update, and the {draw:soldout}{wide}rest sell in two days.",
        "{walk:540}One rule: {draw:fake}{serious}{neg}never fake it. A {draw:countdown}{point:countdown}countdown that resets every day "
        "kills your {calm}credibility.",
        "{walk:420}This week, add {draw:check1}{point:check1!}one real deadline to your offer, and {draw:check2}{point:check2!}tell "
        "people exactly when it ends.",
        "{walk:540}That's it for today. {draw:follow}{wave}Follow for a new sales lesson every day.",
    ],
    'PT': [
        "{brow}Por que tem gente que fica horas na {draw:queue}{point:queue}fila por um {draw:shoe}{point:shoe}tênis limitado? Porque "
        "{chest}a gente quer o que {draw:lose}pode perder. {draw:scarce}{present_hi}Isso é *escassez.",
        "Sem {neg}prazo, o cliente {draw:later}{look:later}pensa: compro depois. E {draw:never}{point:never}depois quase sempre vira *nunca.",
        "Dica um: dê um {draw:calendar}{point:calendar}prazo *real. As pessoas {draw:dates}agem por {count1}data, não por talvez.",
        "Dica dois: mostre o que é limitado. {draw:spots}{point:spots}Dez vagas ou {draw:units}{point:units}cinco "
        "{draw:urgent}unidades criam *urgência.",
        "{walk:610}Dica três: mostre o que ele {draw:hourglass}{point:hourglass}perde esperando. Cada mês sem site é "
        "{draw:clients}{point:clients!}cliente indo pro {wide}concorrente.",
        "{walk:480}Exemplo: uma mentora abre {draw:seats}{point:seats}vinte vagas. Quando {draw:taken}{point:taken!}doze acabam, ela "
        "{draw:update}{present_hi}avisa, e o {draw:soldout}{wide}resto vende em dois dias.",
        "{walk:540}Uma regra: {draw:fake}{serious}{neg}nunca finja. {draw:countdown}{point:countdown}Contagem regressiva que reinicia "
        "todo dia mata sua {calm}credibilidade.",
        "{walk:420}Nesta semana, coloque {draw:check1}{point:check1!}um prazo real na sua oferta, e {draw:check2}{point:check2!}diga "
        "exatamente quando acaba.",
        "{walk:540}Por hoje é só. {draw:follow}{wave}Segue o canal pra uma lição de venda nova todo dia.",
    ],
}

ANCHORS = {'queue': (270, 640), 'shoe': (760, 640), 'lose': (540, 790), 'scarce': (540, 880), 'later': (540, 520),
           'never': (540, 780), 'calendar': (540, 570), 'dates': (540, 880), 'spots': (290, 515), 'units': (770, 540),
           'urgent': (540, 840), 'hourglass': (300, 560), 'clients': (600, 560), 'seats': (330, 590), 'taken': (330, 590),
           'update': (795, 500), 'soldout': (790, 720), 'fake': (540, 450), 'countdown': (540, 670),
           'check1': (155, 485), 'check2': (155, 645), 'follow': (540, 560)}
for i in range(9): ANCHORS[f'title{i}'] = (540, 270)
SLIDE_ITEMS = [['queue', 'shoe', 'lose', 'scarce'], ['later', 'never'], ['calendar', 'dates'], ['spots', 'units', 'urgent'],
               ['hourglass', 'clients'], ['seats', 'taken', 'update', 'soldout'], ['fake', 'countdown'], ['check1', 'check2'],
               ['follow']]
DUR = {'queue': 1.0, 'shoe': 0.9, 'lose': 0.6, 'scarce': 0.6, 'later': 0.9, 'never': 0.7, 'calendar': 1.1, 'dates': 0.7,
       'spots': 0.9, 'units': 0.8, 'urgent': 0.5, 'hourglass': 0.9, 'clients': 1.1, 'seats': 0.9, 'taken': 0.9,
       'update': 0.7, 'soldout': 0.45, 'fake': 0.7, 'countdown': 1.3, 'check1': 0.8, 'check2': 0.8, 'follow': 0.9}


# ------------------------------------------------------------------ desenhos extras
def mini_fig(x, foot, s=1.0, walk=0.0):
    hy = foot - 120 * s
    out = [Bd.circle(x, hy, 15 * s, n=18), [(x, hy + 15 * s), (x, foot - 50 * s)],
           [(x, foot - 50 * s), (x - 18 * s + walk * 10, foot)], [(x, foot - 50 * s), (x + 18 * s - walk * 10, foot)],
           [(x - 22 * s, foot - 72 * s), (x, hy + 32 * s), (x + 22 * s, foot - 72 * s)]]
    return out


def cloud(cx, cy, w, h):
    pts = []
    n = 9
    for i in range(n):
        a0 = 2 * math.pi * i / n; a1 = 2 * math.pi * (i + 1) / n
        mx, my = cx + w / 2 * math.cos((a0 + a1) / 2), cy + h / 2 * math.sin((a0 + a1) / 2)
        r = 0.5 * math.hypot(w / 2 * (math.cos(a1) - math.cos(a0)), h / 2 * (math.sin(a1) - math.sin(a0))) * 0.95
        ang = math.atan2(my - cy, mx - cx)
        pts += Bd.circle(mx, my, r, ang - math.pi / 2, ang + math.pi / 2, 8)
    pts.append(pts[0])
    return [pts, Bd.circle(cx - w * 0.38, cy + h * 0.62, 14, n=14), Bd.circle(cx - w * 0.46, cy + h * 0.82, 8, n=12)]


def shoe():
    body = Bd.wob([(612, 702), (905, 702), (916, 682), (884, 656), (805, 640), (765, 600), (700, 574), (642, 584), (616, 640), (612, 702)], 1.0, 4)
    sole = [(612, 686), (912, 686)]
    laces = [[(722, 603), (744, 618)], [(742, 596), (764, 612)], [(762, 592), (784, 607)]]
    return [body, sole] + laces


def hourglass(cx, cy, h):
    w = h * 0.36
    t, b = cy - h / 2, cy + h / 2
    frame = [[(cx - w - 10, t), (cx + w + 10, t)], [(cx - w - 10, b), (cx + w + 10, b)]]
    glass = Bd.wob([(cx - w, t), (cx - w, t + h * 0.12), (cx - 8, cy - 6), (cx - 8, cy + 6), (cx - w, b - h * 0.12), (cx - w, b),
                    (cx + w, b), (cx + w, b - h * 0.12), (cx + 8, cy + 6), (cx + 8, cy - 6), (cx + w, t + h * 0.12), (cx + w, t),
                    (cx - w, t)], 0.8, 2)
    return frame + [glass]


def calendar(x0, y0, x1, y1):
    out = [Bd.rect(x0, y0, x1, y1, 3), [(x0, y0 + 70), (x1, y0 + 70)]]
    cw = (x1 - x0) / 5; rh = (y1 - y0 - 70) / 3
    for i in range(1, 5): out.append([(x0 + i * cw, y0 + 70), (x0 + i * cw, y1)])
    for j in range(1, 3): out.append([(x0, y0 + 70 + j * rh), (x1, y0 + 70 + j * rh)])
    out += [[(x0 + 70, y0 - 18), (x0 + 70, y0 + 18)], [(x1 - 70, y0 - 18), (x1 - 70, y0 + 18)]]
    return out


def cube(x0, y0, s):
    d = s * 0.35
    return [Bd.rect(x0, y0 + d, x0 + s, y0 + d + s, 7), [(x0, y0 + d), (x0 + d, y0), (x0 + s + d, y0), (x0 + s, y0 + d)],
            [(x0 + s + d, y0), (x0 + s + d, y0 + s), (x0 + s, y0 + d + s)]]


def reset_arrow(cx, cy, r):
    arc = Bd.circle(cx, cy, r, -0.3, 4.6, 26)
    e = arc[-1]; a = 4.6 + math.pi / 2
    head = [(e[0] + 16 * math.cos(a - 0.6), e[1] + 16 * math.sin(a - 0.6)), e, (e[0] + 16 * math.cos(a + 0.9), e[1] + 16 * math.sin(a + 0.9))]
    return [arc, head]


def bubble(x0, y0, x1, y1):
    return [Bd.wob(Bd.rrect_pts(x0, y0, x1, y1, 26) , 0.6, 1), [(x0 + 60, y1 - 2), (x0 + 30, y1 + 46), (x0 + 110, y1 - 2)]]


# ------------------------------------------------------------------ desenho dos itens
def draw_item(c, key, p, L):
    s = Bd.sub
    if key == 'queue':
        figs = []
        for i, x in enumerate((125, 200, 275, 350)): figs += mini_fig(x, 735, 1.0, (i % 2) * 0.6)
        Bd.draw_strokes(c, figs, s(p, 0, 0.75), MARK, 5)
        Bd.draw_strokes(c, [Bd.rect(405, 545, 505, 735, 1), Bd.circle(490, 640, 5, n=8)], s(p, 0.6, 1.0), INK, 5)
    elif key == 'shoe':
        Bd.draw_strokes(c, shoe(), s(p, 0, 0.7), MARK, 6)
        Bd.stamp(c, L['limited'], 760, 515, -0.12, s(p, 0.6, 1.0))
    elif key == 'lose':
        Bd.text(c, L['lose'], 540, 815, 54, RED, p)
    elif key == 'scarce':
        Bd.fill_rr(c, 290, 852, 790, 932, 14, YEL, 0.6 * s(p, 0, 0.4))
        Bd.text(c, L['scarce'], 540, 913, 72, INK, s(p, 0.2, 1.0), family='Poppins')
    elif key == 'later':
        Bd.draw_strokes(c, cloud(560, 520, 600, 210), s(p, 0, 0.6), INK, 5)
        Bd.text(c, L['later'], 560, 538, 58, MARK, s(p, 0.45, 1.0), maxw=520)
    elif key == 'never':
        Bd.text(c, L['never'], 540, 800, 84, RED, s(p, 0, 0.8), family='Poppins', maxw=860)
        Bd.draw_strokes(c, [Bd.wob([(170, 828), (910, 828)], 1.2, 3)], s(p, 0.7, 1.0), RED, 6)
    elif key == 'calendar':
        Bd.fill_rr(c, 300, 380, 780, 450, 6, RED, 0.85 * s(p, 0.25, 0.45))
        Bd.draw_strokes(c, calendar(300, 380, 780, 760), s(p, 0, 0.6), INK, 5)
        Bd.text(c, L['month'], 540, 432, 44, '#FFFFFF', s(p, 0.35, 0.55), family='Poppins')
        Bd.text(c, L['day'], 636, 640, 64, INK, s(p, 0.5, 0.7))
        Bd.draw_strokes(c, [Bd.circle(636, 620, 52, n=30)], s(p, 0.65, 0.85), RED, 7)
        Bd.text(c, L['deadline'], 540, 830, 58, RED, s(p, 0.75, 1.0))
    elif key == 'dates':
        Bd.text(c, L['date'], 330, 920, 62, GREEN, s(p, 0, 0.35), family='Poppins')
        Bd.draw_strokes(c, Bd.check_mark(440, 898, 56), s(p, 0.3, 0.5), GREEN, 9)
        Bd.text(c, L['maybe'], 690, 920, 62, RED, s(p, 0.5, 0.85), family='Poppins')
        Bd.draw_strokes(c, Bd.big_x(830, 898, 24), s(p, 0.8, 1.0), RED, 8)
    elif key == 'spots':
        sq = []
        for r in range(2):
            for k in range(5): sq.append(Bd.rect(110 + k * 74, 430 + r * 84, 168 + k * 74, 488 + r * 84, k + r))
        Bd.draw_strokes(c, sq, s(p, 0, 0.7), MARK, 5)
        Bd.text(c, L['spots'], 290, 680, 58, INK, s(p, 0.55, 1.0))
    elif key == 'units':
        Bd.draw_strokes(c, cube(640, 420, 190), s(p, 0, 0.6), MARK, 6)
        Bd.text(c, 'x5', 735, 555, 70, INK, s(p, 0.5, 0.75), family='Poppins')
        Bd.text(c, L['units'], 770, 740, 58, INK, s(p, 0.6, 1.0))
    elif key == 'urgent':
        Bd.text(c, L['urgent'], 540, 860, 84, RED, p, family='Poppins')
    elif key == 'hourglass':
        Bd.draw_strokes(c, hourglass(300, 575, 330), s(p, 0, 0.75), INK, 6)
        if p > 0.6:
            k = s(p, 0.6, 1.0)
            c.color(ORANGE, 0.85); c.new_path(); c.move(300 - 70 * (1 - k * 0.5), 470); c.line(300 + 70 * (1 - k * 0.5), 470); c.line(300, 560); c.close(); c.fill()
            c.new_path(); c.move(245, 728); c.line(355, 728); c.line(300, 728 - 60 * k); c.close(); c.fill()
        Bd.text(c, L['perm'], 300, 800, 50, RED, s(p, 0.7, 1.0))
    elif key == 'clients':
        figs = []
        for i, x in enumerate((520, 585, 650)): figs += mini_fig(x, 700, 0.85, (i % 2) * 0.7)
        Bd.draw_strokes(c, figs, s(p, 0, 0.45), MARK, 5)
        Bd.draw_strokes(c, Bd.arrow(520, 760, 760, 760, 22), s(p, 0.35, 0.55), RED, 6)
        Bd.draw_strokes(c, [Bd.rect(730, 520, 990, 700, 4), [(720, 520), (760, 470), (960, 470), (1000, 520)]], s(p, 0.5, 0.85), INK, 5)
        Bd.text(c, L['competitor'], 860, 625, 40, INK, s(p, 0.75, 1.0), maxw=240)
    elif key == 'seats':
        sq = []
        for r in range(4):
            for k in range(5): sq.append(Bd.rect(110 + k * 92, 410 + r * 92, 186 + k * 92, 486 + r * 92, k * 4 + r))
        Bd.draw_strokes(c, sq, s(p, 0, 0.9), MARK, 5)
    elif key == 'taken':
        n = int(12 * s(p, 0, 0.8) + 0.999)
        for i in range(n):
            r, k = divmod(i, 5)
            Bd.fill_rr(c, 113 + k * 92, 413 + r * 92, 183 + k * 92, 483 + r * 92, 6, YEL, 0.85)
            Bd.draw_strokes(c, Bd.big_x(148 + k * 92, 448 + r * 92, 20), 1.0, RED, 6)
        Bd.text(c, L['taken'], 330, 830, 56, RED, s(p, 0.7, 1.0))
    elif key == 'update':
        Bd.draw_strokes(c, bubble(600, 410, 990, 570), s(p, 0, 0.5), INK, 5)
        Bd.text(c, L['update'], 795, 508, 54, MARK, s(p, 0.4, 1.0), maxw=350)
    elif key == 'soldout':
        Bd.stamp(c, L['soldout'], 795, 720, -0.16, p)
    elif key == 'fake':
        Bd.text(c, L['fake'], 540, 478, 84, RED, s(p, 0, 0.75), family='Poppins', maxw=860)
        Bd.draw_strokes(c, [Bd.wob([(170, 506), (910, 506)], 1.2, 2)], s(p, 0.6, 1.0), RED, 6)
    elif key == 'countdown':
        Bd.draw_strokes(c, [Bd.rrect_pts(200, 590, 760, 760, 24)], s(p, 0, 0.3), INK, 6)
        Bd.text(c, L['clock'], 480, 705, 92, INK, s(p, 0.2, 0.45), family='Poppins', maxw=520)
        Bd.draw_strokes(c, reset_arrow(860, 675, 62), s(p, 0.4, 0.6), MARK, 7)
        Bd.draw_strokes(c, Bd.big_x(520, 675, 205), s(p, 0.7, 1.0), RED, 13)
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
    poses = simulate(pf, al['end'] + 1.3)
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
        end = al['end'] + 1.0; N = int(end * FPS)
        ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr0', '-s', f'{W}x{H}',
                               '-r', str(FPS), '-i', '-', '-i', al['audio'], '-map', '0:v', '-map', '1:a',
                               '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p',
                               '-af', 'apad,loudnorm=I=-14:TP=-1.5:LRA=11', '-c:a', 'aac', '-b:a', '192k', '-t', f'{end:.3f}', outp],
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
    # decoracao
    Bd.draw_strokes(c, hourglass(300, 815, 170), 1.0, INK, 6)
    c.color(ORANGE, 0.85); c.new_path(); c.move(268, 755); c.line(332, 755); c.line(300, 800); c.close(); c.fill()
    c.new_path(); c.move(270, 885); c.line(330, 885); c.line(300, 860); c.close(); c.fill()
    Bd.stamp(c, L['cstamp'], 690, 815, -0.1, 1.0)
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

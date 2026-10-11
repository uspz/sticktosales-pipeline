"""Licao 13 (Reversao de risco / garantia) no formato vertical com o professor de palito.
uso:
  python3 lesson13.py stills <EN|PT> <saida.png> <t1,t2,...> [align.json]
  python3 lesson13.py render <EN|PT> <align.json> <saida.mp4>
  python3 lesson13.py cover <EN|PT> <saida.png>
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
LESSON = 13

TXT = {
    'EN': dict(
        titles=['THE MATTRESS TEST', 'THE BIG FEAR', 'TIP 1: A GUARANTEE', 'TIP 2: LET THEM TRY', 'TIP 3: PUT IT IN WRITING',
                'EXAMPLE', 'ONE RULE', 'THIS WEEK', "THAT'S IT!"],
        freeret='FREE RETURN', risk='RISK REVERSAL', wasted='WASTED MONEY?', take='YOU TAKE THE RISK', days='DAYS',
        moneyback='MONEY BACK', noq='no questions asked', sample='FREE SAMPLE', test='SMALL TEST', coin='\u00a31',
        nofear='NO FEAR', guarantee='GUARANTEE', real='FEELS REAL', offer="Don't love it? Pay \u00a30", keep='KEEP YOUR WORD',
        terms='*terms and conditions apply', trust='TRUST LOST',
        ch1='One clear guarantee', ch2='Say it before the price', follow='+ FOLLOW', every='a new lesson every day',
        chip='Stick To Sales \u00b7 Lesson #13', cover=['RISK', 'REVERSAL'], cstamp='GUARANTEE'),
    'PT': dict(
        titles=['O TESTE DO COLCH\u00c3O', 'O GRANDE MEDO', 'DICA 1: UMA GARANTIA', 'DICA 2: DEIXE EXPERIMENTAR', 'DICA 3: POR ESCRITO',
                'EXEMPLO', 'UMA REGRA', 'NESTA SEMANA', 'POR HOJE \u00c9 S\u00d3!'],
        freeret='DEVOLU\u00c7\u00c3O GR\u00c1TIS', risk='REVERS\u00c3O DE RISCO', wasted='DINHEIRO PERDIDO?', take='VOC\u00ca ASSUME O RISCO',
        days='DIAS', moneyback='DINHEIRO DE VOLTA', noq='sem perguntas', sample='AMOSTRA GR\u00c1TIS', test='TESTE PEQUENO',
        coin='R$1', nofear='SEM MEDO', guarantee='GARANTIA', real='PARECE REAL', offer='N\u00e3o amou? Paga R$0',
        keep='CUMPRA SUA PALAVRA', terms='*sujeito a condi\u00e7\u00f5es', trust='CONFIAN\u00c7A PERDIDA',
        ch1='Uma garantia clara', ch2='Fale antes do pre\u00e7o', follow='+ SEGUIR', every='li\u00e7\u00e3o nova todo dia',
        chip='Stick To Sales \u00b7 Li\u00e7\u00e3o #13', cover=['REVERS\u00c3O', 'DE RISCO'], cstamp='GARANTIA'),
}

MARKED = {
    'EN': [
        "{brow}Would you buy a {draw:bed}{point:bed}mattress you've never lain on? You would, if you can {draw:back}{point:back}send it "
        "back for free. {draw:risk}{present_hi}That's *risk reversal.",
        "Every customer fears one thing: {draw:wallet}{point:wallet}wasting their money. Take that {draw:shield}{point:shield}risk on "
        "yourself, and the sale gets {calm}easy.",
        "Tip one: offer a {draw:badge}{point:badge}*guarantee. Thirty days, {draw:money}{point:money}money back, {draw:noq}no questions asked.",
        "Tip two: let them *try first. A {draw:sample}{point:sample}free sample or a {draw:test}{point:test}small test "
        "{draw:nofear}removes the *fear.",
        "{walk:610}Tip three: put it in {draw:paper}{point:paper}writing. A promise on {draw:sign}{point:sign}paper feels {draw:real}real.",
        "{walk:480}Example: a web designer says: {draw:offer}{present_hi}if you don't love the first draft, you pay nothing. {draw:bars}{point:bars}Clients stop "
        "hesitating, and she {draw:x2}{wide}closes twice as many.",
        "{walk:540}One rule: only promise what you can {draw:keep}{serious}keep. A guarantee you {draw:dodge}{neg}dodge destroys "
        "{draw:trust}{point:trust}trust.",
        "{walk:420}This week, add {draw:check1}{point:check1!}one clear guarantee to your offer, and {draw:check2}{point:check2!}say it "
        "before the price.",
        "{walk:540}That's it for today. {draw:follow}{wave}Follow for a new sales lesson every day.",
    ],
    'PT': [
        "{brow}Voc\u00ea compraria um {draw:bed}{point:bed}colch\u00e3o sem nunca ter deitado nele? Compraria, se pudesse "
        "{draw:back}{point:back}devolver de gra\u00e7a. {draw:risk}{present_hi}Isso \u00e9 *revers\u00e3o de risco.",
        "Todo cliente tem medo de uma coisa: {draw:wallet}{point:wallet}jogar dinheiro fora. Assuma esse {draw:shield}{point:shield}risco, "
        "e a venda fica {calm}f\u00e1cil.",
        "Dica um: ofere\u00e7a {draw:badge}{point:badge}*garantia. Trinta dias, {draw:money}{point:money}dinheiro de volta, "
        "{draw:noq}sem perguntas.",
        "Dica dois: deixe experimentar *primeiro. Uma {draw:sample}{point:sample}amostra gr\u00e1tis ou um {draw:test}{point:test}teste "
        "pequeno {draw:nofear}tira o *medo.",
        "{walk:610}Dica tr\u00eas: coloque por {draw:paper}{point:paper}escrito. {draw:sign}{point:sign}Promessa no papel "
        "{draw:real}parece real.",
        "{walk:480}Exemplo: uma designer diz: {draw:offer}{present_hi}se voc\u00ea n\u00e3o gostar do primeiro rascunho, n\u00e3o paga nada. "
        "{draw:bars}{point:bars}O cliente para de hesitar, e ela {draw:x2}{wide}fecha o dobro.",
        "{walk:540}Uma regra: s\u00f3 prometa o que voc\u00ea {draw:keep}{serious}cumpre. Garantia que voc\u00ea {draw:dodge}{neg}foge destr\u00f3i a "
        "{draw:trust}{point:trust}confian\u00e7a.",
        "{walk:420}Nesta semana, coloque {draw:check1}{point:check1!}uma garantia clara na sua oferta, e {draw:check2}{point:check2!}fale "
        "antes do pre\u00e7o.",
        "{walk:540}Por hoje \u00e9 s\u00f3. {draw:follow}{wave}Segue o canal pra uma li\u00e7\u00e3o de venda nova todo dia.",
    ],
}

ANCHORS = {'bed': (330, 610), 'back': (780, 600), 'risk': (540, 892), 'wallet': (280, 640), 'shield': (770, 590),
           'badge': (540, 520), 'money': (540, 780), 'noq': (540, 860), 'sample': (300, 560), 'test': (770, 560),
           'nofear': (540, 880), 'paper': (540, 600), 'sign': (540, 720), 'real': (540, 900), 'offer': (540, 480),
           'bars': (590, 800), 'x2': (650, 680), 'keep': (540, 500), 'dodge': (540, 680), 'trust': (540, 850),
           'check1': (155, 485), 'check2': (155, 645), 'follow': (540, 560)}
for i in range(9): ANCHORS[f'title{i}'] = (540, 270)
SLIDE_ITEMS = [['bed', 'back', 'risk'], ['wallet', 'shield'], ['badge', 'money', 'noq'], ['sample', 'test', 'nofear'],
               ['paper', 'sign', 'real'], ['offer', 'bars', 'x2'], ['keep', 'dodge', 'trust'], ['check1', 'check2'], ['follow']]
DUR = {'bed': 1.0, 'back': 1.1, 'risk': 0.6, 'wallet': 1.0, 'shield': 1.0, 'badge': 1.0, 'money': 0.6, 'noq': 0.7,
       'sample': 0.9, 'test': 0.8, 'nofear': 0.6, 'paper': 1.0, 'sign': 0.9, 'real': 0.5, 'offer': 1.0, 'bars': 1.0,
       'x2': 0.5, 'keep': 0.7, 'dodge': 0.9, 'trust': 0.45, 'check1': 0.8, 'check2': 0.8, 'follow': 0.9}


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


def shield_pts(cx, cy, w, h):
    return Bd.wob([(cx, cy - h / 2), (cx + w / 2, cy - h / 2 + h * 0.1), (cx + w / 2, cy + h * 0.1), (cx, cy + h / 2),
                   (cx - w / 2, cy + h * 0.1), (cx - w / 2, cy - h / 2 + h * 0.1), (cx, cy - h / 2)], 1.0, 5)


# ------------------------------------------------------------------ desenho dos itens
def draw_item(c, key, p, L):
    s = Bd.sub
    if key == 'bed':
        bed = [Bd.wob(Bd.rrect_pts(100, 600, 560, 670, 18), 0.8, 1), Bd.wob(Bd.rrect_pts(125, 562, 255, 602, 16), 0.8, 2),
               [(100, 670), (100, 735)], [(560, 670), (560, 735)], [(100, 535), (100, 735)]]
        Bd.draw_strokes(c, bed, s(p, 0, 0.8), MARK, 6)
        Bd.text(c, '?', 410, 565, 110, RED, s(p, 0.6, 1.0), family='Poppins')
    elif key == 'back':
        Bd.draw_strokes(c, cube(640, 480, 150), s(p, 0, 0.55), MARK, 6)
        Bd.draw_strokes(c, reset_arrow(925, 585, 46), s(p, 0.4, 0.75), GREEN, 8)
        Bd.text(c, L['freeret'], 775, 790, 50, GREEN, s(p, 0.7, 1.0), maxw=420)
    elif key == 'risk':
        Bd.fill_rr(c, 120, 852, 960, 932, 14, YEL, 0.6 * s(p, 0, 0.4))
        Bd.text(c, L['risk'], 540, 913, 72, INK, s(p, 0.2, 1.0), family='Poppins', maxw=800)
    elif key == 'wallet':
        w = [Bd.wob(Bd.rrect_pts(120, 560, 440, 730, 16), 0.8, 3), [(120, 615), (440, 615)], Bd.circle(412, 672, 20, n=14)]
        Bd.draw_strokes(c, w, s(p, 0, 0.5), MARK, 6)
        bills = [[(205, 490), (290, 462), (312, 512), (228, 540), (205, 490)], [(335, 450), (420, 428), (440, 478), (355, 500), (335, 450)]]
        Bd.draw_strokes(c, bills, s(p, 0.4, 0.8), GREEN, 5)
        Bd.draw_strokes(c, Bd.arrow(290, 420, 380, 392, 18), s(p, 0.7, 1.0), RED, 5)
        Bd.text(c, L['wasted'], 280, 800, 50, RED, s(p, 0.7, 1.0), maxw=440)
    elif key == 'shield':
        Bd.draw_strokes(c, [shield_pts(770, 585, 250, 310)], s(p, 0, 0.55), MARK, 7)
        Bd.draw_strokes(c, Bd.check_mark(770, 590, 105), s(p, 0.5, 0.8), GREEN, 11)
        Bd.text(c, L['take'], 775, 805, 44, INK, s(p, 0.7, 1.0), maxw=420)
    elif key == 'badge':
        Bd.draw_strokes(c, [Bd.circle(540, 520, 125, n=40), Bd.circle(540, 520, 105, n=36)], s(p, 0, 0.6), MARK, 6)
        Bd.draw_strokes(c, [[(480, 630), (455, 735), (500, 710), (525, 745), (535, 640)], [(600, 630), (625, 735), (580, 710), (555, 745), (545, 640)]],
                        s(p, 0.4, 0.8), RED, 6)
        Bd.text(c, '30', 540, 548, 104, INK, s(p, 0.55, 0.85), family='Poppins')
        Bd.text(c, L['days'], 540, 604, 40, INK, s(p, 0.75, 1.0), family='Poppins')
    elif key == 'money':
        Bd.text(c, L['moneyback'], 540, 800, 62, GREEN, p, family='Poppins', maxw=860)
    elif key == 'noq':
        Bd.text(c, L['noq'], 540, 880, 54, INK, p, maxw=860)
    elif key == 'sample':
        Bd.draw_strokes(c, Bd.bottle(300, 430, 250, 3), s(p, 0, 0.8), MARK, 6)
        Bd.text(c, L['sample'], 300, 770, 46, GREEN, s(p, 0.7, 1.0), maxw=420)
    elif key == 'test':
        Bd.draw_strokes(c, [Bd.circle(770, 560, 112, n=36), Bd.circle(770, 560, 94, n=34)], s(p, 0, 0.7), ORANGE, 6)
        Bd.text(c, L['coin'], 770, 590, 80, INK, s(p, 0.5, 0.9), family='Poppins', maxw=170)
        Bd.text(c, L['test'], 770, 770, 46, INK, s(p, 0.7, 1.0), maxw=400)
    elif key == 'nofear':
        Bd.draw_strokes(c, Bd.check_mark(330, 870, 70), s(p, 0, 0.4), GREEN, 10)
        Bd.text(c, L['nofear'], 610, 893, 72, GREEN, s(p, 0.25, 1.0), family='Poppins', maxw=520)
    elif key == 'paper':
        Bd.draw_strokes(c, [Bd.rect(330, 390, 750, 810, 6)], s(p, 0, 0.6), MARK, 6)
        Bd.text(c, L['guarantee'], 540, 458, 44, INK, s(p, 0.5, 0.8), family='Poppins', maxw=360)
        Bd.draw_strokes(c, [Bd.wob([(380, 510), (700, 510)], 1.2, 1), Bd.wob([(380, 560), (700, 560)], 1.2, 2),
                            Bd.wob([(380, 610), (620, 610)], 1.2, 3)], s(p, 0.6, 1.0), '#8A8A92', 4)
    elif key == 'sign':
        Bd.draw_strokes(c, [[(380, 765), (700, 765)]], s(p, 0, 0.3), INK, 4)
        Bd.draw_strokes(c, [[(392, 735), (420, 690), (440, 745), (468, 700), (490, 742), (540, 706), (580, 738), (650, 716)]],
                        s(p, 0.25, 1.0), MARK, 6)
    elif key == 'real':
        Bd.fill_rr(c, 270, 862, 810, 942, 14, YEL, 0.6 * s(p, 0, 0.4))
        Bd.text(c, L['real'], 540, 923, 70, INK, s(p, 0.2, 1.0), family='Poppins', maxw=520)
    elif key == 'offer':
        Bd.draw_strokes(c, bubble(150, 400, 930, 560), s(p, 0, 0.5), INK, 5)
        Bd.text(c, L['offer'], 540, 506, 58, MARK, s(p, 0.4, 1.0), maxw=720)
        Bd.draw_strokes(c, mini_fig(180, 745, 1.05, 0.3), s(p, 0.2, 0.9), MARK, 5)
    elif key == 'bars':
        k = s(p, 0, 1.0)
        c.color(MARK, 0.28); c.rect(430, 930 - 110 * k, 100, 110 * k); c.fill()
        c.color(GREEN, 0.38); c.rect(600, 930 - 230 * k, 100, 230 * k); c.fill()
        Bd.draw_strokes(c, [[(380, 930), (780, 930)]], s(p, 0, 0.3), INK, 5)
    elif key == 'x2':
        Bd.text(c, 'x2', 650, 690, 84, GREEN, p, family='Poppins')
    elif key == 'keep':
        Bd.text(c, L['keep'], 540, 520, 66, GREEN, s(p, 0, 0.8), family='Poppins', maxw=860)
        Bd.draw_strokes(c, [Bd.wob([(160, 548), (920, 548)], 1.2, 2)], s(p, 0.6, 1.0), GREEN, 6)
    elif key == 'dodge':
        Bd.text(c, L['terms'], 540, 700, 56, INK, s(p, 0, 0.6), maxw=820)
        Bd.draw_strokes(c, [Bd.wob([(150, 678), (930, 678)], 1.2, 4)], s(p, 0.55, 1.0), RED, 7)
    elif key == 'trust':
        Bd.stamp(c, L['trust'], 540, 860, -0.08, p)
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
    Bd.draw_strokes(c, [shield_pts(260, 815, 190, 230)], 1.0, MARK, 7)
    Bd.draw_strokes(c, Bd.check_mark(260, 820, 80), 1.0, GREEN, 12)
    size = Bd.fit(c, L['cstamp'], 70, 430, 'Poppins')
    tw = c.extents(L['cstamp']).x_advance
    cx0, cy0 = 660, 815
    c.color(RED); c.text(cx0 - tw / 2, cy0 + size * 0.35, L['cstamp'])
    rx, ry = tw / 2 + 48, size * 0.5 + 52
    ell = []
    for i in range(61):
        a = -0.6 + (2 * math.pi + 0.9) * i / 60
        k = 1 + 0.045 * (a + 0.6) / (2 * math.pi) + 0.015 * math.sin(3 * a)
        ell.append((cx0 + rx * k * math.cos(a), cy0 + ry * k * math.sin(a)))
    Bd.draw_strokes(c, [ell], 1.0, RED, 8)
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

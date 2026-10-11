import math, sys
from cairoc import Canvas
from rig2 import draw_character, Pose, hand_params, skeleton, STAND_H
import board as Bd
from board import INK, MARK, RED, YEL, GREEN, ORANGE
from PIL import Image

W, H = 1080, 1920
T = {'EN': dict(chip='Stick To Sales', title=['NEW', 'ANIMATION!'], q1='Did you like', q2='the new style?', hint='vote below'),
     'PT': dict(chip='Stick To Sales', title=['NOVA', 'ANIMAÇÃO!'], q1='Curtiu o', q2='estilo novo?', hint='vota aqui embaixo')}

def make(lang, out):
    L = T[lang]
    c = Canvas(W, H)
    c.clear('#F3EFE6')
    # quadro
    BX, BY, BW, BH = 60, 230, 960, 640
    c.color('#000000', 0.10); c.rrect(BX + 8, BY + 12, BW, BH, 24); c.fill()
    c.color('#FFFFFF'); c.rrect(BX, BY, BW, BH, 24); c.fill(True); c.color('#3A3A40'); c.lw(11); c.stroke()
    c.color('#3A3A40'); c.rrect(BX + 70, BY + BH + 7, BW - 140, 14, 6); c.fill()
    c.font('Poppins', 42, True); w = c.extents(L['chip']).x_advance
    c.color('#111111'); c.rrect(540 - w / 2 - 34, 290, w + 68, 76, 38); c.fill()
    c.color('#FFFFFF'); c.text(540 - w / 2, 342, L['chip'])
    c.color(YEL); c.rrect(110, 405, 860, 300, 26); c.fill(True); c.color('#111111'); c.lw(8); c.stroke()
    for i, line in enumerate(L['title']):
        Bd.fit(c, line, 130, 780, 'Poppins')
        e = c.extents(line); c.color('#111111'); c.text(540 - e.x_advance / 2, 540 + i * 135, line)
    for (sx, sy, r) in ((150, 780, 22), (930, 770, 26), (880, 300, 18), (200, 320, 16)):
        Bd.draw_strokes(c, [[(sx, sy - r), (sx, sy + r)], [(sx - r, sy), (sx + r, sy)]], 1.0, ORANGE, 7)
    # pergunta
    for i, line in enumerate((L['q1'], L['q2'])):
        size = Bd.fit(c, line, 96, 900, 'Poppins')
        e = c.extents(line); x = 540 - e.x_advance / 2; y = 1010 + i * 108
        c.text_path(x, y, line); c.color('#000000'); c.lw(16); c.stroke(True); c.color('#FFFFFF' if i == 0 else YEL); c.fill()
    # professor acenando ao lado
    sc = 1.0; floor = 1800
    p = Pose(px=190, py=floor - STAND_H * sc, sc=sc)
    p.fA = (190 - 28, floor); p.fB = (190 + 28, floor); p.toeA = math.pi - 0.16; p.toeB = 0.16
    S = skeleton(p)['S']
    p.wB = (S[0] + 88, S[1] - 104); p.handB = dict(hand_params('open'), ang=-1.45, scale=1.0, fore=1.0)
    p.wA = (S[0] - 40, S[1] + 168); p.handA = dict(hand_params('relax'), ang=1.7, scale=1.0, fore=1.0)
    p.mouth_w, p.mouth_h, p.smile, p.brow_raise, p.eye_x = 26, 18, 1.0, 0.8, 0.6
    p.yaw = 0.25
    draw_character(c, p)
    # seta para a area da enquete
    Bd.text(c, L["hint"], 650, 1330, 56, MARK, 1.0, maxw=520)
    Bd.draw_strokes(c, Bd.arrow(650, 1360, 650, 1480, 26), 1.0, RED, 9)
    Image.fromarray(c.rgb()).save(out)

make(sys.argv[1], sys.argv[2])

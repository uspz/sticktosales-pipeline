import math
from cairoc import Canvas
import rig2
from rig2 import Pose, hand_params, skeleton, STAND_H, draw_character
import board as Bd
from board import YEL, RED, MARK, GREEN, ORANGE
from PIL import Image, ImageDraw

S = 1080

def teacher(c, x, y_floor, sc, point=True, ink='#1E1E22'):
    rig2.INK = ink; rig2.draw_hand.__defaults__ = (ink,)
    p = Pose(px=x, py=y_floor - STAND_H * sc, sc=sc)
    p.fA = (x - 28 * sc, y_floor); p.fB = (x + 28 * sc, y_floor); p.toeA = math.pi - 0.16; p.toeB = 0.16
    Sh = skeleton(p)['S']
    if point:
        p.wB = (Sh[0] + 80 * sc, Sh[1] - 155 * sc); p.handB = dict(hand_params('point'), ang=-1.25, scale=1.0, fore=1.0)
    p.wA = (Sh[0] - 95 * sc, Sh[1] + 55 * sc); p.handA = dict(hand_params('open'), ang=math.pi + 0.35, scale=1.0, fore=1.0)
    p.mouth_w, p.mouth_h, p.smile, p.brow_raise, p.eye_x, p.eye_y = 26, 18, 1.0, 0.7, 0.45, -0.6
    p.yaw = 0.18; p.pitch = -0.15
    draw_character(c, p, shadow=False)
    rig2.INK = '#1E1E22'; rig2.draw_hand.__defaults__ = ('#1E1E22',)

def arrow_up(c, pts, color, w):
    c.color(color); c.lw(w); c.new_path(); c.polyline(pts); c.stroke()
    (x0, y0), (x1, y1) = pts[-2], pts[-1]
    a = math.atan2(y1 - y0, x1 - x0); L = w * 2.6
    c.new_path(); c.move(x1 + math.cos(a) * w * 0.6, y1 + math.sin(a) * w * 0.6)
    c.line(x1 - L * math.cos(a - 0.55), y1 - L * math.sin(a - 0.55)); c.line(x1 - L * math.cos(a + 0.55), y1 - L * math.sin(a + 0.55)); c.close(); c.fill()

def opt1(out):   # amarelo + seta de vendas
    c = Canvas(S, S); c.clear(YEL)
    arrow_up(c, [(600, 860), (720, 700), (800, 770), (950, 470)], '#1E1E22', 44)
    teacher(c, 380, 1480, 2.3)
    Image.fromarray(c.rgb()).save(out)

def opt2(out):   # escuro, boneco branco, aro amarelo
    c = Canvas(S, S); c.clear('#17171B')
    c.color(YEL); c.lw(34); c.new_path(); c.arc(540, 540, 500); c.stroke()
    arrow_up(c, [(600, 850), (715, 700), (795, 765), (930, 480)], YEL, 40)
    rig2.HEAD_FILL = '#17171B'
    teacher(c, 380, 1470, 2.2, ink='#FFFFFF')
    rig2.HEAD_FILL = '#FFFFFF'
    Image.fromarray(c.rgb()).save(out)

def opt3(out):   # quadro com SALES
    c = Canvas(S, S); c.clear('#F3EFE6')
    c.lw(14); c.color('#FFFFFF'); c.rrect(470, 250, 520, 470, 28); c.fill(True); c.color('#3A3A40'); c.stroke()
    c.color(YEL); c.rrect(505, 300, 450, 140, 20); c.fill()
    c.font('Poppins', 104, True); e = c.extents('SALES'); c.color('#1E1E22'); c.text(730 - e.x_advance / 2, 408, 'SALES')
    arrow_up(c, [(530, 640), (640, 560), (720, 610), (930, 490)], GREEN, 22)
    teacher(c, 300, 1430, 2.05)
    Image.fromarray(c.rgb()).save(out)

opt1('/home/claude/logo_opcao1.png'); opt2('/home/claude/logo_opcao2.png'); opt3('/home/claude/logo_opcao3.png')
ims = []
for i in (1, 2, 3):
    im = Image.open(f'/home/claude/logo_opcao{i}.png').resize((360, 360))
    m = Image.new('L', (360, 360), 0); ImageDraw.Draw(m).ellipse((0, 0, 359, 359), fill=255)
    bg = Image.new('RGB', (360, 360), (230, 230, 230)); bg.paste(im, (0, 0), m); ims.append(bg)
sheet = Image.new('RGB', (3 * 380 + 20, 400), (230, 230, 230))
for i, im in enumerate(ims): sheet.paste(im, (20 + i * 380, 20))
sheet.save('logo_prev.png')

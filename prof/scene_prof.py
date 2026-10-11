"""Cena-teste: professor de palito explicando com quadro branco. Sem audio, legenda sincronizada."""
import math, sys, os, subprocess
from cairoc import Canvas
from rig2 import draw_character, INK
from perf import Perf, simulate, FPS, FLOOR, sstep, clamp

W, H = 1920, 1080
BX, BY, BW, BH = 980, 170, 880, 560
MARK = '#1F4E9C'; RED = '#D64541'; YEL = '#FFD21F'; BG = '#F3EFE6'


# ------------------------------------------------------------------ roteiro / atuacao
def build():
    pf = Perf(x0=-170)
    pf.anchors.update({
        'vitrine': (1230, 445), 'luz': (1230, 440), 'titulo2': (1600, 388),
        'item1': (1480, 450), 'item2': (1480, 520), 'item3': (1480, 590),
        'recorte': (1290, 640), 'linha': (1450, 640), 'phone': (582, 566)})
    pf.camera(0.0, 1022, 560, 1.12)
    pf.wait(0.35)
    w = pf.walk(600, v=285)
    pf.look(w.t0 + 1.9, 'cam')
    pf.emotion(w.t0 + 1.9, smile=0.85, raise_=0.3)
    pf.t = w.t0 + w.T + 0.12
    pf.gesture('wave', 'B', pf.t + 0.1, pf.t + 1.25, prep=0.32)
    pf.emotion(pf.t, smile=1.0, raise_=0.45)
    pf.wait(1.35)
    pf.emotion(pf.t, smile=0.55, raise_=0.05)
    pf.camera(pf.t - 0.6, 760, 640, 1.36)
    pf.say("{you}Você já {phone}olhou um vídeo de alguém, {count1}viajando, com {count2}carro novo, "
           "sorrindo numa {count3}praia {shrug}perfeita?")
    pf.wait(0.1)
    pf.camera(pf.t - 0.2, 1022, 560, 1.12)
    pf.say("{walk:850}{look:vitrine}Rede social é uma {draw:vitrine}{present}*vitrine.")
    pf.say("E vitrine mostra o {point:vitrine}*melhor produto, na {draw:luz}{look:luz}*melhor luz.")
    pf.wait(0.15)
    w = pf.walk(1335, v=290)
    pf.look(pf.t + 0.2, 'walk')
    pf.look(w.t0 + w.T - 0.25, 'cam')
    pf.t = w.t0 + w.T + 0.1
    pf.say("{serious}{neg}{draw:titulo2}*Ninguém posta a {draw:item1}{point:item1!}conta atrasada, "
           "a {draw:item2}{point:item2!}briga em casa, o dia em que {draw:item3}{point:item3!}não saiu da cama.")
    pf.wait(0.1)
    pf.emotion(pf.t, smile=0.45, furrow=0.0)
    w = pf.walk(640, v=300)
    pf.look(pf.t + 0.15, 'walk')
    pf.camera(pf.t + 0.6, 900, 625, 1.3)
    pf.look(w.t0 + w.T - 0.3, 'cam')
    pf.t = w.t0 + w.T + 0.15
    pf.say("{you:A}Você está vendo um {draw:recorte}{small}recorte, "
           "{shake:0.2}não a {draw:linha}{wide}*história inteira.")
    pf.emotion(pf.t, smile=0.85)
    pf.nods.append((pf.t - 0.25, 0.8))
    pf.wait(1.6)
    return pf


# ------------------------------------------------------------------ quadro
def strokes_len(strokes):
    tot = 0.0
    for pts in strokes:
        for a, b in zip(pts, pts[1:]): tot += math.hypot(b[0] - a[0], b[1] - a[1])
    return tot


def draw_strokes(c, strokes, prog, color, width):
    if prog <= 0: return
    total = strokes_len(strokes) * clamp(prog, 0, 1)
    c.color(color); c.lw(width)
    acc = 0.0
    for pts in strokes:
        c.new_path(); c.move(*pts[0])
        for a, b in zip(pts, pts[1:]):
            seg = math.hypot(b[0] - a[0], b[1] - a[1])
            if acc + seg <= total:
                c.line(*b); acc += seg
            else:
                k = (total - acc) / seg if seg else 0
                c.line(a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
                acc = total; break
        c.stroke()
        if acc >= total: break


def circle_pts(cx, cy, r, a0=0.0, a1=2 * math.pi, n=28):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def wobble(pts, amp=1.2, seed=0):
    out = []
    for i, (x, y) in enumerate(pts):
        out.append((x + amp * math.sin(i * 1.7 + seed), y + amp * math.cos(i * 2.3 + seed * 0.7)))
    return out


SHOP = []
SHOP.append(wobble([(1085, 352), (1085, 562), (1375, 562), (1375, 352)], 1.0, 1))
aw = [(1072, 352)]
for i in range(8):
    x0 = 1072 + i * 40
    aw += circle_pts(x0 + 20, 352, 20, math.pi, 0, 10)[1:]
SHOP.append(aw)
SHOP.append([(1072, 352), (1095, 318), (1365, 318), (1388, 352)])
SHOP.append(circle_pts(1230, 425, 17))
SHOP.append([(1230, 442), (1230, 498)])
SHOP.append([(1230, 458), (1205, 480)])
SHOP.append([(1230, 458), (1252, 434)])
SHOP.append([(1230, 498), (1214, 536)])
SHOP.append([(1230, 498), (1246, 536)])
SHOP.append([(1095, 540), (1365, 540)])
SMILE = [circle_pts(1230, 425, 9, 0.35, 2.8, 8)]
LUZ = []
for (sx, sy, r) in ((1112, 392, 13), (1348, 398, 12), (1302, 476, 9), (1150, 500, 8)):
    LUZ.append([(sx, sy - r), (sx, sy + r)]); LUZ.append([(sx - r, sy), (sx + r, sy)])

ITEMS = {
    'titulo2': ('text', 'O que ninguém posta:', 1442, 388, 38, INK),
    'item1': ('text', '• conta atrasada', 1452, 463, 42, MARK),
    'item2': ('text', '• briga em casa', 1452, 533, 42, MARK),
    'item3': ('text', '• não saiu da cama', 1452, 603, 42, MARK),
}


def draw_text_wipe(c, txt, x, y, size, color, prog):
    if prog <= 0: return
    c.font('Comic Neue', size, True)
    e = c.extents(txt)
    c.save(); c.rect(x - 4, y - size * 1.2, (e.x_advance + 8) * clamp(prog, 0, 1), size * 1.7); c.clip()
    c.color(color); c.text(x, y, txt); c.restore()


def draw_board(c, pf, t):
    # quadro
    c.save()
    c.color('#000000', 0.10); c.rrect(BX + 8, BY + 12, BW, BH, 18); c.fill()
    c.color('#FFFFFF'); c.rrect(BX, BY, BW, BH, 18); c.fill(True)
    c.color('#3A3A40'); c.lw(10); c.stroke()
    c.color('#3A3A40'); c.rrect(BX + 60, BY + BH + 6, BW - 120, 13, 6); c.fill()
    c.color(MARK); c.rrect(BX + 120, BY + BH - 4, 46, 10, 4); c.fill()
    c.color(RED); c.rrect(BX + 180, BY + BH - 4, 46, 10, 4); c.fill()
    c.restore()

    def prog(name, dur):
        if name not in pf.board: return 0.0
        return sstep((t - pf.board[name]) / dur)
    pv = prog('vitrine', 1.25)
    draw_text_wipe(c, 'VITRINE', 1112, 290, 64, INK, pv / 0.45 if pv < 0.45 else 1.0)
    draw_strokes(c, SHOP, (pv - 0.25) / 0.75, MARK, 6.5)
    if pv > 0.95: draw_strokes(c, SMILE, (pv - 0.95) / 0.05, MARK, 4.5)
    pl = prog('luz', 0.7)
    if pl > 0:
        c.save(); c.radial(1230, 450, 20, 230, [(0, '#FFD54A', 0.55 * pl), (1, '#FFD54A', 0.0)])
        c.rect(1060, 300, 340, 280); c.fill(); c.restore()
        draw_strokes(c, SHOP, 1.0, MARK, 6.5)
        draw_strokes(c, SMILE, 1.0, MARK, 4.5)
    draw_strokes(c, LUZ, pl, '#E39B00', 6)
    for k, (kind, txt, x, y, sz, col) in ITEMS.items():
        draw_text_wipe(c, txt, x, y, sz, col, prog(k, 0.55))
    # linha do tempo: recorte primeiro, depois a historia inteira
    pr = prog('recorte', 0.5)
    if pr > 0:
        c.save(); c.color(YEL, 0.6 * pr); c.rrect(1250, 608, 82, 64, 8); c.fill(); c.restore()
        draw_strokes(c, [wobble([(1250, 608), (1332, 608), (1332, 672), (1250, 672), (1250, 608)], 0.8, 3)], pr, INK, 5)
        draw_text_wipe(c, 'recorte', 1243, 704, 30, INK, pr)
        c.save(); c.color('#E39B00', pr); c.arc(1308, 627, 8); c.fill()
        c.color(MARK, pr); c.lw(3.5); c.new_path(); c.move(1258, 655)
        c.curve(1272, 645, 1285, 665, 1300, 655); c.curve(1312, 647, 1320, 662, 1326, 655); c.stroke(); c.restore()
    pli = prog('linha', 0.9)
    if pli > 0:
        Ll = 210 * pli; Lr = 100 * pli
        draw_strokes(c, [[(1250, 640), (1250 - Ll, 640)], [(1332, 640), (1332 + Lr, 640)]], 1.0, MARK, 6)
        for i in (-2, -1, 1, 2):
            xx = 1291 + i * 82
            if (xx < 1291 and 1291 - xx < 41 + 210 * pli) or (xx > 1291 and xx - 1291 < 41 + 100 * pli):
                c.color(MARK); c.lw(4); c.new_path(); c.move(xx, 630); c.line(xx, 650); c.stroke()
        if pli > 0.55:
            draw_text_wipe(c, 'a história inteira', 1046, 614, 32, MARK, (pli - 0.55) / 0.45)


# ------------------------------------------------------------------ fundo e legenda
def draw_bg(c):
    c.clear(BG)
    c.linear(0, FLOOR, 0, FLOOR + 200, [(0, '#E7E0D2', 1.0), (1, '#DDD5C5', 1.0)])
    c.rect(-2000, FLOOR, 6000, 800); c.fill()
    c.color('#CFC6B4'); c.lw(3); c.new_path(); c.move(-2000, FLOOR + 1); c.line(4000, FLOOR + 1); c.stroke()


def draw_vignette(c):
    c.radial(W / 2, H / 2, H * 0.6, H * 1.2, [(0, '#000000', 0.0), (1, '#000000', 0.10)])
    c.rect(0, 0, W, H); c.fill()


def draw_captions(c, pf, t):
    ch = None
    for i, chunk in enumerate(pf.chunks):
        a = chunk[0]['t0'] - 0.12
        b = chunk[-1]['t1'] + 0.25
        if i + 1 < len(pf.chunks): b = min(b, pf.chunks[i + 1][0]['t0'] - 0.12)
        if a <= t < b: ch = (chunk, a, b)
    if ch is None: return
    chunk, a, b = ch
    size = 54
    c.font('Poppins', size, True)
    spw = c.extents('a a').x_advance - c.extents('aa').x_advance
    spw += 15
    widths = [c.extents(wd['text']).x_advance + spw for wd in chunk]
    total = sum(widths) - spw
    k_in = sstep((t - a) / 0.16)
    y = H - 82 + (1 - k_in) * 18
    x = W / 2 - total / 2
    for wd, wdt in zip(chunk, widths):
        active = wd['t0'] - 0.03 <= t < wd['t1'] + 0.05
        done = t >= wd['t1']
        pop = 1.0
        if active:
            u = (t - wd['t0'] + 0.03) / 0.16
            pop = 1.0 + 0.14 * math.sin(math.pi * clamp(u, 0, 1)) if u < 1 else 1.0
        tw = c.extents(wd['text']).x_advance
        c.save()
        c.translate(x + tw / 2, y - size * 0.35); c.scale(pop, pop); c.translate(-tw / 2, size * 0.35)
        c.text_path(0, 0, wd['text'])
        c.color('#000000', k_in); c.lw(11); c.stroke(True)
        col = YEL if active else ('#FFFFFF' if not done else '#FFFFFF')
        c.color(col, k_in); c.fill()
        c.restore()
        x += wdt


def cam_at(pf, t):
    keys = sorted(pf.cam, key=lambda k: k[0])
    cx, cy, z = keys[0][1:]
    for i in range(1, len(keys)):
        tk, nx, ny, nz = keys[i]
        if t <= tk: break
        k = sstep((t - tk) / 1.6)
        cx, cy, z = cx + (nx - cx) * k, cy + (ny - cy) * k, z + (nz - z) * k
    return cx, cy, z


def render_frame(c, pf, poses, f):
    t = f / FPS
    cx, cy, z = cam_at(pf, t)
    c.save()
    c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-cx, -cy)
    draw_bg(c)
    draw_board(c, pf, t)
    draw_character(c, poses[f])
    c.restore()
    draw_vignette(c)
    draw_captions(c, pf, t)
    end = len(poses) / FPS
    fade = min(sstep(t / 0.35), sstep((end - t) / 0.45))
    if fade < 1:
        c.color('#000000', 1 - fade); c.rect(0, 0, W, H); c.fill()


def get_all():
    pf = build()
    dur = pf.end_time() + 0.2
    poses = simulate(pf, dur)
    return pf, poses


if __name__ == '__main__':
    mode = sys.argv[1]
    pf, poses = get_all()
    if mode == 'info':
        print('dur', len(poses) / FPS, 'frames', len(poses))
        for wd in pf.words[:6]: print(round(wd['t0'], 2), wd['text'])
    elif mode == 'stills':
        from PIL import Image
        out = sys.argv[2]; times = [float(x) for x in sys.argv[3].split(',')]
        c = Canvas(W, H)
        ims = []
        for tt in times:
            f = min(len(poses) - 1, int(tt * FPS))
            render_frame(c, pf, poses, f)
            ims.append(Image.fromarray(c.rgb()).resize((640, 360)))
        cols = 3; rows = (len(ims) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * 644, rows * 364), 'gray')
        for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * 644, (i // cols) * 364))
        sheet.save(out)
    elif mode == 'segment':
        a, b, outp = int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
        b = min(b, len(poses))
        ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr0', '-s', f'{W}x{H}',
                               '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17',
                               '-pix_fmt', 'yuv420p', outp], stdin=subprocess.PIPE)
        c = Canvas(W, H)
        for f in range(a, b):
            render_frame(c, pf, poses, f)
            ff.stdin.write(c.bgr0_bytes())
        ff.stdin.close(); ff.wait()
        print('segment done', a, b)

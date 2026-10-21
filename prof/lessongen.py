"""Motor genérico de lições: cada lição é um arquivo specNN.py curto (MARKED, TITLES, ITEMS, HOOK...).
uso: python3 lessongen.py stills <NN> saida.png t1,t2,... (usa alinhamentos/alNN_pt.json)
O render (aula e cortes) é feito pelo cuts.py: python3 cuts.py render NN PT <aula|dicas|exemplo> saida.mp4 [--loop]
Conferir o final em loop: python3 lessongen.py loop <NN> <aula|dicas|exemplo> saida.png
  (folha com o 1º frame, o início da volta e o último frame, e a diferença entre o 1º e o último)
"""
import sys, json, math, re, importlib, os
from cairoc import Canvas
from rig2 import draw_character
from perf import Perf, simulate, FPS, sstep, clamp
import board as Bd
from board import INK, MARK, RED, YEL, GREEN, ORANGE
import lesson13 as B   # reaproveita cena, legendas, câmera e desenhos extras

W, H, SC, FLOOR_V = B.W, B.H, B.SC, B.FLOOR_V
GRAY = '#8A8A92'
DUR = {'t': 0.7, 'bar': 0.6, 'big': 0.7, 'strike': 0.9, 'check': 0.8, 'bub': 1.0, 'stamp': 0.45, 'follow': 0.9,
       'x': 0.4, 'ok': 0.4, 'arrow': 0.5, 'icon': 0.9}


# ------------------------------------------------------------------ ícones (traços centrados em x,y; escala s)
def _sc(pts, x, y, s):
    return [(x + px * s, y + py * s) for px, py in pts]


def icon_strokes(name, x, y, s):
    R = lambda pts: Bd.wob(_sc(pts, x, y, s), 0.8, len(pts))
    C = lambda cx, cy, r, n=28: Bd.circle(x + cx * s, y + cy * s, r * s, n=n)
    if name == 'tag':
        return Bd.price_tag(x - 120 * s, y - 55 * s, x + 120 * s, y + 55 * s, 3)
    if name == 'gift':
        return [R([(-90, -40), (90, -40), (90, 90), (-90, 90), (-90, -40)]), R([(-100, -75), (100, -75), (100, -40), (-100, -40), (-100, -75)]),
                R([(0, -75), (0, 90)]), R([(0, -75), (-40, -120), (-60, -95), (0, -75), (40, -120), (60, -95), (0, -75)])]
    if name == 'truck':
        return [R([(-120, -60), (40, -60), (40, 50), (-120, 50), (-120, -60)]), R([(40, -20), (95, -20), (120, 15), (120, 50), (40, 50)]),
                C(-75, 62, 20, 16), C(80, 62, 20, 16)]
    if name == 'phone':
        return [Bd.wob(Bd.rrect_pts(x - 65 * s, y - 120 * s, x + 65 * s, y + 120 * s, 18 * s), 0.6, 1),
                R([(-50, -95), (50, -95), (50, 85), (-50, 85), (-50, -95)]), C(0, 103, 7, 10)]
    if name == 'people':
        out = []
        for i, dx in enumerate((-70, 0, 70)): out += B.mini_fig(x + dx * s, y + 70 * s, 1.15 * s, (i % 2) * 0.6)
        return out
    if name == 'fig':
        return B.mini_fig(x, y + 75 * s, 1.3 * s, 0.3) + Bd.star(x + 45 * s, y - 70 * s, 22 * s)
    if name == 'coin':
        return [C(0, 0, 70, 30), C(0, 0, 56, 26)]
    if name == 'box':
        return B.cube(x - 80 * s, y - 80 * s, 140 * s)
    if name == 'bag':
        return [R([(-75, -40), (75, -40), (90, 100), (-90, 100), (-75, -40)]), Bd.circle(x, y - 40 * s, 35 * s, math.pi, 2 * math.pi, 16)]
    if name in ('clock', 'stopwatch'):
        out = [C(0, 0, 90, 34), R([(0, 0), (0, -60)]), R([(0, 0), (40, 18)])]
        if name == 'stopwatch': out += [R([(-14, -90), (-14, -110), (14, -110), (14, -90)]), R([(-22, -114), (22, -114)])]
        return out
    if name == 'eye':
        up = [(x + 130 * s * math.cos(a), y - 70 * s * math.sin(a)) for a in [math.pi * i / 20 for i in range(21)]]
        dn = [(x + 130 * s * math.cos(a), y + 70 * s * math.sin(a)) for a in [math.pi * i / 20 for i in range(21)]]
        return [up, dn, C(0, 0, 38, 24), C(0, 0, 14, 12)]
    if name == 'chart':
        return [R([(-110, 90), (110, 90)]), R([(-110, 90), (-110, -90)]), R([(-80, 90), (-80, 30), (-45, 30), (-45, 90)]),
                R([(-20, 90), (-20, -10), (15, -10), (15, 90)]), R([(40, 90), (40, -60), (75, -60), (75, 90)])]
    if name == 'doc':
        return [R([(-80, -110), (50, -110), (80, -80), (80, 110), (-80, 110), (-80, -110)]), R([(-50, -60), (50, -60)]),
                R([(-50, -20), (50, -20)]), R([(-50, 20), (50, 20)]), R([(-50, 60), (20, 60)])]
    if name == 'stars':
        out = []
        for i in range(5): out += Bd.star(x + (i - 2) * 62 * s, y, 26 * s)
        return out
    if name == 'shield':
        return [B.shield_pts(x, y, 170 * s, 210 * s)] + Bd.check_mark(x, y + 5 * s, 70 * s)
    if name == 'card':
        out = [R([(-70, -110), (70, -110), (70, 110), (-70, 110), (-70, -110)]), R([(-45, -85), (45, -85), (45, -30), (-45, -30), (-45, -85)])]
        for r in range(3):
            for k in range(3): out.append(C(-30 + k * 30, 5 + r * 30, 6, 8))
        return out
    if name == 'ad':
        return [R([(-90, -25), (-30, -25), (60, -80), (60, 80), (-30, 25), (-90, 25), (-90, -25)]), R([(-70, 25), (-55, 85), (-30, 85), (-40, 25)]),
                R([(85, -30), (115, -45)]), R([(85, 0), (120, 0)]), R([(85, 30), (115, 45)])]
    if name == 'bottle':
        return Bd.bottle(x, y - 110 * s, 230 * s, 4)
    if name == 'shoe':
        pts = [(612, 702), (905, 702), (916, 682), (884, 656), (805, 640), (765, 600), (700, 574), (642, 584), (616, 640), (612, 702)]
        sh = lambda P: [(x + (px - 764) * s, y + (py - 640) * s) for px, py in P]
        return [Bd.wob(sh(pts), 1.0, 4), sh([(612, 686), (912, 686)]), sh([(722, 603), (744, 618)]), sh([(742, 596), (764, 612)])]
    if name == 'audio':
        out = [Bd.wob(Bd.rrect_pts(x - 190 * s, y - 50 * s, x + 190 * s, y + 50 * s, 48 * s), 0.6, 2), R([(-160, -22), (-160, 22), (-125, 0), (-160, -22)])]
        for i in range(10):
            h = 10 + 26 * abs(math.sin(i * 1.7))
            out.append(R([(-95 + i * 22, -h), (-95 + i * 22, h)]))
        return out
    if name == 'cake':
        return [R([(-100, 20), (100, 20), (100, 100), (-100, 100), (-100, 20)]), R([(-75, -45), (75, -45), (75, 20), (-75, 20), (-75, -45)]),
                R([(0, -45), (0, -95)]), R([(0, -105), (-8, -118), (0, -132), (8, -118), (0, -105)]),
                R([(-100, 55), (-60, 70), (-20, 55), (20, 70), (60, 55), (100, 70)])]
    if name == 'photos':
        out = []
        for i, dx in enumerate((-150, 0, 150)):
            out.append(R([(dx - 65, -55), (dx + 65, -55), (dx + 65, 65), (dx - 65, 65), (dx - 65, -55)]))
            out += B.mini_fig(x + dx * s, y + 50 * s, 0.6 * s, 0.4 * (i % 2))
        return out
    if name == 'scribble':
        out = []
        for i in range(5):
            out.append([(x + (-200 + k * 10) * s, y + (-90 + i * 45) * s + 9 * math.sin(k * 0.9 + i)) for k in range(41 - (i % 2) * 8)])
        return out
    if name == 'return':
        return B.reset_arrow(x, y, 70 * s)
    if name == 'boxes':
        out = []
        for r in range(2):
            for k in range(5): out.append(Bd.rect(x + (-150 + k * 62) * s, y + (-60 + r * 70) * s, x + (-105 + k * 62) * s, y + (-15 + r * 70) * s, k + r))
        return out
    raise ValueError(name)


# ------------------------------------------------------------------ desenho de cada tipo de item
def text_lines(c, lines, x, y, size, color, p, fam='Comic Neue', maxw=800):
    n = len(lines)
    for i, ln in enumerate(lines):
        Bd.text(c, ln, x, y + (i - (n - 1) / 2) * size * 1.25 + size * 0.35, size, color, Bd.sub(p, i / n, (i + 1) / n), maxw=maxw, family=fam)


def draw_it(c, it, p):
    s = Bd.sub; k = it[0]
    if k == 't':
        _, x, y, txt, *o = it
        size = o[0] if len(o) > 0 else 56; col = o[1] if len(o) > 1 else INK; fam = 'Poppins' if (len(o) > 2 and o[2] == 'P') else 'Comic Neue'
        align = o[3] if len(o) > 3 else 'c'
        Bd.text(c, txt, x, y, size, col, p, align=align, family=fam, maxw=o[4] if len(o) > 4 else 880)
    elif k == 'bar':
        _, y, txt, *o = it
        size = o[0] if o else 68; col = o[1] if len(o) > 1 else INK
        size = Bd.fit(c, txt, size, 820, 'Poppins'); w = c.extents(txt).x_advance
        Bd.fill_rr(c, 540 - w / 2 - 40, y - size * 1.05, 540 + w / 2 + 40, y + size * 0.35, 14, YEL, 0.6 * s(p, 0, 0.4))
        Bd.text(c, txt, 540, y, size, col, s(p, 0.2, 1.0), family='Poppins', maxw=820)
    elif k == 'big':
        _, y, txt, *o = it
        col = o[0] if o else GREEN
        w = Bd.text(c, txt, 540, y, 72, col, s(p, 0, 0.75), family='Poppins', maxw=860) or 700
        Bd.draw_strokes(c, [Bd.wob([(540 - w / 2 - 20, y + 28), (540 + w / 2 + 20, y + 28)], 1.2, 2)], s(p, 0.6, 1.0), col, 6)
    elif k == 'strike':
        _, x, y, txt, *o = it
        size = o[0] if o else 52
        w = Bd.text(c, txt, x, y, size, INK, s(p, 0, 0.6), maxw=820) or 500
        Bd.draw_strokes(c, [Bd.wob([(x - w / 2 - 20, y - size * 0.32), (x + w / 2 + 20, y - size * 0.32)], 1.2, 4)], s(p, 0.55, 1.0), RED, 7)
    elif k == 'check':
        _, y, txt = it
        Bd.draw_strokes(c, [Bd.rect(118, y, 190, y + 70, 2)], s(p, 0, 0.35), INK, 6)
        Bd.text(c, txt, 222, y + 57, 60, INK, s(p, 0.2, 0.7), align='l', maxw=780)
        Bd.draw_strokes(c, Bd.check_mark(156, y + 35, 70), s(p, 0.65, 1.0), GREEN, 10)
    elif k == 'bub':
        _, x0, y0, x1, y1, txt, *o = it
        tail = o[0] if o else 'l'; fig = o[1] if len(o) > 1 else False; col = o[2] if len(o) > 2 else MARK
        size = o[3] if len(o) > 3 else 48
        if tail == 'r':
            tl = [(x1 - 60, y1 - 2), (x1 - 30, y1 + 46), (x1 - 110, y1 - 2)]; fx = x1 - 30
        else:
            tl = [(x0 + 60, y1 - 2), (x0 + 30, y1 + 46), (x0 + 110, y1 - 2)]; fx = x0 + 30
        Bd.draw_strokes(c, [Bd.wob(Bd.rrect_pts(x0, y0, x1, y1, 26), 0.6, 1), tl], s(p, 0, 0.45), INK, 5)
        if fig: Bd.draw_strokes(c, B.mini_fig(fx, y1 + 185, 1.05, 0.3), s(p, 0.2, 0.8), MARK, 5)
        text_lines(c, txt.split('\n'), (x0 + x1) / 2, (y0 + y1) / 2, size, col, s(p, 0.35, 1.0), maxw=x1 - x0 - 60)
    elif k == 'stamp':
        _, x, y, txt, *o = it
        Bd.stamp(c, txt, x, y, o[0] if o else -0.1, p, o[1] if len(o) > 1 else RED)
    elif k == 'follow':
        Bd.button(c, '+ SEGUIR', 540, 560, s(p, 0, 0.6))
        Bd.text(c, 'lição nova todo dia', 540, 775, 60, INK, s(p, 0.5, 1.0))
    elif k == 'x':
        _, x, y, sz = it
        Bd.draw_strokes(c, Bd.big_x(x, y, sz), p, RED, 10)
    elif k == 'ok':
        _, x, y, sz = it
        Bd.draw_strokes(c, Bd.check_mark(x, y, sz), p, GREEN, 11)
    elif k == 'arrow':
        _, x0, y0, x1, y1, *o = it
        Bd.draw_strokes(c, Bd.arrow(x0, y0, x1, y1, 22), p, o[0] if o else INK, 6)
    elif k == 'icon':
        _, name, x, y, *o = it
        sz = o[0] if o else 1.0; label = o[1] if len(o) > 1 else None; col = o[2] if len(o) > 2 else MARK
        ly = o[3] if len(o) > 3 else None; lsize = o[4] if len(o) > 4 else 46
        Bd.draw_strokes(c, icon_strokes(name, x, y, sz), s(p, 0, 0.75), col, 6)
        if label:
            if name in ('tag', 'coin'):
                Bd.text(c, label, x + (12 * sz if name == 'tag' else 0), y + 20 * sz, 52 * sz, INK, s(p, 0.5, 0.9), family='Poppins', maxw=190 * sz)
            else:
                Bd.text(c, label, x, ly if ly else y + 165 * sz, lsize, INK, s(p, 0.6, 1.0), maxw=420)


def anchor_of(it):
    k = it[0]
    if k in ('t', 'strike', 'stamp', 'x', 'ok'): return (it[1], it[2] - 20)
    if k in ('bar', 'big'): return (540, it[1] - 30)
    if k == 'check': return (155, it[1] + 35)
    if k == 'bub': return ((it[1] + it[3]) / 2, (it[2] + it[4]) / 2)
    if k == 'follow': return (540, 560)
    if k == 'arrow': return ((it[1] + it[3]) / 2, (it[2] + it[4]) / 2)
    if k == 'icon': return (it[2], it[3])
    return (540, 600)


# ------------------------------------------------------------------ lição
class Lesson:
    def __init__(self, S):
        self.S = S
        self.TXT = {'PT': None}
        self.HOOK = S.HOOK
        self.CUT_HOOKS = S.CUT_HOOKS
        self.block_of = {}
        for b, m in enumerate(S.MARKED):
            for key in re.findall(r'\{draw:([^}]+)\}', m): self.block_of[key] = b
        missing = [k for k in self.block_of if k not in S.ITEMS]
        assert not missing, f'itens sem desenho: {missing}'
        groups = getattr(S, 'GROUPS', [])
        self.slides = []   # lista de (primeiro_bloco, ultimo_bloco)
        b = 0
        while b < 9:
            g = next((gg for gg in groups if gg[0] == b), None)
            self.slides.append(g if g else (b, b)); b = (g[1] if g else b) + 1

    def build(self, lang, al):
        S = self.S
        pf = Perf(x0=540.0, sc=SC, floor=FLOOR_V, chunk_chars=18)
        pf.anchors.update({k: anchor_of(v) for k, v in S.ITEMS.items()})
        for i in range(9): pf.anchors[f'title{i}'] = (540, 270)
        pf.env = al.get('env')
        for b in range(9):
            ws = [w for w in al['words'] if w['block'] == b]
            pf.say_timed(S.MARKED[b], ws)
            t0 = ws[0]['t0']
            if b > 0 and any(sl[0] == b for sl in self.slides):
                pf.looks.append((t0 - 0.1, ('item', f'title{b}')))
                pf.looks.append((t0 + 0.55, 'cam'))
        pf.looks.sort(key=lambda x: x[0])
        return pf, simulate(pf, al['end'] + 1.3)

    def draw_board(self, c, pf, t, blocks):
        S = self.S
        c.save()
        c.color('#000000', 0.10); c.rrect(B.BX + 8, B.BY + 12, B.BW, B.BH, 22); c.fill()
        c.color('#FFFFFF'); c.rrect(B.BX, B.BY, B.BW, B.BH, 22); c.fill(True)
        c.color('#3A3A40'); c.lw(11); c.stroke()
        c.color('#3A3A40'); c.rrect(B.BX + 70, B.BY + B.BH + 7, B.BW - 140, 14, 6); c.fill()
        c.color(MARK); c.rrect(B.BX + 140, B.BY + B.BH - 3, 52, 11, 4); c.fill()
        c.color(RED); c.rrect(B.BX + 205, B.BY + B.BH - 3, 52, 11, 4); c.fill()
        c.restore()
        starts = [b[0] for b in blocks]
        for j, (b0, b1) in enumerate(self.slides):
            a = 0.0 if j == 0 else starts[b0] - 0.15
            bb = starts[b1 + 1] - 0.15 if b1 + 1 < len(starts) else 1e9
            alpha = (1.0 if j == 0 else sstep((t - a) / 0.25)) * (1 - sstep((t - bb) / 0.25))
            if alpha <= 0.001: continue
            c.push()
            Bd.text(c, S.TITLES[b0], 540, 298, 76, INK, sstep((t - a) / 0.5), maxw=900)
            for key, it in S.ITEMS.items():
                if b0 <= self.block_of.get(key, -1) <= b1 and key in pf.board:
                    draw_it(c, it, sstep((t - pf.board[key]) / (it_dur(it))))
            c.pop_paint(alpha)

    def render_frame(self, c, pf, poses, f, blocks, L, end):
        t = f / FPS
        cx, cy, z = B.cam_at(t, blocks)
        c.save(); c.translate(W / 2, H / 2 + 40); c.scale(z, z); c.translate(-cx, -cy)
        B.draw_bg(c)
        self.draw_board(c, pf, t, blocks)
        draw_character(c, poses[min(f, len(poses) - 1)])
        c.restore()
        c.radial(W / 2, H / 2, H * 0.45, H * 0.85, [(0, '#000000', 0.0), (1, '#000000', 0.10)])
        c.rect(0, 0, W, H); c.fill()
        B.draw_captions(c, pf, t)


# ------------------------------------------------------------------ final em loop
LOOP_DUR = 1.0   # segundos finais em que o vídeo volta ao primeiro frame (pose, câmera e gancho)


def loop_k(i, n, fps=FPS, loop_dur=LOOP_DUR):
    """Peso do primeiro frame no frame i de um corte com n frames: 0 até o último segundo,
    sobe suave e chega a 1 exatamente no último frame (i = n - 1)."""
    lf = max(1, int(round(loop_dur * fps)))
    return sstep((i - (n - 1 - lf)) / lf)


def loop_blend(cur, first, k):
    """Mistura o frame atual (HxWx4 uint8) com o primeiro frame do corte. k=1 devolve o primeiro frame."""
    import numpy as np
    if k <= 0: return cur
    if k >= 1: return first
    out = cur.astype(np.float32) * (1 - k) + first.astype(np.float32) * k
    return (out + 0.5).astype(np.uint8)


def it_dur(it):
    return DUR[it[0]]


def module_for(n):
    """Expõe a lição n com a mesma interface dos módulos lessonNN antigos (usada pelo cuts.py)."""
    S = importlib.import_module(f'spec{n}')
    Lz = Lesson(S)
    class M: pass
    m = M(); m.TXT = Lz.TXT; m.build = Lz.build; m.render_frame = Lz.render_frame
    m.HOOK = Lz.HOOK; m.CUT_HOOKS = Lz.CUT_HOOKS; m.S = S
    return m


if __name__ == '__main__':
    if sys.argv[1] == 'loop':
        import cuts
        n, cut, out = int(sys.argv[2]), sys.argv[3], sys.argv[4]
        cuts.loop_sheet(n, 'PT', cut, out)
    elif sys.argv[1] == 'stills':
        n = int(sys.argv[2]); out = sys.argv[3]; times = [float(x) for x in sys.argv[4].split(',')]
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        al = json.load(open(f'{root}/alinhamentos/al{n}_pt.json'))
        m = module_for(n); pf, poses = m.build('PT', al)
        from PIL import Image
        c = Canvas(W, H); ims = []
        for tt in times:
            f = min(len(poses) - 1, int(tt * FPS))
            m.render_frame(c, pf, poses, f, al['blocks'], None, al['end'])
            ims.append(Image.fromarray(c.rgb()).resize((270, 480)))
        cols = min(6, len(ims)); rows = (len(ims) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * 274, rows * 484), 'gray')
        for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * 274, (i // cols) * 484))
        sheet.save(out)

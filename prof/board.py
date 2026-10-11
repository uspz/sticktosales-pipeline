"""Elementos desenhados no quadro, com animacao de 'desenhar' (progresso 0..1)."""
import math

INK = '#1E1E22'; MARK = '#1F4E9C'; RED = '#D64541'; YEL = '#FFD21F'; GREEN = '#2E9E5B'; ORANGE = '#E39B00'


def clamp(x, a, b): return max(a, min(b, x))
def sstep(x): x = clamp(x, 0.0, 1.0); return x * x * (3 - 2 * x)
def sub(p, a, b): return clamp((p - a) / (b - a), 0.0, 1.0)


def wob(pts, amp=1.1, seed=0):
    return [(x + amp * math.sin(i * 1.7 + seed), y + amp * math.cos(i * 2.3 + seed * 0.7)) for i, (x, y) in enumerate(pts)]


def circle(cx, cy, r, a0=0.0, a1=2 * math.pi, n=30):
    return [(cx + r * math.cos(a0 + (a1 - a0) * i / n), cy + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)]


def rect(x0, y0, x1, y1, seed=0):
    return wob([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], 1.0, seed)


def rrect_pts(x0, y0, x1, y1, r, n=6):
    pts = []
    for (cx, cy, a0) in ((x1 - r, y0 + r, -math.pi / 2), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, math.pi / 2), (x0 + r, y0 + r, math.pi)):
        pts += circle(cx, cy, r, a0, a0 + math.pi / 2, n)
    pts.append(pts[0])
    return pts


def strokes_len(strokes):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for pts in strokes for a, b in zip(pts, pts[1:]))


def draw_strokes(c, strokes, prog, color=MARK, width=6.0, alpha=1.0):
    if prog <= 0: return
    total = strokes_len(strokes) * clamp(prog, 0, 1)
    c.color(color, alpha); c.lw(width)
    acc = 0.0
    for pts in strokes:
        c.new_path(); c.move(*pts[0])
        for a, b in zip(pts, pts[1:]):
            seg = math.hypot(b[0] - a[0], b[1] - a[1])
            if acc + seg <= total:
                c.line(*b); acc += seg
            else:
                k = (total - acc) / seg if seg else 0
                c.line(a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k); acc = total; break
        c.stroke()
        if acc >= total: break


def fit(c, txt, size, maxw, family='Comic Neue'):
    c.font(family, size, True)
    w = c.extents(txt).x_advance
    if w > maxw:
        size = size * maxw / w
        c.font(family, size, True)
    return size


def text(c, txt, x, y, size, color=INK, prog=1.0, align='c', maxw=880, family='Comic Neue', alpha=1.0):
    """texto de marcador revelado da esquerda para a direita."""
    if prog <= 0: return
    size = fit(c, txt, size, maxw, family)
    e = c.extents(txt)
    w = e.x_advance
    x0 = x - w / 2 if align == 'c' else (x - w if align == 'r' else x)
    c.save()
    c.rect(x0 - 6, y - size * 1.15, (w + 12) * clamp(prog, 0, 1), size * 1.6); c.clip()
    c.color(color, alpha); c.text(x0, y, txt)
    c.restore()
    return w


def fill_rr(c, x0, y0, x1, y1, r, color, alpha):
    if alpha <= 0: return
    c.color(color, alpha); c.rrect(x0, y0, x1 - x0, y1 - y0, r); c.fill()


# ------------------------------------------------------------------ desenhos prontos
def bottle(cx, top, h, seed=0):
    w = h * 0.30; nw = h * 0.085
    y_n = top + h * 0.24; y_s = top + h * 0.40; bot = top + h
    out = [cx - nw, top]
    left = [(cx - nw, top), (cx - nw, y_n)]
    left += [(cx - nw - (w - nw) * k, y_n + (y_s - y_n) * math.sin(k * math.pi / 2)) for k in [i / 6 for i in range(1, 7)]]
    left += [(cx - w, bot - 12), (cx - w + 12, bot)]
    right = [(2 * cx - x, y) for (x, y) in left]
    body = left + [(cx + w - 12, bot)] + right[::-1][1:]
    body = wob(body, 0.9, seed)
    cap = rect(cx - nw - 3, top - 18, cx + nw + 3, top, seed + 1)
    label = rect(cx - w + 14, top + h * 0.55, cx + w - 14, top + h * 0.80, seed + 2)
    return [cap, body, label]


def price_tag(x0, y0, x1, y1, seed=0):
    m = (y1 - y0) * 0.5
    pts = [(x0 + m * 0.7, y0), (x1, y0), (x1, y1), (x0 + m * 0.7, y1), (x0, y0 + m), (x0 + m * 0.7, y0)]
    return [wob(pts, 1.0, seed), circle(x0 + m * 0.62, y0 + m, 7, n=14)]


def anchor_icon(cx, cy, s):
    ring = circle(cx, cy - 1.0 * s, 0.22 * s, n=24)
    shaft = [(cx, cy - 0.78 * s), (cx, cy + 0.95 * s)]
    bar = [(cx - 0.45 * s, cy - 0.45 * s), (cx + 0.45 * s, cy - 0.45 * s)]
    arc = circle(cx, cy + 0.25 * s, 0.70 * s, math.radians(25), math.radians(155), 26)
    tl = [(arc[-1][0] - 0.16 * s, arc[-1][1] - 0.18 * s), arc[-1], (arc[-1][0] + 0.2 * s, arc[-1][1] - 0.05 * s)]
    tr = [(arc[0][0] + 0.16 * s, arc[0][1] - 0.18 * s), arc[0], (arc[0][0] - 0.2 * s, arc[0][1] - 0.05 * s)]
    return [ring, shaft, bar, arc, tl, tr]


def ruler(x0, x1, y, h=58, step=46):
    out = [rect(x0, y, x1, y + h, 5)]
    x = x0 + step
    k = 0
    while x < x1 - 6:
        out.append([(x, y), (x, y + (h * 0.45 if k % 2 == 0 else h * 0.28))]); x += step; k += 1
    return out


def double_arrow(x0, x1, y):
    a = 18
    return [[(x0, y), (x1, y)], [(x0 + a, y - a * 0.7), (x0, y), (x0 + a, y + a * 0.7)], [(x1 - a, y - a * 0.7), (x1, y), (x1 - a, y + a * 0.7)]]


def arrow(x0, y0, x1, y1, a=20):
    ang = math.atan2(y1 - y0, x1 - x0)
    return [[(x0, y0), (x1, y1)], [(x1 - a * math.cos(ang - 0.5), y1 - a * math.sin(ang - 0.5)), (x1, y1),
                                   (x1 - a * math.cos(ang + 0.5), y1 - a * math.sin(ang + 0.5))]]


def check_mark(x, y, s):
    return [[(x - 0.45 * s, y), (x - 0.12 * s, y + 0.35 * s), (x + 0.55 * s, y - 0.45 * s)]]


def big_x(cx, cy, s):
    return [[(cx - s, cy - s * 0.8), (cx + s, cy + s * 0.8)], [(cx + s, cy - s * 0.8), (cx - s, cy + s * 0.8)]]


def star(cx, cy, r):
    pts = []
    for i in range(11):
        rr = r if i % 2 == 0 else r * 0.45
        a = -math.pi / 2 + i * math.pi / 5
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return [pts]


def stamp(c, txt, cx, cy, ang, prog, color=RED):
    if prog <= 0: return
    k = sstep(prog)
    sc = 1.6 - 0.6 * k
    c.save(); c.translate(cx, cy); c.rotate(ang); c.scale(sc, sc)
    size = 46
    c.font('Poppins', size, True)
    w = c.extents(txt).x_advance
    c.color(color, k); c.lw(6); c.rrect(-w / 2 - 22, -size * 0.95, w + 44, size * 1.45, 12); c.stroke()
    c.text(-w / 2, size * 0.32, txt)
    c.restore()


def button(c, txt, cx, cy, prog):
    if prog <= 0: return
    k = sstep(prog)
    sc = 0.6 + 0.4 * k + 0.08 * math.sin(math.pi * k)
    c.save(); c.translate(cx, cy); c.scale(sc, sc)
    c.font('Poppins', 70, True)
    w = c.extents(txt).x_advance
    c.color(RED, k); c.rrect(-w / 2 - 50, -70, w + 100, 128, 64); c.fill()
    c.color('#FFFFFF', k); c.text(-w / 2, 22, txt)
    c.restore()

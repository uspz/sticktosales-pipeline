"""Boneco de palito com esqueleto: IK de bracos/pernas, maos com dedos, rosto expressivo."""
import math
from dataclasses import dataclass, field

INK = '#1E1E22'
HEAD_FILL = '#FFFFFF'
TONGUE = '#C8473F'

HEAD_R = 44.0
NECK = 9.0
TORSO = 172.0
SH_DROP = 24.0
UPPER = 92.0
FORE = 86.0
THIGH = 110.0
SHIN = 106.0
FOOT = 24.0
LW = 9.0
STAND_H = 211.0          # altura da pelve em pe (joelho levemente dobrado)

# formatos de mao: extensao dos dedos [indicador, medio, anelar, minimo], polegar, abertura, angulo do polegar
HANDS = {
    'relax':  dict(ext=[0.55, 0.5, 0.45, 0.4], th=0.55, spread=0.10, tha=0.75),
    'open':   dict(ext=[1.0, 1.0, 1.0, 0.92], th=1.0, spread=0.30, tha=0.95),
    'point':  dict(ext=[1.0, 0.12, 0.10, 0.10], th=0.45, spread=0.10, tha=0.70),
    'one':    dict(ext=[1.0, 0.10, 0.10, 0.10], th=0.20, spread=0.12, tha=0.55),
    'two':    dict(ext=[1.0, 1.0, 0.10, 0.10], th=0.20, spread=0.24, tha=0.55),
    'three':  dict(ext=[1.0, 1.0, 1.0, 0.10], th=0.20, spread=0.26, tha=0.55),
    'fist':   dict(ext=[0.08, 0.08, 0.08, 0.08], th=0.35, spread=0.05, tha=0.65),
    'lshape': dict(ext=[1.0, 0.10, 0.10, 0.10], th=1.0, spread=0.10, tha=1.55),
    'thumb':  dict(ext=[0.08, 0.08, 0.08, 0.08], th=1.0, spread=0.05, tha=1.45),
}


def hand_params(name):
    h = HANDS[name]
    return dict(ext=list(h['ext']), th=h['th'], spread=h['spread'], tha=h['tha'])


def lerp(a, b, k): return a + (b - a) * k


@dataclass
class Pose:
    px: float = 600.0
    py: float = 690.0
    lean: float = 0.0            # inclinacao da coluna (rad, + = topo para +x)
    bend: float = 0.0            # curvatura da coluna (px)
    shrug: float = 0.0           # ombros para cima (px)
    tilt: float = 0.0            # inclinacao da cabeca (rad)
    yaw: float = 0.0             # cabeca virada (-1..1)
    pitch: float = 0.0           # cabeca para baixo (+) / cima (-)
    eye_x: float = 0.0
    eye_y: float = 0.0
    blink: float = 0.0
    brow_raise: float = 0.0
    brow_furrow: float = 0.0
    mouth_w: float = 20.0
    mouth_h: float = 0.0
    smile: float = 0.4
    wA: tuple = (560.0, 700.0)   # punho do braco da esquerda da tela
    wB: tuple = (640.0, 700.0)   # punho do braco da direita da tela
    handA: dict = field(default_factory=lambda: dict(hand_params('relax'), ang=1.6, scale=1.0, fore=1.0))
    handB: dict = field(default_factory=lambda: dict(hand_params('relax'), ang=1.5, scale=1.0, fore=1.0))
    fA: tuple = (570.0, 900.0)   # tornozelo
    fB: tuple = (630.0, 900.0)
    toeA: float = math.pi
    toeB: float = 0.0
    kneeA: float = -1.0          # para que lado o joelho dobra
    kneeB: float = 1.0
    upA: float = 1.0             # encurtamento do braco (perspectiva: braco vindo pra camera)
    foA: float = 1.0
    upB: float = 1.0
    foB: float = 1.0
    ebA: tuple = (1.0, 0.35)     # preferencia do cotovelo (para baixo, para fora)
    ebB: tuple = (1.0, 0.35)
    sgA: float = None            # lado continuo do cotovelo (-1..1); None = escolhe pela preferencia
    sgB: float = None
    skA: float = None            # lado continuo do joelho
    skB: float = None
    sc: float = 1.0


def ik(root, target, l1, l2, score):
    dx, dy = target[0] - root[0], target[1] - root[1]
    d = math.hypot(dx, dy)
    base = math.atan2(dy, dx)
    d = max(abs(l1 - l2) + 1e-3, min(l1 + l2 - 1e-3, d))
    ca = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)
    a = math.acos(max(-1.0, min(1.0, ca)))
    j1 = (root[0] + l1 * math.cos(base + a), root[1] + l1 * math.sin(base + a))
    j2 = (root[0] + l1 * math.cos(base - a), root[1] + l1 * math.sin(base - a))
    end = (root[0] + d * math.cos(base), root[1] + d * math.sin(base))
    return (j1 if score(j1) >= score(j2) else j2), end


def ik_c(root, target, l1, l2, sigma):
    """IK continuo: sigma em [-1,1] gira o cotovelo em 3D (no meio fica apontando pra camera)."""
    dx, dy = target[0] - root[0], target[1] - root[1]
    d = math.hypot(dx, dy) or 1e-6
    ux, uy = dx / d, dy / d
    d = max(abs(l1 - l2) + 1e-3, min(l1 + l2 - 1e-3, d))
    x = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, l1 * l1 - x * x))
    px, py = -uy, ux
    J = (root[0] + ux * x + px * h * sigma, root[1] + uy * x + py * h * sigma)
    end = (root[0] + ux * d, root[1] + uy * d)
    return J, end


def pref_sign(root, target, l1, l2, score):
    """Qual lado (+1/-1) a preferencia escolhe, e a diferenca de pontuacao."""
    jp, _ = ik_c(root, target, l1, l2, 1.0)
    jm, _ = ik_c(root, target, l1, l2, -1.0)
    sp, sm = score(jp), score(jm)
    return (1.0 if sp >= sm else -1.0), abs(sp - sm)


def arm_score(S, side, eb):
    return lambda j: (j[1] - S[1]) * eb[0] + side * (j[0] - S[0]) * eb[1]


def leg_score(P, kd):
    return lambda j: kd * (j[0] - P[0]) - 0.15 * (j[1] - P[1])


def skeleton(p):
    s = p.sc
    P = (p.px, p.py)
    u = (math.sin(p.lean), -math.cos(p.lean))
    N = (P[0] + TORSO * s * u[0], P[1] + TORSO * s * u[1])
    S = (P[0] + (TORSO - SH_DROP) * s * u[0], P[1] + (TORSO - SH_DROP) * s * u[1] - p.shrug * s)
    ha = p.lean + p.tilt * 0.6
    H = (N[0] + (NECK + HEAD_R) * s * math.sin(ha), N[1] - (NECK + HEAD_R) * s * math.cos(ha))
    arms = {}
    for key, side in (('A', -1), ('B', 1)):
        W = getattr(p, 'w' + key)
        eb = getattr(p, 'eb' + key)
        l1 = UPPER * s * getattr(p, 'up' + key); l2 = FORE * s * getattr(p, 'fo' + key)
        sg = getattr(p, 'sg' + key)
        if sg is None: sg, _ = pref_sign(S, W, l1, l2, arm_score(S, side, eb))
        arms[key] = ik_c(S, W, l1, l2, sg)
    legs = {}
    for key in ('A', 'B'):
        F = getattr(p, 'f' + key); kd = getattr(p, 'knee' + key)
        sk = getattr(p, 'sk' + key)
        if sk is None: sk, _ = pref_sign(P, F, THIGH * s, SHIN * s, leg_score(P, kd))
        legs[key] = ik_c(P, F, THIGH * s, SHIN * s, sk)
    return dict(P=P, N=N, S=S, H=H, arms=arms, legs=legs)


def _dir(a): return (math.cos(a), math.sin(a))


def draw_hand(c, W, h, side, s, ink=INK):
    """Mao no punho W. h: ext, th, spread, tha, ang, scale, fore."""
    a = h['ang']; sc = s * h.get('scale', 1.0); fore = h.get('fore', 1.0)
    ux, uy = _dir(a); vx, vy = -uy, ux            # eixo da mao e perpendicular
    tside = -side
    c.color(ink)
    # palma
    pl = 11 * sc * (0.75 + 0.25 * fore)
    c.lw(12.5 * sc); c.new_path(); c.move(*W); c.line(W[0] + ux * pl, W[1] + uy * pl); c.stroke()
    base = (W[0] + ux * pl, W[1] + uy * pl)
    lens = [0.95, 1.0, 0.93, 0.78]
    c.lw(5.2 * sc)
    for i in range(4):
        e = max(0.0, min(1.0, h['ext'][i]))
        off = (i - 1.5) * 3.3 * sc * (1 + h['spread'])
        bx, by = base[0] + vx * off * tside, base[1] + vy * off * tside
        fa = a + (i - 1.5) * h['spread'] * tside * 0.9
        L = (6.0 + 15.0 * lens[i]) * sc * (fore if i == 0 else 1.0)
        curl = 1.0 - e
        L1 = L * (0.55 - 0.15 * curl)
        mx, my = bx + math.cos(fa) * L1, by + math.sin(fa) * L1
        fa2 = fa + tside * curl * 1.9
        L2 = L * (0.5 - 0.22 * curl)
        tx, ty = mx + math.cos(fa2) * L2, my + math.sin(fa2) * L2
        c.new_path(); c.smooth([(bx, by), (mx, my), (tx, ty)], 0.5); c.stroke()
        if i == 0 and fore < 0.8:   # indicador apontando para a camera: ponta destacada
            c.arc(tx, ty, 4.4 * sc); c.fill()
    # polegar
    ta = a + tside * h['tha']
    tb = (W[0] + ux * 3 * sc + vx * tside * 5.5 * sc, W[1] + uy * 3 * sc + vy * tside * 5.5 * sc)
    tl = (5 + 11 * h['th']) * sc
    c.lw(5.6 * sc); c.new_path(); c.move(*tb); c.line(tb[0] + math.cos(ta) * tl, tb[1] + math.sin(ta) * tl); c.stroke()


def draw_face(c, p, H):
    s = p.sc
    c.save()
    c.translate(H[0], H[1]); c.rotate(p.lean + p.tilt)
    yaw = max(-1.0, min(1.0, p.yaw))
    fx = yaw * HEAD_R * 0.36 * s
    fy = p.pitch * HEAD_R * 0.20 * s
    sp = 16.0 * s * (1 - 0.16 * abs(yaw))
    c.color(INK)
    # olhos
    ey = -6 * s + fy
    for side in (-1, 1):
        far = 1 - 0.18 * max(0.0, side * -yaw)    # olho do lado oposto ao giro fica menor
        cx = fx + side * sp + p.eye_x * 3.6 * s
        cy = ey + p.eye_y * 3.0 * s
        ry = 9.2 * s * (1 - p.blink) * far
        rx = 6.3 * s * far
        if ry < 1.8 * s:
            c.lw(4.2 * s); c.new_path(); c.move(cx - rx - 1, cy); c.curve(cx - 2, cy + 3 * s, cx + 2, cy + 3 * s, cx + rx + 1, cy); c.stroke()
        else:
            c.save(); c.translate(cx, cy); c.scale(rx / ry, 1.0); c.arc(0, 0, ry); c.restore(); c.fill()
            # brilho
            c.color('#FFFFFF'); c.arc(cx + rx * 0.35, cy - ry * 0.4, 1.7 * s); c.fill(); c.color(INK)
    # sobrancelhas
    by = -6 * s + fy - 19 * s - p.brow_raise * 6.5 * s
    c.lw(4.4 * s)
    for side in (-1, 1):
        inner = fx + side * (sp - 7.5 * s); outer = fx + side * (sp + 9.5 * s)
        iy = by + p.brow_furrow * 5.0 * s; oy = by - p.brow_furrow * 1.5 * s
        c.new_path(); c.move(inner, iy)
        c.curve(inner + side * 5 * s, iy - 3.5 * s, outer - side * 5 * s, oy - 3.5 * s, outer, oy); c.stroke()
    # boca
    mx = fx * 1.06; my = 22 * s + fy * 1.25
    w = p.mouth_w * s * (1 - 0.12 * abs(yaw)); h = p.mouth_h * s; sm = p.smile
    if h < 1.6 * s:
        c.lw(4.4 * s); c.new_path()
        c.move(mx - w / 2, my - sm * 3 * s)
        c.curve(mx - w / 4, my + sm * 6 * s, mx + w / 4, my + sm * 6 * s, mx + w / 2, my - sm * 3 * s)
        c.stroke()
    else:
        cy0 = my - sm * 2.5 * s
        c.new_path(); c.move(mx - w / 2, cy0)
        c.curve(mx - w / 4, cy0 - h * 0.22 - sm * 1.5 * s, mx + w / 4, cy0 - h * 0.22 - sm * 1.5 * s, mx + w / 2, cy0)
        c.curve(mx + w / 3, cy0 + h * 1.18, mx - w / 3, cy0 + h * 1.18, mx - w / 2, cy0)
        c.close()
        c.fill(True)
        if h > 9 * s:   # lingua
            c.save(); c.clip()
            c.color(TONGUE); c.save(); c.translate(mx, cy0 + h * 0.86); c.scale(1.0, 0.55); c.arc(0, 0, w * 0.3); c.restore(); c.fill()
            c.restore(); c.color(INK)
        c.new_path()
    c.restore()


def draw_character(c, p, shadow=True):
    s = p.sc
    sk = skeleton(p)
    P, N, S, H = sk['P'], sk['N'], sk['S'], sk['H']
    if shadow:
        gy = max(p.fA[1], p.fB[1]) + 6 * s
        cx = (p.fA[0] + p.fB[0]) / 2
        c.save(); c.translate(cx, gy); c.scale(1.0, 0.16)
        c.radial(0, 0, 0, 115 * s, [(0, '#000000', 0.16), (1, '#000000', 0.0)])
        c.arc(0, 0, 115 * s); c.fill(); c.restore()
    c.color(INK)
    # pernas
    for key in ('A', 'B'):
        K, F = sk['legs'][key]
        toe = getattr(p, 'toe' + key)
        c.lw(LW * s); c.new_path(); c.smooth([P, K, F], 0.35); c.stroke()
        hx, hy = F[0] - math.cos(toe) * 5 * s, F[1] - math.sin(toe) * 5 * s
        c.lw(LW * s); c.new_path(); c.move(hx, hy); c.line(F[0] + math.cos(toe) * FOOT * s, F[1] + math.sin(toe) * FOOT * s); c.stroke()
    # tronco (curva suave)
    mid = ((P[0] + N[0]) / 2, (P[1] + N[1]) / 2)
    nx, ny = -(N[1] - P[1]), (N[0] - P[0]); nl = math.hypot(nx, ny) or 1
    ctrl = (mid[0] + nx / nl * p.bend * s, mid[1] + ny / nl * p.bend * s)
    c.lw(LW * s); c.new_path(); c.move(*P)
    c.curve(P[0] + (ctrl[0] - P[0]) * 0.66, P[1] + (ctrl[1] - P[1]) * 0.66,
            N[0] + (ctrl[0] - N[0]) * 0.66, N[1] + (ctrl[1] - N[1]) * 0.66, N[0], N[1]); c.stroke()
    # cabeca
    c.arc(H[0], H[1], HEAD_R * s); c.color(HEAD_FILL); c.fill(True); c.color(INK); c.lw(8 * s); c.stroke()
    # cabelo (tres riscos, identidade do personagem)
    c.save(); c.translate(H[0], H[1]); c.rotate(p.lean + p.tilt)
    hxo = p.yaw * 7 * s
    c.lw(6.5 * s)
    for dx in (-17, 0, 17):
        x0 = hxo + dx * s - 6 * s; y0 = -HEAD_R * s + 2 * s
        c.new_path(); c.move(x0, y0); c.line(x0 + 7 * s, y0 - 21 * s); c.stroke()
    c.restore()
    draw_face(c, p, H)
    # bracos por cima
    for key, side in (('A', -1), ('B', 1)):
        E, W = sk['arms'][key]
        c.color(INK); c.lw(LW * s); c.new_path(); c.smooth([S, E, W], 0.4); c.stroke()
        h = getattr(p, 'hand' + key)
        if h.get('prop', 0) > 0.02:
            draw_phone(c, W, h, side, s)
        draw_hand(c, W, h, side, s)
    return sk


def draw_phone(c, W, h, side, s):
    """Celular segurado na mao (aparece/desaparece com h['prop'])."""
    k = h['prop']
    a = h['ang']
    c.save()
    c.translate(W[0] + math.cos(a) * 16 * s, W[1] + math.sin(a) * 16 * s)
    c.rotate(a + math.pi / 2)
    c.scale(k * s * 1.3, k * s * 1.3)
    c.color(INK); c.rrect(-17, -30, 34, 58, 7); c.fill()
    c.color('#7FB3F5'); c.rrect(-13, -25, 26, 46, 4); c.fill()
    c.color('#FFFFFF', 0.85); c.rrect(-9, -20, 18, 10, 2); c.fill()
    c.rrect(-9, -6, 18, 3.5, 1.5); c.fill(); c.rrect(-9, 0, 12, 3.5, 1.5); c.fill()
    c.restore()

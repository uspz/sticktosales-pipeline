"""Sistema de atuacao: fala (visemas), gestos ligados as palavras, olhar, caminhada com pe plantado,
respiracao, troca de peso, piscadas. Tudo simulado com molas para ficar fluido."""
import math, random, re
from rig2 import Pose, skeleton, hand_params, HANDS, STAND_H, UPPER, FORE, THIGH, SHIN, pref_sign, arm_score, leg_score

FPS = 30
FLOOR = 900.0
PI = math.pi


def clamp(x, a, b): return max(a, min(b, x))
def sstep(x): x = clamp(x, 0.0, 1.0); return x * x * (3 - 2 * x)
def lerp(a, b, k): return a + (b - a) * k


def near_ang(a, ref):
    while a - ref > PI: a -= 2 * PI
    while a - ref < -PI: a += 2 * PI
    return a


# ---------------------------------------------------------------- fala
VOW = {**{c: 'A' for c in 'aáàâã'}, **{c: 'E' for c in 'eéê'}, **{c: 'I' for c in 'iíy'},
       **{c: 'O' for c in 'oóôõ'}, **{c: 'U' for c in 'uúü'}}
VIS = {'A': (26, 19), 'E': (28, 10), 'I': (25, 6), 'O': (16, 16), 'U': (12, 10),
       'MBP': (17, 0), 'FV': (22, 2.5), 'C': (22, 6.5), 'rest': (20, 0)}


def word_units(word):
    w = ''.join(ch for ch in word.lower() if ch.isalpha())
    units = []
    i = 0
    while i < len(w):
        ch = w[i]
        if ch in VOW:
            j = i
            while j < len(w) and w[j] in VOW: j += 1
            units.append((VOW[ch], 1.0)); i = j
        else:
            j = i
            while j < len(w) and w[j] not in VOW: j += 1
            v = 'MBP' if ch in 'mbp' else ('FV' if ch in 'fv' else 'C')
            units.append((v, 0.55)); i = j
    return units or [('C', 1.0)]


def word_dur(word, stress=False):
    n = sum(1 for ch in word if ch.isalpha())
    return 0.11 + 0.056 * n + (0.06 if stress else 0.0)


# ---------------------------------------------------------------- poses de gesto (relativas ao ombro)
def gesture_target(kind, side, t=0.0, ts=0.0, extra=None):
    """Retorna alvo do punho (dx,dy), mao, angulo, encurtamentos e preferencia do cotovelo."""
    s = side
    out = dict(up=1.0, fo=1.0, eb=(1.0, 0.35), scale=1.0, fore=1.0, prop=0.0)
    if kind == 'clasp':
        out.update(pos=(-s * 8, 126), hand='relax', ang=(0.25 if s < 0 else PI - 0.25), up=0.94, fo=0.63, eb=(0.2, 1.0))
    elif kind == 'hang':
        out.update(pos=(s * 40, 168), hand='relax', ang=PI / 2 - s * 0.12)
    elif kind == 'beat':
        out.update(pos=(s * 58, 112), hand='relax', ang=PI / 2 - s * 0.6, up=0.96, fo=0.72)
    elif kind == 'you':
        out.update(pos=(s * 84, 62), hand='open', ang=(-0.3 if s > 0 else PI + 0.3), up=0.93, fo=0.78)
    elif kind == 'phone_hold':     # segura o celular na frente do peito (braco s)
        out.update(pos=(s * 20, 34), hand='fist', ang=(-1.25 if s < 0 else -1.89), up=0.82, fo=0.55, eb=(0.4, 1.0), prop=1.0)
    elif kind == 'phone_scroll':   # o outro dedo rola a tela
        ph = math.sin(2 * PI * 1.8 * (t - ts))
        out.update(pos=(s * -4, 30 + 9 * ph), hand='point', ang=(PI + 0.6 if s > 0 else -0.6), up=0.82, fo=0.55, eb=(0.4, 1.0))
    elif kind == 'present':
        out.update(pos=(s * 130, 52), hand='open', ang=(-0.38 if s > 0 else PI + 0.38))
    elif kind == 'present_hi':
        out.update(pos=(s * 140, -8), hand='open', ang=(-0.65 if s > 0 else PI + 0.65))
    elif kind in ('count1', 'count2', 'count3'):
        hand = {'count1': 'one', 'count2': 'two', 'count3': 'three'}[kind]
        out.update(pos=(s * 92, -14), hand=hand, ang=-PI / 2 + s * 0.22)
    elif kind == 'shrug':
        out.update(pos=(s * 96, 68), hand='open', ang=(-0.55 if s > 0 else PI + 0.55), up=0.95, fo=0.71)
    elif kind == 'negate':
        k = sstep((t - ts) / 0.38)
        out.update(pos=(s * lerp(18, 142, k), lerp(90, 98, k)), hand='open', ang=(0.06 if s > 0 else PI - 0.06), up=0.97, fo=0.9)
    elif kind == 'small':
        out.update(pos=(s * 38, 80), hand='open', ang=-PI / 2 + s * 0.35, up=0.95, fo=0.62)
    elif kind == 'wide':
        out.update(pos=(s * 168, 22), hand='open', ang=(-0.3 if s > 0 else PI + 0.3))
    elif kind == 'chest':
        out.update(pos=(-s * 8, 62), hand='open', ang=(PI + 0.25 if s > 0 else -0.25), up=0.9, fo=0.62, eb=(0.3, 1.0))
    elif kind == 'wave':
        ph = 2 * PI * 2.3 * (t - ts)
        env = sstep((t - ts + 0.15) / 0.3)
        out.update(pos=(s * 86 + 11 * math.sin(ph) * env, -104), hand='open', ang=-PI / 2 + s * 0.22 + 0.38 * math.sin(ph) * env)
    elif kind == 'point':     # alvo no mundo: extra = (dx,dy) do ombro ate o alvo
        dx, dy = extra
        d = math.hypot(dx, dy) or 1.0
        reach = min(UPPER + FORE - 6, max(60.0, d - 30))
        out.update(pos=(dx / d * reach, dy / d * reach), hand='point', ang=math.atan2(dy, dx), eb=(1.0, 0.2))
    else:
        raise ValueError(kind)
    return out


# ---------------------------------------------------------------- caminhada
class Walk:
    def __init__(self, t0, x0, x1, v=300.0, step=128.0, acc=0.42, dec=0.5, stance=28.0, floor=FLOOR, sc=1.0):
        self.floor, self.sc = floor, sc
        step *= sc; stance *= sc
        self.t0, self.x0, self.x1 = t0, x0, x1
        self.dir = 1.0 if x1 >= x0 else -1.0
        self.dist = abs(x1 - x0)
        if self.dist < v * (acc + dec) / 2:
            v = self.dist / ((acc + dec) / 2)
        self.v, self.acc, self.dec = v, acc, dec
        self.T = self.dist / v + (acc + dec) / 2
        self.n = max(2, round(self.dist / step))
        self.L = self.dist / self.n
        self.stance = stance
        self.settle = 0.32
        self.t_end = t0 + self.T + self.settle

    def traveled(self, t):
        u = t - self.t0
        if u <= 0: return 0.0
        v, a, d, T = self.v, self.acc, self.dec, self.T
        if u < a: return 0.5 * v / a * u * u
        cruise_end = T - d
        if u < cruise_end: return 0.5 * v * a + v * (u - a)
        if u < T:
            w = T - u
            return self.dist - 0.5 * v / d * w * w
        return self.dist

    def speed(self, t):
        u = t - self.t0
        if u <= 0 or u >= self.T: return 0.0
        if u < self.acc: return self.v * u / self.acc
        if u > self.T - self.dec: return self.v * (self.T - u) / self.dec
        return self.v

    def plants(self):
        """Posicoes de apoio de cada pe ao longo da caminhada."""
        dr, x0, L, n, st = self.dir, self.x0, self.L, self.n, self.stance
        back, front = x0 - dr * st, x0 + dr * st
        feet = [back, front]          # pe 0 comeca atras
        seq = []                      # (passo k, pe que se move, de, para)
        for k in range(1, n + 1):
            f = (k - 1) % 2
            dest = x0 + dr * (k * L + L / 2) if k < n else self.x1 + dr * st
            seq.append((k, f, feet[f], dest))
            feet[f] = dest
        return seq, feet

    def state(self, t):
        """pelve x, offset y, pes [(x,y,toe)], fase, peso da caminhada"""
        dr = self.dir
        d = self.traveled(t)
        phi = d / self.L
        seq, final_feet = self.plants()
        pos = [self.x0 - dr * self.stance, self.x0 + dr * self.stance]
        lift = [0.0, 0.0]; toe = [0.0, 0.0]
        for (k, f, a, b) in seq:
            if phi >= k:
                pos[f] = b
            elif phi > k - 1:
                u = phi - (k - 1)
                s = clamp((u - 0.06) / 0.94, 0.0, 1.0)
                e = s * s * (3 - 2 * s)
                pos[f] = a + (b - a) * e
                lift[f] = 30.0 * self.sc * math.sin(PI * s) ** 0.85 * min(1.0, abs(b - a) / (110.0 * self.sc))
                toe[f] = 0.42 * (1 - s) * math.sin(PI * min(1, s * 2.2)) - 0.30 * math.sin(PI * clamp((s - 0.55) / 0.45, 0, 1))
                break
        # assentamento final: pe de tras vem para a posicao de base
        ts = self.t0 + self.T
        if t > ts:
            k = sstep((t - ts) / self.settle)
            last_f = (self.n - 1) % 2
            other = 1 - last_f
            target = self.x1 - dr * self.stance
            src = final_feet[other]
            pos[other] = src + (target - src) * k
            lift[other] = 10.0 * math.sin(PI * k) * min(1.0, abs(target - src) / 30)
        px = self.x0 + dr * d
        w = clamp(self.speed(t) / self.v, 0.0, 1.0)
        frac = phi - math.floor(phi)
        bob = -8.5 * self.sc * math.sin(PI * frac) ** 2 * w
        feet = [(pos[i], self.floor - lift[i], toe[i]) for i in range(2)]
        return px, bob, feet, phi, w


# ---------------------------------------------------------------- atuacao
class Perf:
    def __init__(self, x0=-170.0, seed=7, sc=1.0, floor=FLOOR, chunk_chars=36):
        self.sc, self.floor, self.chunk_chars = sc, floor, chunk_chars
        self.env = None
        self.t = 0.0
        self.x_start = x0
        self.words = []; self.chunks = []
        self.gest = []            # dict(kind, arms, tp, ts, te, extra)
        self.impulses = []        # (t, arm, vx, vy)
        self.looks = [(0.0, 'walk')]
        self.walks = []
        self.emos = [(0.0, 0.45, 0.0, 0.0)]   # (t, smile, raise, furrow)
        self.nods = []; self.shakes = []; self.tilts = []; self.brow_imp = []
        self.shrugs = []
        self.board = {}           # item -> t0
        self.anchors = {}         # item -> (x,y) no mundo
        self.cam = [(0.0, 960.0, 540.0, 1.0)]
        self.rnd = random.Random(seed)
        self.sent = 0

    # --- comandos ---
    def wait(self, d): self.t += d
    def look(self, t, target): self.looks.append((t, target))
    def emotion(self, t, smile=None, raise_=None, furrow=None):
        last = self.emos[-1]
        self.emos.append((t, last[1] if smile is None else smile, last[2] if raise_ is None else raise_,
                          last[3] if furrow is None else furrow))
    def camera(self, t, cx, cy, z): self.cam.append((t, cx, cy, z))
    def gesture(self, kind, arms, ts, te, prep=0.3, extra=None):
        self.gest.append(dict(kind=kind, arms=arms, tp=ts - prep, ts=ts, te=te, extra=extra))
    def walk(self, x1, t0=None, v=300.0):
        t0 = self.t if t0 is None else t0
        x0 = self.walks[-1].x1 if self.walks else self.x_start
        w = Walk(t0, x0, x1, v=v * self.sc, floor=self.floor, sc=self.sc)
        self.walks.append(w)
        return w

    def say(self, text, rate=1.0):
        toks = re.findall(r'\{[^}]*\}|[^\s{}]+', text)
        pending = []
        sent_words = []
        for tok in toks:
            if tok.startswith('{'):
                pending.append(tok[1:-1]); continue
            stress = tok.startswith('*')
            disp = tok.lstrip('*')
            t0 = self.t
            d = word_dur(disp, stress) / rate
            t1 = t0 + d
            punct = disp[-1] if disp[-1] in ',.?!;:' else ''
            wd = dict(text=disp, t0=t0, t1=t1, stress=stress, punct=punct, sent=self.sent, marks=pending)
            self.words.append(wd); sent_words.append(wd)
            pending = []
            self.t = t1 + 0.07
            if punct and punct in ',;:': self.t += 0.22
            elif punct and punct in '.!': self.t += 0.42
            elif punct == '?': self.t += 0.52
        self._process(sent_words)
        self.sent += 1
        return sent_words

    def _process(self, sent_words):
        # marcas -> eventos
        for i, wd in enumerate(sent_words):
            clause_end = sent_words[-1]['t1'] + 0.3
            for j in range(i, len(sent_words)):
                if sent_words[j]['punct']:
                    clause_end = sent_words[j]['t1'] + 0.3; break
            sent_end = sent_words[-1]['t1'] + 0.35
            tw = wd['t0']
            for m in wd['marks']:
                self._mark(m, tw, clause_end, sent_end)
            if wd['stress']:
                self.nods.append((tw + 0.04, 0.9))
                self.brow_imp.append((tw, 0.6))
                self.impulses.append((tw + 0.03, 'B', 0.0, 430.0))
            elif len(wd['text']) >= 7 and i % 2 == 0:
                self.impulses.append((tw + 0.03, 'B', 0.0, 190.0))
        if sent_words and sent_words[-1]['punct'] == '?':
            self.brow_imp.append((sent_words[-1]['t0'] - 0.2, 0.9))
            self.tilts.append((sent_words[-1]['t0'] - 0.3, sent_words[-1]['t1'] + 0.5, 0.11))
        # legendas em blocos: por oracao, no maximo 6 palavras
        clause = []
        clauses = []
        for wd in sent_words:
            clause.append(wd)
            if wd['punct']: clauses.append(clause); clause = []
        if clause: clauses.append(clause)
        for cl in clauses:
            txt = ' '.join(w['text'] for w in cl)
            parts = max(1, math.ceil(len(txt) / self.chunk_chars))
            target = len(txt) / parts
            cur = []; ln = 0
            for w in cl:
                if cur and ln + len(w['text']) > target + 6 and len(self.chunks) >= 0:
                    self.chunks.append(cur); cur = []; ln = 0
                cur.append(w); ln += len(w['text']) + 1
            if cur: self.chunks.append(cur)

    def say_timed(self, marked, timed):
        """Texto com marcas + palavras com tempos vindos do audio (mesma ordem)."""
        toks = re.findall(r'\{[^}]*\}|[^\s{}]+', marked)
        pending = []; k = 0; allw = []
        for tok in toks:
            if tok.startswith('{'):
                pending.append(tok[1:-1]); continue
            stress = tok.startswith('*'); disp = tok.lstrip('*')
            tw = timed[k]; k += 1
            if disp != tw['text']:
                raise ValueError(f'palavra diferente: {disp!r} x {tw["text"]!r}')
            punct = disp[-1] if disp[-1] in ',.?!;:' else ''
            wd = dict(text=disp, t0=tw['t0'], t1=tw['t1'], stress=stress, punct=punct, sent=tw['sent'], marks=pending, block=tw['block'])
            pending = []; allw.append(wd); self.words.append(wd)
        assert k == len(timed), (k, len(timed))
        by = {}
        for wd in allw: by.setdefault(wd['sent'], []).append(wd)
        for sid in sorted(by): self._process(by[sid])
        self.t = allw[-1]['t1'] + 0.3

    def _mark(self, m, tw, clause_end, sent_end):
        name, _, arg = m.partition(':')
        if name == 'you':
            self.gesture('you', arg or 'B', tw, tw + 1.0); self.brow_imp.append((tw, 0.5))
        elif name == 'wave':
            self.gesture('wave', arg or 'B', tw, tw + 1.5, prep=0.3)
            self.emotion(tw, smile=1.0)
        elif name == 'phone':
            self.gesture('phone_hold', 'A', tw, clause_end, prep=0.32)
            self.gesture('phone_scroll', 'B', tw + 0.12, clause_end, prep=0.32)
            self.looks.append((tw, ('item', 'phone')))
            self.looks.append((clause_end - 0.55, 'cam'))
        elif name in ('count1', 'count2', 'count3'):
            self.gesture(name, 'A', tw, sent_end, prep=0.28)
            self.impulses.append((tw + 0.02, 'A', 0.0, -260.0))
        elif name == 'present':
            self.gesture('present', 'B', tw, clause_end)
        elif name == 'present_hi':
            self.gesture('present_hi', 'B', tw, clause_end)
        elif name == 'point':
            te = clause_end if not arg.endswith('!') else tw + 1.0
            self.gesture('point', 'B', tw, te, extra=arg.rstrip('!'))
            self.looks.append((tw - 0.15, ('item', arg.rstrip('!'))))
        elif name == 'shrug':
            self.gesture('shrug', 'AB', tw, tw + 1.1); self.shrugs.append((tw, tw + 1.1))
            self.brow_imp.append((tw, 0.9)); self.tilts.append((tw, tw + 1.1, 0.12))
        elif name == 'neg':
            self.gesture('negate', arg or 'A', tw, tw + 0.85, prep=0.22)
            self.shakes.append((tw, 0.75, 0.32))
        elif name == 'shake':
            self.shakes.append((tw, 0.7, float(arg) if arg else 0.28))
        elif name == 'nod':
            self.nods.append((tw, float(arg) if arg else 1.0))
        elif name == 'small':
            self.gesture('small', 'AB', tw, clause_end)
        elif name == 'wide':
            self.gesture('wide', 'AB', tw, tw + 1.4, prep=0.32)
            self.brow_imp.append((tw, 0.8))
        elif name == 'chest':
            self.gesture('chest', 'B', tw, clause_end)
        elif name == 'look':
            if arg == 'cam': self.looks.append((tw, 'cam'))
            else:
                self.looks.append((tw - 0.1, ('item', arg)))
                self.looks.append((tw + 1.15, 'cam'))
        elif name == 'draw':
            self.board[arg] = tw
        elif name == 'smile':
            self.emotion(tw, smile=float(arg))
        elif name == 'serious':
            self.emotion(tw, smile=0.05, furrow=0.35)
        elif name == 'calm':
            self.emotion(tw, smile=0.45, furrow=0.0)
        elif name == 'brow':
            self.brow_imp.append((tw, float(arg) if arg else 0.7))
        elif name == 'walk':
            self.walk(float(arg), t0=tw)
        elif name == 'cam':
            cx, cy, z = (float(v) for v in arg.split(','))
            self.camera(tw, cx, cy, z)
        else:
            raise ValueError('marca desconhecida: ' + m)

    # --- consultas no tempo ---
    def walk_at(self, t):
        cur = None
        for w in self.walks:
            if t >= w.t0: cur = w
        return cur

    def speaking(self, t):
        for wd in self.words:
            if wd['t0'] - 0.05 <= t <= wd['t1'] + 0.35: return True
        return False

    def in_sentence(self, t):
        by = {}
        for wd in self.words:
            a, b = by.get(wd['sent'], (1e9, -1e9))
            by[wd['sent']] = (min(a, wd['t0']), max(b, wd['t1']))
        return any(a - 0.25 <= t <= b + 0.45 for a, b in by.values())

    def emotion_at(self, t):
        cur = self.emos[0]
        for e in self.emos:
            if t >= e[0]: cur = e
        return cur

    def look_at(self, t):
        cur = self.looks[0][1]
        for (tt, tg) in sorted(self.looks, key=lambda x: x[0]):
            if t >= tt: cur = tg
        return cur

    def active_gesture(self, arm, t):
        best = None
        for g in self.gest:
            if arm in g['arms'] and g['tp'] <= t < g['te']:
                if best is None or g['tp'] >= best['tp']: best = g
        return best

    def mouth_target(self, t):
        for wd in self.words:
            if wd['t0'] <= t < wd['t1']:
                units = word_units(wd['text'])
                tot = sum(u[1] for u in units)
                acc = wd['t0']; d = wd['t1'] - wd['t0']
                for v, wgt in units:
                    seg = d * wgt / tot
                    if t < acc + seg: return VIS[v], True
                    acc += seg
                return VIS[units[-1][0]], True
        return VIS['rest'], False

    def end_time(self):
        te = self.t
        for w in self.walks: te = max(te, w.t_end)
        return te


# ---------------------------------------------------------------- simulacao
class Spring:
    def __init__(self, x, w, z):
        self.x, self.v, self.w, self.z = x, 0.0, w, z
    def step(self, target, dt, w=None, z=None):
        w = self.w if w is None else w; z = self.z if z is None else z
        n = 4; h = dt / n
        for _ in range(n):
            a = w * w * (target - self.x) - 2 * z * w * self.v
            self.v += a * h; self.x += self.v * h
        return self.x


def simulate(perf, duration, fps=FPS):
    rnd = random.Random(3)
    sc = perf.sc; floor = perf.floor
    dt = 1.0 / fps
    N = int(duration * fps)
    TW = 2 * PI
    # estado das molas
    arm = {}
    for key, side in (('A', -1), ('B', 1)):
        g = gesture_target('hang', side)
        arm[key] = dict(x=Spring(g['pos'][0] * sc, TW * 1.9, 0.72), y=Spring(g['pos'][1] * sc, TW * 1.9, 0.72),
                        ang=Spring(g['ang'], TW * 2.6, 0.58), shape=hand_params('relax'),
                        up=1.0, fo=1.0, eb=(1.0, 0.35), scale=1.0, fore=1.0, side=side, prop=0.0)
    yaw = Spring(0.0, TW * 1.6, 0.85); pitch = Spring(0.0, TW * 2.4, 0.5)
    tilt = Spring(0.0, TW * 1.2, 0.8)
    ex = Spring(0.0, TW * 7.0, 1.0); ey = Spring(0.0, TW * 7.0, 1.0)
    lean = Spring(0.0, TW * 1.1, 0.9)
    pel = Spring(0.0, TW * 0.45, 1.0)
    shr = Spring(0.0, TW * 1.6, 0.8)
    brow = Spring(0.0, TW * 3.0, 0.8)
    furrow = Spring(0.0, TW * 1.5, 1.0)
    smile = Spring(0.45, TW * 1.5, 1.0)
    mw = Spring(20.0, TW * 10.0, 0.9); mh = Spring(0.0, TW * 10.0, 0.9)
    fired = set()
    next_blink = 1.2; blink_t = -1.0; last_yaw_t = 0.0
    weight_target = 0.0; next_shift = 2.5
    micro = (0.0, 0.0); next_micro = 1.0
    stand_feet = None
    prev_fore = {'A': PI / 2, 'B': PI / 2}
    sgn = {'A': None, 'B': None, 'kA': None, 'kB': None}
    sgt = {}
    out = []
    for f in range(N):
        t = f * dt
        p = Pose()
        # ---------- locomocao
        w = perf.walk_at(t)
        walking_w = 0.0
        if w is not None and t < w.t_end:
            px, bob, feet, phi, walking_w = w.state(t)
            dr = w.dir
            in_settle = t > w.t0 + w.T
            stand_feet = None
        else:
            dr = 1.0
            if w is not None:
                px = w.x1
            else:
                px = perf.x_start
            bob = 0.0; phi = 0.0; in_settle = False
            if stand_feet is None or stand_feet[0] != px:
                stand_feet = (px, [(px - 28 * sc, floor, 0.0), (px + 28 * sc, floor, 0.0)])
            feet = stand_feet[1]
        standing = (walking_w < 0.02) and not (w is not None and w.t0 <= t < w.t0 + w.T)
        # troca de peso quando parado
        if standing:
            if t > next_shift:
                weight_target = rnd.choice([-8.0, 6.0, -5.0, 8.0]) * sc; next_shift = t + rnd.uniform(3.0, 5.5)
        else:
            weight_target = 0.0
        pel.step(weight_target, dt)
        breath = math.sin(TW * t / 3.7)
        p.px = px + pel.x
        p.py = floor - STAND_H * sc + 5.5 * sc * walking_w + bob + abs(pel.x) * 0.35 - breath * 0.6 * sc
        # pes
        fs = sorted(feet, key=lambda q: q[0])
        moving = w is not None and t < w.t_end and not standing
        for key, (fx, fy, toe), side in zip(('A', 'B'), fs, (-1, 1)):
            setattr(p, 'f' + key, (fx, fy))
            if moving:
                base = 0.0 if dr > 0 else PI
                setattr(p, 'toe' + key, base + (toe if dr > 0 else -toe))
                setattr(p, 'knee' + key, dr)
            else:
                setattr(p, 'toe' + key, (PI - 0.16) if side < 0 else 0.16)
                setattr(p, 'knee' + key, float(side))
        for key in ('A', 'B'):
            F = getattr(p, 'f' + key); kd = getattr(p, 'knee' + key)
            want, gap = pref_sign((p.px, p.py), F, THIGH * sc, SHIN * sc, leg_score((p.px, p.py), kd))
            kk = 'k' + key
            if sgn[kk] is None: sgn[kk] = want; sgt[kk] = want
            if want != sgt[kk] and gap > 4: sgt[kk] = want
            sgn[kk] += (sgt[kk] - sgn[kk]) * (1 - math.exp(-dt * 9.0))
            setattr(p, 'sk' + key, sgn[kk])
        # ---------- tronco
        g_any = perf.active_gesture('B', t)
        lean_t = 0.06 * dr * walking_w - pel.x * 0.0025
        if g_any and g_any['kind'] in ('point', 'present', 'present_hi'):
            lean_t += 0.035
        p.lean = lean.step(lean_t, dt)
        p.bend = -p.lean * 40
        sh_t = 0.0
        for (a, b) in perf.shrugs:
            if a - 0.1 <= t <= b: sh_t = 12.0
        p.shrug = shr.step(sh_t, dt) + 1.3 * breath
        p.sc = sc
        sk = skeleton(p)
        S = sk['S']; H = sk['H']
        # ---------- olhar
        lt = perf.look_at(t)
        if walking_w > 0.15 and lt == 'walk':
            yt, ext, eyt, pt = 0.78 * dr, 0.85 * dr, 0.15, 0.08
        elif lt == 'walk' or lt == 'cam':
            if t > next_micro:
                micro = (rnd.uniform(-0.22, 0.22), rnd.uniform(-0.12, 0.12)); next_micro = t + rnd.uniform(0.9, 2.2)
            yt, ext, eyt, pt = 0.0, micro[0], micro[1], 0.0
        else:
            tx, ty = perf.anchors[lt[1]]
            dx, dy = tx - H[0], ty - H[1]
            yt = clamp(dx / 330.0, -0.85, 0.85)
            dd = math.hypot(dx, dy) or 1
            ext, eyt = clamp(dx / dd * 1.1, -1, 1), clamp(dy / dd * 1.1, -1, 1)
            pt = clamp(dy / 900.0, -0.35, 0.35)
        prev_yaw = yaw.x
        # balanco de cabeca (negacao)
        shake = 0.0
        for (t0, dur, amp) in perf.shakes:
            if t0 <= t <= t0 + dur:
                u = (t - t0) / dur
                shake += amp * math.sin(TW * 2.6 * (t - t0)) * math.sin(PI * u)
        p.yaw = yaw.step(yt, dt) + shake
        if abs(yt - prev_yaw) > 0.45 and t - last_yaw_t > 0.8:
            blink_t = t; last_yaw_t = t
        p.eye_x = ex.step(ext, dt); p.eye_y = ey.step(eyt, dt)
        # aceno de cabeca
        for i, (tn, amp) in enumerate(perf.nods):
            if ('n', i) not in fired and t >= tn:
                pitch.v += 1.6 * amp; fired.add(('n', i))
        speaking = perf.speaking(t)
        talk_bob = 0.035 * math.sin(TW * 1.9 * t) if speaking else 0.0
        p.pitch = pitch.step(pt, dt) + talk_bob
        tl_t = 0.0
        for (a, b, ang) in perf.tilts:
            if a <= t <= b: tl_t = ang
        p.tilt = tilt.step(tl_t + 0.02 * math.sin(TW * t / 5.3), dt)
        # ---------- rosto
        emo = perf.emotion_at(t)
        bi = 0.0
        for (tb, amp) in perf.brow_imp:
            if t >= tb:
                bi += amp * math.exp(-(t - tb) / 0.42) * sstep((t - tb) / 0.08)
        p.brow_raise = brow.step(emo[2] + bi + (0.12 if speaking else 0.0), dt)
        p.brow_furrow = furrow.step(emo[3], dt)
        (vw, vh), on = perf.mouth_target(t)
        if perf.env is not None:
            e = perf.env[min(f, len(perf.env) - 1)]
            gte = clamp((e - 0.07) / 0.45, 0.0, 1.0) ** 0.7
            if not on and gte > 0.25: (vw, vh), on = VIS['E'], True
            vh = vh * min(1.0, gte * 1.15)
            if gte < 0.05: vw, vh = VIS['rest']
        p.mouth_w = mw.step(vw, dt); p.mouth_h = max(0.0, mh.step(vh, dt))
        p.smile = smile.step(emo[1] * (0.55 if on else 1.0), dt)
        # piscadas
        if t >= next_blink:
            blink_t = t; next_blink = t + rnd.uniform(2.2, 4.8)
            if rnd.random() < 0.15: next_blink = t + 0.32
        u = t - blink_t
        p.blink = 0.0 if u < 0 else (sstep(u / 0.055) if u < 0.055 else (1.0 if u < 0.1 else max(0.0, 1 - (u - 0.1) / 0.09)))
        # ---------- bracos
        for key, side in (('A', -1), ('B', 1)):
            st = arm[key]
            g = perf.active_gesture(key, t)
            if g is not None:
                extra = None
                if g['kind'] == 'point':
                    ax, ay = perf.anchors[g['extra']]
                    extra = ((ax - S[0]) / sc, (ay - S[1]) / sc)
                tg = gesture_target(g['kind'], side, t, g['ts'], extra)
                wsp, zsp = TW * 1.75, 0.72
            else:
                if walking_w > 0.05 and not standing:
                    sw = math.sin(PI * phi) * (1 if key == 'B' else -1)
                    tg = gesture_target('hang', side)
                    fwd = max(0.0, sw * dr * (1 if True else 1))
                    tg['pos'] = (tg['pos'][0] - side * 10 + dr * sw * 58 * walking_w, tg['pos'][1] - 10 * abs(sw) * walking_w)
                    tg['fo'] = 1.0 - 0.18 * max(0.0, sw) * walking_w
                    tg['ang'] = PI / 2 - dr * sw * 0.45
                    wsp, zsp = TW * 2.4, 0.85
                elif perf.in_sentence(t):
                    tg = gesture_target('beat' if key == 'B' else 'hang', side)
                    wsp, zsp = TW * 1.5, 0.8
                else:
                    tg = gesture_target('clasp', side)
                    wsp, zsp = TW * 1.3, 0.85
            for (ti, k2, vx, vy) in perf.impulses:
                kk = ('i', ti, k2)
                if k2 == key and kk not in fired and t >= ti:
                    if g is None or g['kind'] in ('you', 'present', 'count1', 'count2', 'count3', 'point', 'present_hi') or perf.in_sentence(t):
                        st['x'].v += vx * sc; st['y'].v += vy * sc
                    fired.add(kk)
            x = st['x'].step(tg['pos'][0] * sc, dt, wsp, zsp); y = st['y'].step(tg['pos'][1] * sc, dt, wsp, zsp)
            k = 1 - math.exp(-dt * 9.0)
            target_shape = hand_params(tg['hand'])
            sh = st['shape']
            sh['ext'] = [lerp(a, b, 1 - math.exp(-dt * 13)) for a, b in zip(sh['ext'], target_shape['ext'])]
            for nm in ('th', 'spread', 'tha'):
                sh[nm] = lerp(sh[nm], target_shape[nm], 1 - math.exp(-dt * 13))
            st['up'] = lerp(st['up'], tg['up'], k); st['fo'] = lerp(st['fo'], tg['fo'], k)
            st['eb'] = (lerp(st['eb'][0], tg['eb'][0], k), lerp(st['eb'][1], tg['eb'][1], k))
            st['scale'] = lerp(st['scale'], tg['scale'], k); st['fore'] = lerp(st['fore'], tg['fore'], k)
            st['prop'] = lerp(st['prop'], tg['prop'], 1 - math.exp(-dt * 11))
            ta = near_ang(tg['ang'], st['ang'].x)
            a = st['ang'].step(ta, dt)
            setattr(p, 'w' + key, (S[0] + x, S[1] + y))
            setattr(p, 'up' + key, st['up']); setattr(p, 'fo' + key, st['fo']); setattr(p, 'eb' + key, st['eb'])
            # lado do cotovelo: muda de forma continua (gira em 3D), com histerese
            l1 = UPPER * st['up'] * sc; l2 = FORE * st['fo'] * sc
            want, gap = pref_sign(S, (S[0] + x, S[1] + y), l1, l2, arm_score(S, side, st['eb']))
            if sgn[key] is None: sgn[key] = want; sgt[key] = want
            if want != sgt[key] and gap > 10: sgt[key] = want
            sgn[key] += (sgt[key] - sgn[key]) * (1 - math.exp(-dt * 7.5))
            setattr(p, 'sg' + key, sgn[key])
            setattr(p, 'hand' + key, dict(ext=list(sh['ext']), th=sh['th'], spread=sh['spread'], tha=sh['tha'],
                                          ang=a, scale=st['scale'], fore=st['fore'], prop=st['prop']))
        out.append(p)
    return out

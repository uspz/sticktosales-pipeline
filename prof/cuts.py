"""Cortes curtos (20-30 s) das licoes com gancho escrito na tela.
uso:
  python3 cuts.py still <lesson> <EN|PT> <cut_id> <saida.png> <t_rel1,t_rel2,...>
  python3 cuts.py render <lesson> <EN|PT> <cut_id> <saida.mp4>
"""
import sys, json, math, subprocess, importlib, os
from cairoc import Canvas
from perf import FPS, sstep, clamp

W, H = 1080, 1920
P = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # raiz do repo
YEL = '#FFD21F'

# cortes: (bloco inicial, bloco final)
CUTS = {'dicas': (1, 4), 'exemplo': (5, 7)}

HOOKS = {
    11: {'dicas': {'PT': '3 truques pro seu preço *não* *parecer* *caro*',
                   'EN': '3 tricks so your price *never* *looks* *expensive*'},
         'exemplo': {'PT': 'O truque que faz R$~1.500 *parecer* *barato*',
                     'EN': 'The trick that makes £1,500 *look* *cheap*'}},
    12: {'dicas': {'PT': "Cliente diz *'compro* *depois'*? Faz isso",
                   'EN': "Customer says *'I'll* *buy* *later'*? Do this"},
         'exemplo': {'PT': 'Como ela esgotou as vagas em *2* *dias*',
                     'EN': 'How she sold out her spots in *2* *days*'}},
    13: {'dicas': {'PT': 'Seu cliente tem *medo* *de* *comprar*? Faz isso',
                   'EN': 'Customers *scared* *to* *buy*? Do this'},
         'exemplo': {'PT': 'Uma frase que fez ela fechar o *dobro*',
                     'EN': 'One line that *doubled* her clients'}},
}
ENDCARD = {'PT': 'AULA COMPLETA NO PERFIL', 'EN': 'FULL LESSON ON MY PROFILE'}


def al_path(n, lang):
    for p in (f'{P}/alinhamentos/al{n}_{lang.lower()}.json', f'{P}/prof/al{n}_{lang.lower()}.json', f'{P}/al{n}_{lang.lower()}.json'):
        if os.path.exists(p): return p
    raise FileNotFoundError(n)


def layout(c, txt, size, maxw):
    c.font('Poppins', size, True)
    words = [(w.replace('*', '').replace('~', ' '), w.startswith('*')) for w in txt.split()]
    sp = c.extents('a a').x_advance - c.extents('aa').x_advance
    lines, cur, cw = [], [], 0.0
    for w, hi in words:
        ww = c.extents(w).x_advance
        add = ww if not cur else cw + sp + ww
        if cur and add > maxw:
            lines.append((cur, cw)); cur, cw = [(w, hi, ww)], ww
        else:
            cur.append((w, hi, ww)); cw = add
    if cur: lines.append((cur, cw))
    return lines, sp


def layout_bal(c, txt, size, maxw):
    lines, sp = layout(c, txt, size, maxw)
    n = len(lines); lo, hi = 150.0, float(maxw)
    for _ in range(14):
        mid = (lo + hi) / 2
        if len(layout(c, txt, size, mid)[0]) <= n: hi = mid
        else: lo = mid
    return layout(c, txt, size, hi + 0.5)


def hook_box(c, txt, size, maxw, cx, cy, sc=1.0, pad=35, rad=30, border=6):
    lines, sp = layout_bal(c, txt, size, maxw)
    lh = size * 1.18
    bw = max(w for _, w in lines) + 2 * pad + 20
    bh = lh * len(lines) + 2 * pad
    c.save(); c.translate(cx, cy); c.scale(sc, sc)
    c.color('#000000', 0.18); c.rrect(-bw / 2 + 6, -bh / 2 + 10, bw, bh, rad); c.fill()
    c.color('#111114', 0.95); c.rrect(-bw / 2, -bh / 2, bw, bh, rad); c.fill()
    c.color(YEL); c.lw(border); c.rrect(-bw / 2, -bh / 2, bw, bh, rad); c.stroke()
    c.font('Poppins', size, True)
    y = -bh / 2 + pad + size * 0.92
    for ln, lw_ in lines:
        x = -lw_ / 2
        for w, hi, ww in ln:
            c.color(YEL if hi else '#FFFFFF'); c.text(x, y, w)
            x += ww + sp
        y += lh
    c.restore()
    return bh


def draw_hook(c, txt, tr):
    k = sstep((tr - 2.3) / 0.4)
    if k < 1:
        size = 80
        lines, _ = layout(c, txt, size, 880)
        while len(lines) > 3 and size > 50:
            size -= 4; lines, _ = layout(c, txt, size, 880)
        pulse = 1.0 + 0.025 * math.sin(min(tr, 2.3) / 2.3 * math.pi * 2)
        c.push()
        hook_box(c, txt, size, 880, W / 2, 640 - 380 * k, (1 - 0.5 * k) * pulse)
        c.pop_paint(1 - k)
    if k > 0:
        lines, _ = layout(c, txt, 48, 980)
        bh = 48 * 1.18 * len(lines) + 2 * 18
        c.push()
        hook_box(c, txt, 48, 980, W / 2, 20 + bh / 2 - 30 * (1 - k), 1.0, pad=18, rad=22, border=4)
        c.pop_paint(k)


def draw_endcard(c, txt, tr, dur):
    t0 = dur - 2.6
    if tr < t0: return
    k = sstep((tr - t0) / 0.3)
    pop = 1.0 + 0.12 * math.sin(math.pi * clamp((tr - t0) / 0.35, 0, 1))
    c.save(); c.translate(W / 2, 1805); c.scale(pop, pop)
    c.font('Poppins', 46, True); w = c.extents(txt).x_advance
    c.color(YEL, k); c.rrect(-w / 2 - 40, -46, w + 80, 86, 43); c.fill()
    c.color('#111114', k); c.text(-w / 2, 16, txt)
    c.restore()


def setup(n, lang, cut):
    mod = importlib.import_module(f'lesson{n}')
    al = json.load(open(al_path(n, lang)))
    pf, poses = mod.build(lang, al)
    i0, i1 = CUTS[cut]
    bl = al['blocks']
    a = bl[i0][0] - 0.08
    b = min(bl[i1][1] + 0.75, bl[i1 + 1][0] - 0.2) if i1 + 1 < len(bl) else al['end'] + 0.6
    blocks_mod = [(-1e9 if k <= i0 else s, e) for k, (s, e) in enumerate(bl)]
    return mod, al, pf, poses, a, b, blocks_mod


def frame(c, mod, pf, poses, f, blocks_mod, L, end, a, b, hook, endtxt):
    t = f / FPS
    mod.render_frame(c, pf, poses, f, blocks_mod, L, end)
    tr = t - a
    c.color('#E0E0E0'); c.rect(0, 0, W, 12); c.fill()
    c.color('#000000'); c.rect(0, 0, W * clamp(tr / (b - a), 0, 1), 12); c.fill()
    draw_hook(c, hook, tr)
    draw_endcard(c, endtxt, tr, b - a)


def main():
    mode, n, lang, cut = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
    mod, al, pf, poses, a, b, blocks_mod = setup(n, lang, cut)
    L = mod.TXT[lang]; hook = HOOKS[n][cut][lang]; endtxt = ENDCARD[lang]
    c = Canvas(W, H)
    if mode == 'still':
        from PIL import Image
        out = sys.argv[5]; times = [float(x) for x in sys.argv[6].split(',')]
        ims = []
        for tr in times:
            f = int((a + tr) * FPS)
            frame(c, mod, pf, poses, f, blocks_mod, L, al['end'], a, b, hook, endtxt)
            ims.append(Image.fromarray(c.rgb()).resize((360, 640)))
        cols = min(5, len(ims)); rows = (len(ims) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * 364, rows * 644), 'gray')
        for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * 364, (i // cols) * 644))
        sheet.save(out)
        print('cut', n, lang, cut, round(a, 2), round(b, 2), 'dur', round(b - a, 2))
    else:
        outp = sys.argv[5]
        fa, fb = int(round(a * FPS)), int(round(b * FPS))
        dur = (fb - fa) / FPS
        ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr0', '-s', f'{W}x{H}',
                               '-r', str(FPS), '-i', '-', '-ss', f'{fa / FPS:.3f}', '-t', f'{dur:.3f}', '-i', al['audio'],
                               '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                               '-pix_fmt', 'yuv420p',
                               '-af', f'afade=t=in:d=0.04,afade=t=out:st={max(0, dur - 0.3):.3f}:d=0.3,apad,loudnorm=I=-14:TP=-1.5:LRA=11',
                               '-c:a', 'aac', '-b:a', '192k', '-t', f'{dur:.3f}', outp], stdin=subprocess.PIPE)
        for f in range(fa, fb):
            frame(c, mod, pf, poses, f, blocks_mod, L, al['end'], a, b, hook, endtxt)
            ff.stdin.write(c.bgr0_bytes())
        ff.stdin.close(); ff.wait()
        print('ok', outp, round(dur, 2))


if __name__ == '__main__':
    main()

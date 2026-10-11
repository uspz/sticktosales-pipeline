"""Alinha as palavras do roteiro ao audio real (sem transcricao): usa as pausas como ancoras,
distribui as palavras pelas silabas dentro de cada frase, encurta silencios e ajusta o tempo.

uso: python3 align.py <audio> <roteiro.txt> <saida.json> [alvo_seg]
Gera <saida>.wav (audio final) e <saida>.json (palavras com tempos no audio final, envelope)."""
import re, sys, json, wave, subprocess, math
import numpy as np

VOWELS = 'aeiouáéíóúâêôãõàüy'


def syl(t):
    return max(1, len(re.findall('[' + VOWELS + ']+', t.lower())))


def load_mono(path, sr=24000):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(sr), '-f', 's16le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0, sr


def silences(x, sr, thr_db=-35.0, min_d=0.15):
    """intervalos de silencio (inicio, fim) em segundos, por energia em janelas de 10 ms."""
    hop = int(sr * 0.01)
    n = len(x) // hop
    e = np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(e + 1e-9)
    quiet = db < thr_db
    out = []; i = 0
    while i < n:
        if quiet[i]:
            j = i
            while j < n and quiet[j]: j += 1
            if (j - i) * 0.01 >= min_d: out.append((i * 0.01, j * 0.01))
            i = j
        else:
            i += 1
    return out, len(x) / sr


def parse_script(path):
    blocks = [b.strip() for b in open(path, encoding='utf-8').read().strip().split('\n\n') if b.strip()]
    words = []; sents = []
    for bi, b in enumerate(blocks):
        for s in re.split(r'(?<=[.?!])\s+', b):
            s = s.strip()
            if not s: continue
            si = len(sents); sents.append(dict(block=bi, text=s, words=[]))
            for w in s.split():
                sents[si]['words'].append(len(words))
                words.append(dict(text=w, block=bi, sent=si))
    return blocks, sents, words


def dp_assign(exps, cands, inner, bonus_fn, skip_fn=lambda i: 1.0):
    """Associa cada fim de frase a uma pausa (ordem crescente); pode deixar frase sem pausa (com custo)
    e pode ignorar pausas (pausas no meio da frase)."""
    n, m = len(exps), len(cands)
    if n == 0: return []
    mids = [(inner[k][0] + inner[k][1]) / 2 for k in cands]
    durs = [inner[k][1] - inner[k][0] for k in cands]
    INF = 1e18
    # dp[j+1]: custo minimo com ultima pausa usada = j (j=-1 -> nenhuma)
    dp = [0.0] + [INF] * m
    back = []
    for i in range(n):
        nd = [INF] * (m + 1); bk = [None] * (m + 1)
        # pular frase
        for j in range(m + 1):
            c = dp[j] + skip_fn(i)
            if c < nd[j]: nd[j] = c; bk[j] = ('skip', j)
        # usar pausa j2 > j
        best = INF; bj = None
        for j2 in range(m):
            if dp[j2] < best: best = dp[j2]; bj = j2      # dp[j2] = ultima usada j2-1 < j2
            c = best + abs(mids[j2] - exps[i]) - bonus_fn(i, durs[j2])
            if c < nd[j2 + 1]: nd[j2 + 1] = c; bk[j2 + 1] = ('use', bj)
        back.append(bk); dp = nd
    j = min(range(m + 1), key=lambda j: dp[j])
    res = [None] * n
    for i in range(n - 1, -1, -1):
        kind, pj = back[i][j]
        if kind == 'use': res[i] = cands[j - 1]
        j = pj
    return res


def main():
    aud, script, out = sys.argv[1], sys.argv[2], sys.argv[3]
    target = float(sys.argv[4]) if len(sys.argv) > 4 else 65.5
    x, sr = load_mono(aud)
    sil, dur = silences(x, sr)
    lead = sil[0][1] if sil and sil[0][0] < 0.02 else 0.0
    tail = [s for s in sil if s[1] >= dur - 0.02]
    end_speech = tail[0][0] if tail else dur
    inner = [s for s in sil if s[0] > 0.02 and s[1] < dur - 0.02]
    blocks, sents, words = parse_script(script)
    nS = len(sents)
    # tempo de fala (sem silencios) para expectativas
    speech = []; prev = lead
    for a, b in inner: speech.append((prev, a)); prev = b
    speech.append((prev, end_speech))
    S = sum(b - a for a, b in speech)

    def raw_at(fr):
        t = fr * S; acc = 0.0
        for a, b in speech:
            if acc + (b - a) >= t: return a + (t - acc)
            acc += b - a
        return speech[-1][1]
    wts = [sum(syl(words[i]['text']) for i in s['words']) for s in sents]
    tot = sum(wts); cum = 0; exp = []
    for w in wts[:-1]: cum += w; exp.append(raw_at(cum / tot))
    # segmentos: fim de bloco (B), fim de frase (S), dois-pontos (C), virgula (K)
    segs_w = []; seg_kind = []
    cur = []
    for wi, w in enumerate(words):
        cur.append(wi)
        last = wi == len(words) - 1
        nxt_block = (not last) and words[wi + 1]['block'] != w['block']
        ch = w['text'][-1]
        kind = None
        if nxt_block: kind = 'B'
        elif ch in '.?!': kind = 'S'
        elif ch == ':': kind = 'C'
        elif ch in ',;': kind = 'K'
        if kind and not last:
            segs_w.append(cur); seg_kind.append(kind); cur = []
    segs_w.append(cur); seg_kind.append('E')
    nG = len(segs_w)
    gsyl = [sum(syl(words[i]['text']) for i in g) for g in segs_w]
    allsil = [(a_, b_) for (a_, b_) in sil if b_ - a_ >= 0.12]

    def sclock(t):
        tot_ = t
        for a_, b_ in allsil:
            if b_ <= t: tot_ -= (b_ - a_)
            elif a_ < t: tot_ -= (t - a_)
        return tot_
    r = (sclock(end_speech) - sclock(lead)) / max(1, sum(gsyl))
    cand = [k for k, (a_, b_) in enumerate(inner) if b_ - a_ >= 0.2]
    m = len(cand)
    cs = [sclock(inner[k][0]) for k in cand]
    du = [inner[k][1] - inner[k][0] for k in cand]
    big = max(du) if du else 1.0
    pref = [0]
    for w_ in gsyl: pref.append(pref[-1] + w_)
    BON = {'B': lambda d: 3.0 * min(d / max(0.6, big * 0.8), 1.25), 'S': lambda d: 1.6 * min(d / 0.6, 1.0),
           'C': lambda d: 1.0 * min(d / 0.5, 1.0), 'K': lambda d: 0.6 * min(d / 0.35, 1.0)}
    SKIP = {'B': 9.0, 'S': 0.9, 'C': 0.25, 'K': 0.08}
    INF = 1e18
    best = {(-1, -1): 0.0}; back = {}
    start_clock = sclock(lead)
    by_i = {-1: [(-1, -1)]}
    for i in range(nG - 1):
        by_i[i] = []
        for j in range(m):
            bestc = INF; arg = None
            for pi in range(max(-1, i - 7), i):
                skipped = sum(SKIP[seg_kind[q]] for q in range(pi + 1, i))
                for (qi, pj) in by_i.get(pi, []):
                    if pj >= j: continue
                    pc = best[(qi, pj)]
                    c0 = start_clock if pj == -1 else cs[pj]
                    spoken = cs[j] - c0
                    expect = r * (pref[i + 1] - pref[pi + 1])
                    c = pc + 3.0 * abs(math.log((spoken + 0.25) / (expect + 0.25))) + 0.15 * abs(spoken - expect) + skipped - BON[seg_kind[i]](du[j])
                    if c < bestc: bestc = c; arg = (qi, pj)
            if arg is not None:
                best[(i, j)] = bestc; back[(i, j)] = arg; by_i[i].append((i, j))
    endc = INF; earg = None
    for pi in range(max(-1, nG - 9), nG - 1):
        skipped = sum(SKIP[seg_kind[q]] for q in range(pi + 1, nG - 1))
        for (qi, pj) in by_i.get(pi, []):
            pc = best[(qi, pj)]
            c0 = start_clock if pj == -1 else cs[pj]
            spoken = sclock(end_speech) - c0
            expect = r * (pref[nG] - pref[pi + 1])
            c = pc + 3.0 * abs(math.log((max(0.0, spoken) + 0.25) / (expect + 0.25))) + 0.15 * abs(spoken - expect) + skipped
            if c < endc: endc = c; earg = (qi, pj)
    gassign = {}
    st_ = earg
    while st_ != (-1, -1):
        i, j = st_
        gassign[i] = cand[j]
        st_ = back[st_]
    # compatibilidade com o restante: assign por frase e tipos de pausa
    sent_end_seg = {}
    for gi, g in enumerate(segs_w):
        sent_end_seg[words[g[-1]]['sent']] = gi
    block_end = [sents[i]['block'] != sents[i + 1]['block'] for i in range(nS - 1)]
    # ----- encurta silencios: bloco -> gB, frase -> gS, demais -> gI
    kinds = {}
    for gi, k in gassign.items():
        kinds[k] = {'B': 'B', 'S': 'S', 'C': 'S', 'K': 'K'}[seg_kind[gi]]

    def build(gB, gS, gI):
        tt = 0.0; pv = lead
        for k, (a, b) in enumerate(inner):
            tt += a - pv
            tt += {'B': gB, 'S': gS, 'K': min(gI + 0.06, b - a)}.get(kinds.get(k), min(gI, b - a))
            pv = b
        return tt + (end_speech - pv)
    gB, gS, gI = 0.5, 0.28, 0.14
    while build(gB, gS, gI) < target - 0.5 and (gB < 1.0 or gS < 0.5):
        gB = min(1.0, gB + 0.04); gS = min(0.5, gS + 0.02); gI = min(0.22, gI + 0.006)
    segs = []; maps = []   # (raw_a, raw_b, new_a)
    tt = 0.0; pv = lead
    for k, (a, b) in enumerate(inner):
        segs.append(x[int(pv * sr):int(a * sr)]); maps.append((pv, a, tt)); tt += a - pv
        g = {'B': gB, 'S': gS, 'K': min(gI + 0.06, b - a)}.get(kinds.get(k), min(gI, b - a))
        maps.append((a, b, tt, g)); segs.append(np.zeros(int(g * sr), np.float32)); tt += g; pv = b
    segs.append(x[int(pv * sr):int(min(dur, end_speech + 0.06) * sr)]); maps.append((pv, end_speech, tt)); tt += end_speech - pv
    y = np.concatenate(segs)
    L = len(y) / sr
    f = max(0.94, min(1.22, L / target))

    def to_final(t):
        for m_ in maps:
            if len(m_) == 3:
                a, b, na = m_
                if a <= t <= b: return (na + (t - a)) / f
            else:
                a, b, na, g = m_
                if a <= t <= b: return (na + (t - a) / max(1e-6, b - a) * g) / f
        return (t - lead) / f if t < lead else L / f
    # ----- tempos das palavras: trechos entre ancoras (segmentos agrupados), silabas no tempo de fala
    anchors = sorted(gassign.items())
    spans = []; prev_i = -1; prev_t = lead
    for gi, k in anchors:
        spans.append((prev_i + 1, gi, prev_t, inner[k][0])); prev_i = gi; prev_t = inner[k][1]
    spans.append((prev_i + 1, nG - 1, prev_t, end_speech))
    for (g0, g1, a, b) in spans:
        ws = [w for g in segs_w[g0:g1 + 1] for w in g]
        sp = []; pv = a
        for (u, v) in inner:
            if u >= a and v <= b:
                sp.append((pv, u)); pv = v
        sp.append((pv, b))
        Ssp = sum(max(0.0, q - p) for p, q in sp) or 1e-6
        wsy = [syl(words[w]['text']) + 0.35 for w in ws]; tw = sum(wsy)

        def at(fr, sp=sp, Ssp=Ssp):
            t = fr * Ssp; acc = 0.0
            for p, q in sp:
                d = max(0.0, q - p)
                if acc + d >= t: return p + (t - acc)
                acc += d
            return sp[-1][1]
        acc = 0.0
        for w, wy in zip(ws, wsy):
            words[w]['raw0'] = at(acc / tw); acc += wy; words[w]['raw1'] = at(acc / tw)
    for w in words:
        w['t0'] = round(to_final(w['raw0']), 3); w['t1'] = round(to_final(w['raw1']), 3)
    # ----- audio final
    wav_tmp = out.replace('.json', '_tight.wav'); wav_out = out.replace('.json', '.wav')
    wv = wave.open(wav_tmp, 'wb'); wv.setnchannels(1); wv.setsampwidth(2); wv.setframerate(sr)
    wv.writeframes((np.clip(y, -1, 1) * 32767).astype(np.int16).tobytes()); wv.close()
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', wav_tmp, '-af', f'atempo={f:.4f}', '-ar', '48000', wav_out], check=True)
    # envelope (30 fps) do audio final para a boca
    z, sr2 = load_mono(wav_out, 24000)
    hop = sr2 // 30; n = len(z) // hop
    env = np.sqrt(np.mean(z[:n * hop].reshape(n, hop) ** 2, axis=1))
    ref = np.percentile(env[env > 0.01], 90) if np.any(env > 0.01) else 1.0
    env = np.clip(env / ref, 0, 1.2)
    blocks_t = []
    for b in range(len(blocks)):
        ws = [w for w in words if w['block'] == b]
        blocks_t.append((ws[0]['t0'], ws[-1]['t1']))
    res = dict(words=[dict(text=w['text'], t0=w['t0'], t1=w['t1'], block=w['block'], sent=w['sent']) for w in words],
               blocks=blocks_t, end=round(len(z) / sr2, 3), f=f, gaps=(gB, gS, gI), env=[round(float(v), 3) for v in env],
               audio=wav_out)
    json.dump(res, open(out, 'w'), ensure_ascii=False)
    print('raw', round(dur, 1), 'tight', round(L, 1), 'f', round(f, 3), 'final', res['end'], 'gaps', [round(g, 2) for g in (gB, gS, gI)])
    for gi in range(nG - 1):
        k = gassign.get(gi)
        if seg_kind[gi] in 'BS' or k is not None:
            txt = ' '.join(words[w]['text'] for w in segs_w[gi])
            print(gi, seg_kind[gi], txt[-34:], '->', None if k is None else (round(inner[k][0], 2), round(inner[k][1] - inner[k][0], 2)))


if __name__ == '__main__':
    main()

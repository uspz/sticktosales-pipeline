import numpy as np, wave, sys
OUT,SEED,BPM_,PROG,TR,LEAD=sys.argv[1],int(sys.argv[2]),float(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]),sys.argv[6]
from scipy.signal import butter, lfilter, fftconvolve
sr=44100; BPM=BPM_; beat=60/BPM; bar=4*beat; DUR=96
N=int(DUR*sr); rng=np.random.default_rng(SEED)
mix_p=np.zeros(N); mix_b=np.zeros(N); mix_d=np.zeros(N); mix_m=np.zeros(N)
def add(buf,sig,t0):
    i=max(0,int(t0*sr))
    if i>=N: return
    e=min(N,i+len(sig)); buf[i:e]+=sig[:e-i]
def hz(n): return 440*2**((n-69)/12)
def ep(note,dur,vel=1.0):
    t=np.arange(int(dur*sr))/sr; f=hz(note)
    s=np.sin(2*np.pi*f*t)+0.35*np.sin(2*np.pi*2*f*t)*np.exp(-5*t)+0.12*np.sin(2*np.pi*3*f*t)*np.exp(-9*t)
    s+=0.25*np.sin(2*np.pi*f*1.004*t)  # leve desafino (chorus)
    env=np.minimum(1,t/0.012)*np.exp(-1.6*t)
    return s*env*vel*(1+0.12*np.sin(2*np.pi*4.2*t))
def pluck(note,dur,vel=1.0):
    t=np.arange(int(dur*sr))/sr; f=hz(note)
    s=np.sin(2*np.pi*f*t)+0.5*np.sin(2*np.pi*2*f*t)*np.exp(-8*t)+0.25*np.sin(2*np.pi*3*f*t)*np.exp(-14*t)
    return s*np.minimum(1,t/0.004)*np.exp(-4.5*t)*vel
def bass(note,dur):
    t=np.arange(int(dur*sr))/sr; f=hz(note)
    return (np.sin(2*np.pi*f*t)+0.2*np.sin(2*np.pi*2*f*t))*np.minimum(1,t/0.01)*np.exp(-2.6*t)
def kick():
    t=np.arange(int(0.45*sr))/sr; f=45+90*np.exp(-t*28)
    return np.sin(2*np.pi*np.cumsum(f)/sr)*np.exp(-t*8)
def snare():
    t=np.arange(int(0.3*sr))/sr; n=rng.standard_normal(len(t))
    b,a=butter(2,[1200/(sr/2),6500/(sr/2)],'band'); n=lfilter(b,a,n)
    return n*np.exp(-t*16)*0.55+np.sin(2*np.pi*185*t)*np.exp(-t*22)*0.4
def hat(open_=False):
    t=np.arange(int((0.18 if open_ else 0.05)*sr))/sr; n=rng.standard_normal(len(t))
    b,a=butter(2,7000/(sr/2),'high'); return lfilter(b,a,n)*np.exp(-t*(22 if open_ else 70))
# progressao: Cmaj7 - Am7 - Dm7 - G7  (2 compassos de cada acorde = 8 compassos; repete)
PROGS={0:[([48,52,55,59],36),([45,48,52,55],33),([50,53,57,60],38),([43,47,50,53],31)],
 1:[([53,57,60,64],41),([52,55,59,62],40),([50,53,57,60],38),([48,52,55,59],36)],
 2:[([52,55,59,62],40),([49,52,55,59],45),([50,54,57,61],38),([47,50,54,57],35)],
 3:[([45,48,52,55],33),([41,45,48,52],29),([48,52,55,59],36),([43,47,50,55],31)],
 4:[([50,54,57,61],38),([47,50,54,57],35),([43,47,50,54],31),([45,49,52,55],33)]}
chords=[([n+TR for n in ch],r+TR) for ch,r in PROGS[PROG]]
penta=[n+TR for n in {0:[72,74,76,79,81,84],1:[72,74,76,79,81,84],2:[74,76,78,81,83,86],3:[69,72,74,76,79,81],4:[74,76,78,81,83,86]}[PROG]]
nbar=int(DUR/bar)+1
for b_ in range(nbar):
    ch,root=chords[(b_//1)%4]; t0=b_*bar
    # piano: acorde no tempo 1 e sincopado no "e" do 2 (levemente arpejado)
    for k,n in enumerate(ch): add(mix_p,ep(n+12*(k>2)-0,2.8,0.55),t0+0.012*k+rng.normal(0,0.004))
    for k,n in enumerate(ch[1:]): add(mix_p,ep(n+12,1.6,0.38),t0+1.5*beat+0.018*k+rng.normal(0,0.004))
    # baixo
    add(mix_b,bass(root,1.4),t0); add(mix_b,bass(root,1.0),t0+2.5*beat); 
    if b_%2: add(mix_b,bass(root+7,0.8),t0+3.5*beat)
    # bateria (swing leve)
    sw=0.14*beat/2
    add(mix_d,kick()*0.9,t0); add(mix_d,kick()*0.7,t0+2.5*beat+sw)
    add(mix_d,snare(),t0+1*beat+rng.normal(0,0.006)); add(mix_d,snare(),t0+3*beat+rng.normal(0,0.006))
    for h in range(8):
        tt=t0+h*beat/2+(sw if h%2 else 0); add(mix_d,hat(h==7)*(0.35 if h%2 else 0.5)*rng.uniform(0.8,1.1),tt)
    # melodia esparsa (pentatonica), so a partir do compasso 3, 2-3 notas
    if b_>=2 and b_%2==0:
        for pos in rng.choice([0.5,1.5,2.0,3.0,3.5],size=2,replace=False):
            n=int(rng.choice(penta)); add(mix_m,(pluck(n,0.9,0.30) if LEAD=='pluck' else ep(n,1.3,0.28)),t0+pos*beat)
# reverb curto no piano/melodia
ir_t=np.arange(int(0.9*sr))/sr; ir=rng.standard_normal(len(ir_t))*np.exp(-ir_t*5)
wet=fftconvolve(mix_p+mix_m,ir)[:N]*0.012
def lp(x,fc): b,a=butter(2,fc/(sr/2),'low'); return lfilter(b,a,x)
x=lp(mix_p+mix_m*0.9,3800)*0.55+wet+lp(mix_b,300)*0.75+lp(mix_d,6000)*0.4
# chiado de vinil e leve ruido
crack=np.zeros(N); idx=rng.integers(0,N-200,size=int(DUR*6))
for i in idx: crack[i:i+60]+=rng.standard_normal(60)*rng.uniform(0.005,0.02)*np.exp(-np.arange(60)/8)
hiss=lp(rng.standard_normal(N),6000)*0.002
x=x+crack+hiss
# fade in/out, saturacao suave
f=int(2*sr); x[:f]*=np.linspace(0,1,f); x[-f:]*=np.linspace(1,0,f)
x=lp(np.tanh(x*1.2),6500); x=x/np.max(np.abs(x))*0.8
# estereo: leve atraso entre canais
L=x; R=np.concatenate([np.zeros(int(0.012*sr)),x[:-int(0.012*sr)]])
st=np.stack([L,R],1); pcm=(st*32767).astype(np.int16)
w=wave.open(OUT,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes()); w.close()
print('ok',DUR)

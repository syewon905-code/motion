import numpy as np, wave
SR=44100; D=30; n=SR*D; out=np.zeros((n,2))
BPM=120; beat=60/BPM; rng=np.random.default_rng(1)
def add(sig,t,pan=0.5,g=1):
    i=int(t*SR); s=sig[:max(0,n-i)]
    out[i:i+len(s),0]+=s*g*(1-pan)*2**0.5*0.7; out[i:i+len(s),1]+=s*g*pan*2**0.5*0.7
def env(L,a=0.005,r=0.3):
    t=np.arange(int(L*SR))/SR; return np.minimum(t/a,1)*np.exp(-t/r)
def kick():
    t=np.arange(int(0.4*SR))/SR; f=50+120*np.exp(-t*30); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*7)
def hat(L=0.05): return rng.standard_normal(int(L*SR))*env(L,0.001,0.015)
def clap():
    s=rng.standard_normal(int(0.25*SR))*env(0.25,0.002,0.06)
    return np.convolve(s,[1,-0.9],'same')
def tone(f,L,typ='saw',r=0.4,det=0.0):
    t=np.arange(int(L*SR))/SR; s=0
    for d in ([0] if det==0 else [-det,0,det]):
        ph=(f*(1+d))*t
        s=s+(2*(ph%1)-1 if typ=='saw' else np.sin(2*np.pi*ph))
    return s*env(L,0.01,r)
def lp(x,a=0.15):
    k=int(1/a); return np.convolve(x,np.ones(k)/k,'same')
mid=lambda m:440*2**((m-69)/12)
# can open + fizz intro
fz=rng.standard_normal(int(3*SR)); fz=np.diff(fz,prepend=0)*np.linspace(0.05,0.5,len(fz))
add(fz*0.25,0)
pop=rng.standard_normal(int(0.3*SR))*env(0.3,0.001,0.04); add(pop*0.9,2.4)
fz2=np.diff(rng.standard_normal(int(4*SR)),prepend=0)*env(4,0.01,1.2); add(fz2*0.35,2.45)
prog=[(57,[57,60,64,67]),(53,[53,57,60,64]),(48,[48,52,55,59]),(55,[55,59,62,66])] # Am9-ish bright: A F C G
start=3.0
nbars=int((D-start-1)/(4*beat))
for b in range(nbars+1):
    bt=start+b*4*beat; root,ch=prog[b%4]
    drop = 3<=b<11
    for k in range(4):
        tb=bt+k*beat
        if tb>D-1.5: break
        add(kick(),tb,0.5,0.9 if (b>=1) else 0.5)
        if drop and k%2==1: add(clap(),tb,0.5,0.35)
        for h in range(2):
            add(hat(),tb+h*beat/2+beat/4,0.65,0.25 if b>=1 else 0.1)
        # offbeat bass
        add(lp(tone(mid(root-12),beat*0.45,'saw',0.12),0.08),tb+beat/2,0.5,0.45)
    # pad chord
    pad=sum(lp(tone(mid(m),4*beat,'saw',1.5,0.006),0.05) for m in ch)
    add(pad*0.12,bt,0.5)
    # pluck arpeggio
    if b>=2:
        for s in range(8):
            m=ch[[0,2,1,3,2,0,3,1][s]]+12
            add(tone(mid(m),beat/2,'sin',0.12)*0.25+tone(mid(m+12),beat/2,'sin',0.06)*0.08,bt+s*beat/2,0.3+0.4*(s%2))
# riser into 14s and final hit 22s
for tr in [13.0,21.0]:
    L=1.0; r=np.diff(rng.standard_normal(int(L*SR)),prepend=0)*np.linspace(0,0.6,int(L*SR)); add(r,tr)
for th in [3,8,14,22]:
    add(kick()*1.2,th); add(np.diff(rng.standard_normal(int(1.5*SR)),prepend=0)*env(1.5,0.001,0.35)*0.3,th)
# outro chord
add(sum(tone(mid(m),4,'sin',1.6) for m in [69,72,76,81])*0.15,26.0)
# simple stereo delay
dl=int(beat*0.75*SR); out[dl:,0]+=out[:-dl,1]*0.18; out[dl:,1]+=out[:-dl,0]*0.18
fade=np.ones(n); fade[-int(1.5*SR):]=np.linspace(1,0,int(1.5*SR)); out*=fade[:,None]
out=np.tanh(out/np.max(np.abs(out))*1.6)*0.89
w=wave.open("music.wav","wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((out*32767).astype('<i2').tobytes()); w.close()

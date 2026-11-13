import numpy as np, wave
SR=44100; D=30; n=SR*D; L=np.zeros(n); R=np.zeros(n); rng=np.random.default_rng(2)
beat=0.5; bar=1.5
mid=lambda m:440*2**((m-69)/12)
def add(s,t,g=1,pan=0.5):
    i=int(t*SR); s=s[:max(0,n-i)]; L[i:i+len(s)]+=s*g*(1-pan)*1.4; R[i:i+len(s)]+=s*g*pan*1.4
def ts(d): return np.arange(int(d*SR))/SR
def celesta(f,d=1.6):
    t=ts(d); return (np.sin(2*np.pi*f*t)+0.4*np.sin(2*np.pi*f*4*t)*np.exp(-t*8)+0.15*np.sin(2*np.pi*f*2*t))*np.exp(-t*2.8)*np.minimum(t/0.003,1)
def bell(f,d=3):
    t=ts(d); s=0
    for k,a,dc in [(1,1,1.2),(2.76,0.5,2),(5.4,0.25,3),(0.5,0.4,0.8)]: s=s+a*np.sin(2*np.pi*f*k*t)*np.exp(-t*dc)
    return s*np.minimum(t/0.002,1)
def pad(fs,d):
    t=ts(d); s=0
    for f in fs:
        for dt in (-0.004,0,0.004): s=s+np.sin(2*np.pi*f*(1+dt)*t)+0.3*np.sin(2*np.pi*2*f*(1+dt)*t)
    e=np.minimum(t/0.6,1)*np.minimum((d-t)/0.6,1); return s*e/len(fs)
def pluckbass(f,d=1.2):
    t=ts(d); return (np.sin(2*np.pi*f*t)+0.3*np.sin(2*np.pi*2*f*t))*np.exp(-t*3)
def sleigh(d=0.12):
    t=ts(d); s=rng.standard_normal(len(t)); s=np.diff(s,prepend=0); s=np.diff(s,prepend=0)
    return s*np.exp(-t*30)*0.15
# chords per bar (F major waltz): F Dm Bb C / F Am Bb C ...
C={'F':[53,57,60],'Dm':[50,53,57],'Bb':[46,50,53],'C':[48,52,55],'Am':[45,48,52],'Gm':[43,46,50],'C7':[48,52,58]}
prog=['F','Dm','Bb','C','F','Am','Bb','C7','Dm','Am','Bb','F','Gm','C','F','F','Bb','C','F','F']
# original melody (bar -> list of (beat_offset, midi, dur))
mel={2:[(0,72,1),(1,74,1),(2,77,1)],3:[(0,76,2),(2,72,1)],4:[(0,77,1),(1,81,1),(2,79,1)],5:[(0,76,3)],
 6:[(0,74,1),(1,77,1),(2,81,1)],7:[(0,79,1.5),(1.5,77,0.5),(2,76,1)],8:[(0,74,1),(1,77,1),(2,81,1)],
 9:[(0,84,2),(2,81,1)],10:[(0,82,1),(1,81,1),(2,79,1)],11:[(0,77,3)],12:[(0,79,1),(1,82,1),(2,86,1)],
 13:[(0,84,1.5),(1.5,82,0.5),(2,79,1)],14:[(0,81,1),(1,84,1),(2,89,1)],15:[(0,88,3)],
 16:[(0,86,1),(1,84,1),(2,82,1)],17:[(0,81,1),(1,79,1),(2,76,1)],18:[(0,77,3)]}
for b,ch in enumerate(prog):
    t0=b*bar
    if t0>=D: break
    notes=C[ch]
    add(pad([mid(m+12) for m in notes],bar+0.6),t0,0.06)
    if b>=1:
        add(pluckbass(mid(notes[0]-12)),t0,0.35)
        for k in (1,2): add(sum(celesta(mid(m+12),0.6) for m in notes)/3,t0+k*beat,0.08,0.3 if k==1 else 0.7)
    if 1<=b<19:
        for k in range(6): add(sleigh(),t0+k*beat/2,0.6 if k%2 else 0.35,0.75)
    for off,m,d in mel.get(b,[]):
        add(celesta(mid(m),1.2+d*0.4),t0+off*beat,0.3,0.45)
        add(bell(mid(m+12),1.2),t0+off*beat,0.04,0.55)
# intro shimmer & 2027 chime & ending
for k,m in enumerate([77,81,84,89,93]): add(celesta(mid(m),2),0.2+k*0.18,0.2,0.2+0.15*k)
for t0 in (13.0,13.67,14.33): add(bell(mid(84),1.5),t0,0.3); add(bell(mid(72),1.5),t0,0.2)
for t0 in (15.0,): 
    tt=ts(2.5); add(np.sin(2*np.pi*np.cumsum(45+90*np.exp(-tt*12))/SR)*np.exp(-tt*2.2),t0,1.0)
    add(bell(mid(65),4),t0,0.4); add(bell(mid(77),4),t0,0.3); add(bell(mid(89),4),t0,0.15)
    add(np.diff(rng.standard_normal(int(2*SR)),prepend=0)*np.exp(-ts(2)*2.5)*0.4,t0,1)
for k in range(9): add(np.diff(rng.standard_normal(int(0.02*SR)),prepend=0)*np.exp(-ts(0.02)*300),9.0+k*0.5,0.5,0.6)
for tc in (3,4.5,6,7.5,9,15,21.5,26):
    w=rng.standard_normal(int(0.35*SR)); w=np.convolve(w,np.ones(12)/12,'same')*np.linspace(0,1,len(w))**2; add(w,tc-0.35,0.9)
for b in range(10):
    t0=15.0+b*1.5
    if t0>26.5: break
    tt=ts(0.4); add(np.sin(2*np.pi*np.cumsum(55+70*np.exp(-tt*25))/SR)*np.exp(-tt*8),t0,0.5)
    add(np.diff(rng.standard_normal(int(0.2*SR)),prepend=0)*np.exp(-ts(0.2)*20)*0.5,t0+1.0,0.5)
cl=ts(2.5); add((np.sin(2*np.pi*2600*cl)+0.6*np.sin(2*np.pi*3900*cl)+0.4*np.sin(2*np.pi*5300*cl))*np.exp(-cl*2.5)*np.minimum(cl/0.001,1),22.4,0.25)
add(sum(bell(mid(m),5) for m in [65,69,72,77]),27.0,0.15)
add(pad([mid(m) for m in [65,69,72,77]],3.0),27.0,0.08)
# reverb via FFT conv
ir_t=ts(2.2); ir=rng.standard_normal(len(ir_t))*np.exp(-ir_t*2.8); ir[0]=0
def conv(x):
    m=len(x)+len(ir); N2=1<<(m-1).bit_length()
    return np.fft.irfft(np.fft.rfft(x,N2)*np.fft.rfft(ir,N2),N2)[:len(x)]
ir2=ir.copy()
wl=conv(L); rng2=np.random.default_rng(9); ir=rng2.standard_normal(len(ir_t))*np.exp(-ir_t*2.8); ir[0]=0; wr=conv(R)
wl/=np.max(np.abs(wl)); wr/=np.max(np.abs(wr)); pk=max(np.max(np.abs(L)),np.max(np.abs(R)))
L=L/pk+wl*0.35; R=R/pk+wr*0.35
fade=np.ones(n); fade[-int(2*SR):]=np.linspace(1,0,int(2*SR)); fade[:int(0.05*SR)]=np.linspace(0,1,int(0.05*SR))
out=np.stack([L,R],1)*fade[:,None]; out=np.tanh(out/np.max(np.abs(out))*1.3)*0.88
w=wave.open("music.wav","wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((out*32767).astype('<i2').tobytes()); w.close()

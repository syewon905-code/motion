import numpy as np, math, sys, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from multiprocessing import Pool
W,H,FPS,DUR=1920,1080,30,30; N=FPS*DUR
FE="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FK="/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
_fc={}
def F(s,k=False):
    key=(int(s),k)
    if key not in _fc:_fc[key]=ImageFont.truetype(FK if k else FE,max(4,int(s)))
    return _fc[key]
def ease(t):t=max(0,min(1,t));return 1-(1-t)**3
def eio(t):t=max(0,min(1,t));return t*t*(3-2*t)
def eob(t):t=max(0,min(1,t));c=1.7;return 1+(c+1)*(t-1)**3+c*(t-1)**2
yy=np.linspace(0,1,H)[:,None]; xx=np.linspace(0,1,W)[None,:]
def grad(c1,c2):
    r=np.sqrt((xx-0.5)**2*2.5+(yy-0.55)**2); m=np.clip(r*1.25,0,1)[...,None]
    return (np.array(c1)*(1-m)+np.array(c2)*m)
BG1=grad((70,30,25),(8,5,10)); BG2=grad((120,40,35),(20,6,12)); BG3=grad((60,40,20),(6,4,8))
rng=random.Random(5)
SNOW=[(rng.random()*W,rng.random()*H,rng.uniform(1.5,6),rng.uniform(30,110),rng.random()*6) for _ in range(260)]
BOK=[(rng.random()*W,rng.random()*H,rng.uniform(20,90),rng.random()*6,rng.choice([(255,200,120),(255,160,90),(255,230,170),(220,90,70)])) for _ in range(45)]
GOLD=(255,214,140)
def bg(t):
    if t<10: a=BG1
    elif t<16: k=eio((t-10)/2); a=BG1*(1-k)+BG2*k
    else: k=eio((t-16)/2); a=BG2*(1-k)+BG3*k
    return Image.fromarray(a.astype(np.uint8)).convert("RGBA")
def bokeh(img,t,amt=1.0):
    L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    for x,y,r,p,c in BOK:
        x2=x+math.sin(t*0.3+p)*40; y2=y-t*8%H
        a=int(70*amt*(0.6+0.4*math.sin(t*1.5+p)))
        d.ellipse([x2-r,y2-r,x2+r,y2+r],fill=c+(a,))
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(6)))
def snow(d,t):
    for x,y,r,v,p in SNOW:
        y2=(y+t*v)%(H+20)-10; x2=x+math.sin(t*0.8+p)*30*r/4
        d.ellipse([x2-r,y2-r,x2+r,y2+r],fill=(255,250,240,int(120+20*r)))
def txt(d,s,cx,cy,size,fill,k=False,anchor="mm",sp=0):
    if sp==0: d.text((cx,cy),s,font=F(size,k),fill=fill,anchor=anchor); return
    f=F(size,k); ws=[d.textlength(c,font=f) for c in s]; tot=sum(ws)+sp*(len(s)-1); x=cx-tot/2
    for c,w in zip(s,ws): d.text((x+w/2,cy),c,font=f,fill=fill,anchor="mm"); x+=w+sp
def glowtext(img,s,cx,cy,size,col,a,k=False,sp=0,blur=18):
    L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L); txt(d,s,cx,cy,size,col+(a,),k,sp=sp)
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(blur))); img.alpha_composite(L)
def stagger(img,s,cx,cy,size,col,lt,k=False,per=0.06,dur=0.6,sp=10):
    f=F(size,k); d0=ImageDraw.Draw(img); ws=[d0.textlength(c,font=f) for c in s]
    tot=sum(ws)+sp*(len(s)-1); x=cx-tot/2
    L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    for i,(c,w) in enumerate(zip(s,ws)):
        p=ease((lt-i*per)/dur)
        if p>0: d.text((x+w/2,cy+(1-p)*60),c,font=f,fill=col+(int(255*p),),anchor="mm")
        x+=w+sp
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(14))); img.alpha_composite(L)
def digit_roll(img,cx,cy,size,frm,to,p,col):
    # vertical roll of a single digit inside a clip window
    f=F(size); L=Image.new("RGBA",(int(size*0.8),int(size*1.2)),(0,0,0,0)); d=ImageDraw.Draw(L)
    h=size*1.2; off=eio(p)*h
    d.text((L.width/2,h/2-off),str(frm),font=f,fill=col+(255,),anchor="mm")
    d.text((L.width/2,h/2+h-off),str(to),font=f,fill=col+(255,),anchor="mm")
    img.alpha_composite(L,(int(cx-L.width/2),int(cy-h/2)))
def firework(d,cx,cy,lt,col,n=40,R=260):
    if lt<0 or lt>2.2: return
    p=ease(lt/1.2); fade=max(0,1-lt/2.2)
    for i in range(n):
        a=i/n*6.283; r=R*p; x=cx+math.cos(a)*r; y=cy+math.sin(a)*r+lt*lt*30
        for k in range(4):
            rr=R*max(0,p-0.05*k); xx_=cx+math.cos(a)*rr; yy_=cy+math.sin(a)*rr+lt*lt*30
            s=4-k; d.ellipse([xx_-s,yy_-s,xx_+s,yy_+s],fill=col+(int(255*fade*(1-k/4)),))
def star(d,cx,cy,R,rot,fill):
    pts=[]
    for i in range(10):
        r=R if i%2==0 else R*0.42; a=rot+i*math.pi/5-math.pi/2
        pts.append((cx+math.cos(a)*r,cy+math.sin(a)*r))
    d.polygon(pts,fill=fill)
def frame(i):
    t=i/FPS; img=bg(t); bokeh(img,t, min(1,t/2))
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    if t<4:
        # thin golden line draws, then 2026 rises
        p=ease(t/1.6); d.rectangle([W/2-500*p,H/2+120,W/2+500*p,H/2+122],fill=GOLD+(200,))
        img.alpha_composite(ov); ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
        if t>0.6: stagger(img,"2026",W/2,H/2-20,260,GOLD,t-0.6,per=0.12,dur=0.9,sp=30)
        if t>1.8:
            a=int(255*ease((t-1.8)/0.8)); txt(d,"올 한 해도",W/2,H/2+190,54,(255,240,220,a),k=True)
        if t>3.4: a=int(255*(t-3.4)/0.6); d.rectangle([0,0,W,H],fill=(0,0,0,0))
    elif t<10:
        lt=t-4
        lines=[("고마웠어요",0.0,140),("함께해서",2.0,140),("따뜻했어요",3.8,140)]
        for s,st,sz in lines:
            if st<=lt<(st+2.0 if s!="따뜻했어요" else 99):
                q=lt-st
                img.alpha_composite(ov); ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
                out=1-ease((q-1.6)/0.4) if s!="따뜻했어요" else 1-ease((lt-5.6)/0.4)
                sc=1+0.04*q
                L=Image.new("RGBA",(W,H),(0,0,0,0)); stagger(L,s,W/2,H/2,int(sz*sc),(255,236,210),q,k=True,per=0.08,dur=0.5,sp=14)
                arr=np.array(L); arr[...,3]=(arr[...,3]*max(0,out)).astype(np.uint8); img.alpha_composite(Image.fromarray(arr))
        # side caption
        a=int(200*ease(lt/1)); txt(d,"THANK YOU, 2026",W/2,H*0.82,40,GOLD+(a,),sp=14)
    elif t<16:
        lt=t-10
        img.alpha_composite(ov); ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
        sz=320; f=F(sz); cx=W/2; cy=H/2-30
        L=Image.new("RGBA",(W,H),(0,0,0,0)); ld=ImageDraw.Draw(L)
        a=int(255*ease(lt/0.6))
        w3=ld.textlength("202",font=f); wd=ld.textlength("6",font=f); x0=cx-(w3+wd)/2
        ld.text((x0,cy),"202",font=f,fill=GOLD+(a,),anchor="lm")
        img.alpha_composite(L.filter(ImageFilter.GaussianBlur(20))); img.alpha_composite(L)
        # odometer: 6 -> 7 with overshoot ticks
        p=0 if lt<1.5 else min(1,(lt-1.5)/1.2)
        digit_roll(img,x0+w3+wd/2,cy,sz,6,7,p,GOLD if p<1 else (255,235,190))
        if lt>2.7:
            q=lt-2.7; r=ease(q/0.8)
            d.ellipse([cx-700*r,cy-700*r,cx+700*r,cy+700*r],outline=GOLD+(int(200*(1-r)),),width=6)
            a2=int(255*ease((q-0.3)/0.8))
            txt(d,"HELLO, 2027",W/2,H/2+190,56,(255,240,220,a2),sp=18)
        for k,(fx,fy,c,st) in enumerate([(380,300,(255,200,120),3.0),(1540,280,(255,140,110),3.4),(1300,180,(255,235,180),4.0),(560,160,(255,170,90),4.5)]):
            firework(d,fx,fy,lt-st,c)
    elif t<23:
        lt=t-16
        for k,(fx,fy,c,st) in enumerate([(300,250,(255,210,140),0.0),(1620,300,(255,150,110),0.8),(960,160,(255,235,180),2.2),(500,200,(255,170,90),3.5),(1400,180,(255,220,160),4.4)]):
            firework(d,fx,fy,lt-st,c,R=220)
        img.alpha_composite(ov); ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
        stagger(img,"새해 복 많이",W/2,H/2-90,150,(255,240,220),lt-0.3,k=True,per=0.1,dur=0.6,sp=12)
        stagger(img,"받으세요",W/2,H/2+90,150,GOLD,lt-1.3,k=True,per=0.12,dur=0.6,sp=12)
        if lt>3: a=int(220*ease((lt-3)/1)); txt(d,"WISHING YOU WARMTH & JOY",W/2,H*0.84,36,(255,230,200,a),sp=12)
        if lt>6.2: d.rectangle([0,0,W,H],fill=(0,0,0,int(160*ease((lt-6.2)/0.8))))
    else:
        lt=t-23
        s=eob(lt/0.8); star(d,W/2,H*0.25,60*s,lt*0.4,GOLD+(255,))
        img.alpha_composite(ov.filter(ImageFilter.GaussianBlur(20))); img.alpha_composite(ov)
        ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
        stagger(img,"HAPPY NEW YEAR",W/2,H/2,150,(255,240,220),lt-0.4,per=0.05,dur=0.6,sp=8)
        stagger(img,"2027",W/2,H/2+170,110,GOLD,lt-1.4,per=0.12,dur=0.6,sp=40)
        p=ease((lt-2.2)/1.2); d.rectangle([W/2-260*p,H/2+260,W/2+260*p,H/2+262],fill=GOLD+(200,))
        if lt>6.0: d.rectangle([0,0,W,H],fill=(0,0,0,min(255,int(255*(lt-6.0)/1.0))))
    snow(d,t)
    img.alpha_composite(ov)
    # vignette + grain
    img.convert("RGB").save(f"frames/f{i:04d}.jpg",quality=92)
if __name__=="__main__":
    import os; os.makedirs("frames",exist_ok=True)
    r=list(range(N)) if len(sys.argv)<2 else [int(x) for x in sys.argv[1:]]
    with Pool() as p: p.map(frame,r,chunksize=4)

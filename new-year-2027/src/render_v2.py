import numpy as np, math, sys, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from multiprocessing import Pool
W,H,FPS,DUR=1920,1080,30,30; N=FPS*DUR
FE="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"; FK="/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
_fc={}
def F(s,k=False):
    key=(int(s),k)
    if key not in _fc:_fc[key]=ImageFont.truetype(FK if k else FE,max(4,int(s)))
    return _fc[key]
def cl(t):return max(0,min(1,t))
def ease(t):t=cl(t);return 1-(1-t)**3
def eio(t):t=cl(t);return t*t*(3-2*t)
def eob(t):t=cl(t);c=1.7;return 1+(c+1)*(t-1)**3+c*(t-1)**2
def ein(t):t=cl(t);return t**3
GOLD=(255,214,140); CREAM=(255,240,220); RED=(200,50,50); GREEN=(40,120,80)
yy=np.linspace(0,1,H)[:,None]; xx=np.linspace(0,1,W)[None,:]
def vgrad(top,bot,cx=0.5,cy=0.5):
    r=np.clip(np.sqrt((xx-cx)**2*2+(yy-cy)**2)*1.3,0,1)[...,None]
    return Image.fromarray((np.array(top)*(1-r)+np.array(bot)*r).astype(np.uint8)).convert("RGBA")
SKY=vgrad((40,40,90),(6,8,25),0.5,0.2)
WARM=vgrad((140,60,40),(25,8,10)); WARM2=vgrad((90,45,30),(12,5,8)); NIGHT=vgrad((50,25,60),(5,3,12),0.5,0.4)
rng=random.Random(5)
SNOW=[[(rng.random()*W,rng.random()*H,rng.uniform(*sz),rng.uniform(*v),rng.random()*6) for _ in range(n)] for sz,v,n in [((1,2.5),(20,50),180),((2.5,4.5),(50,110),90),((6,11),(140,260),18)]]
BOK=[(rng.random()*W,rng.random()*H,rng.uniform(25,90),rng.random()*6,rng.choice([(255,200,120),(255,160,90),(255,230,170),(220,90,70)])) for _ in range(40)]
def snow(img,t,layers=(0,1,2),drift=0):
    L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    for li in layers:
        for x,y,r,v,p in SNOW[li]:
            y2=(y+t*v)%(H+40)-20; x2=(x+math.sin(t*0.8+p)*25*r/3+drift*(li+1))%W
            d.ellipse([x2-r,y2-r,x2+r,y2+r],fill=(255,250,240,150 if li<2 else 110))
    img.alpha_composite(L)
def bokeh(img,t,amt=1):
    L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    for x,y,r,p,c in BOK:
        x2=x+math.sin(t*0.3+p)*40; y2=(y-t*15)%H
        d.ellipse([x2-r,y2-r,x2+r,y2+r],fill=c+(int(60*amt*(0.6+0.4*math.sin(t*1.5+p))),))
    img.alpha_composite(L.filter(ImageFilter.GaussianBlur(5)))
def glow(img,L,b=18,k=1):
    g=L.filter(ImageFilter.GaussianBlur(b))
    for _ in range(k): img.alpha_composite(g)
    img.alpha_composite(L)
def T(d,s,cx,cy,size,fill,k=False,sp=0):
    f=F(size,k)
    if sp==0: d.text((cx,cy),s,font=f,fill=fill,anchor="mm"); return
    ws=[d.textlength(c,font=f) for c in s]; x=cx-(sum(ws)+sp*(len(s)-1))/2
    for c,w in zip(s,ws): d.text((x+w/2,cy),c,font=f,fill=fill,anchor="mm"); x+=w+sp
def stagger(img,s,cx,cy,size,col,lt,k=False,per=0.06,dur=0.5,sp=10,rise=60):
    f=F(size,k); d0=ImageDraw.Draw(img); ws=[d0.textlength(c,font=f) for c in s]
    x=cx-(sum(ws)+sp*(len(s)-1))/2; L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    for i,(c,w) in enumerate(zip(s,ws)):
        p=eob((lt-i*per)/dur)
        if p>0: d.text((x+w/2,cy+(1-p)*rise),c,font=f,fill=col+(int(255*cl(p)),),anchor="mm")
        x+=w+sp
    glow(img,L,14)
def camera(img,s=1.0,dx=0,dy=0,rot=0,shake=0,i=0):
    if shake: dx+=math.sin(i*7.3)*shake; dy+=math.cos(i*5.1)*shake
    if s==1 and dx==0 and dy==0 and rot==0: return img
    if rot: img=img.rotate(rot,resample=Image.BILINEAR,center=(W/2,H/2))
    a=1/s; return img.transform((W,H),Image.AFFINE,(a,0,W/2-a*W/2-dx*a,0,a,H/2-a*H/2-dy*a),resample=Image.BILINEAR)
# ---------- scenes ----------
def town(t):
    img=SKY.copy(); d=ImageDraw.Draw(img)
    r=random.Random(1)
    for _ in range(150):
        x,y=r.random()*W,r.random()*H*0.6; a=int(120+120*math.sin(t*3+x))
        d.ellipse([x-1.5,y-1.5,x+1.5,y+1.5],fill=(255,255,255,a))
    m=Image.new("RGBA",(W,H),(0,0,0,0)); md=ImageDraw.Draw(m); md.ellipse([1450,120,1610,280],fill=(255,245,220,255))
    glow(img,m,40,2)
    # hills
    d.polygon([(0,H)]+[(x,860+math.sin(x/300)*40) for x in range(0,W+1,20)]+[(W,H)],fill=(230,235,250,255))
    r=random.Random(3)
    L=Image.new("RGBA",(W,H),(0,0,0,0)); ld=ImageDraw.Draw(L)
    for k in range(11):
        x=k*180+r.uniform(-30,30); w=r.uniform(120,170); h=r.uniform(120,200); base=870+math.sin(x/300)*40
        ld.rectangle([x,base-h,x+w,base],fill=(40,30,45,255))
        ld.polygon([(x-15,base-h),(x+w/2,base-h-w*0.55),(x+w+15,base-h)],fill=(245,248,255,255))
        for wx in range(2):
            on=(t*2>k*0.3)
            col=(255,190,90,255) if on else (60,50,60,255)
            ld.rectangle([x+20+wx*(w/2),base-h*0.65,x+20+wx*(w/2)+w*0.25,base-h*0.65+38],fill=col)
            if on: d.ellipse([x+wx*(w/2)-20,base-h*0.75,x+w*0.6+wx*(w/2),base-h*0.3],fill=(255,170,80,60))
        ld.rectangle([x+w*0.7,base-h-w*0.4,x+w*0.82,base-h-w*0.15],fill=(40,30,45,255))
        # smoke
        for s in range(6):
            q=(t*0.5+s/6+k*0.13)%1; sx=x+w*0.76+math.sin(q*6+k)*20*q; sy=base-h-w*0.4-q*160
            ld.ellipse([sx-10-q*20,sy-10-q*20,sx+10+q*20,sy+10+q*20],fill=(220,220,230,int(90*(1-q))))
    img.alpha_composite(L)
    return img
def tree(t,lt):
    img=WARM.copy(); bokeh(img,t); L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    cx=W/2; g=ease(lt/0.6)
    for k,(y,w) in enumerate([(330,260),(470,360),(620,460)]):
        s=eob((lt-k*0.1)/0.5); d.polygon([(cx,y-200*s),(cx-w*s,y+130*s),(cx+w*s,y+130*s)],fill=(30,100+k*12,65,255))
    d.rectangle([cx-40,750,cx+40,840],fill=(90,55,35,255))
    Lg=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(Lg); r=random.Random(9)
    for j in range(46):
        yv=r.uniform(170,740); half=(yv-120)/620*440*r.uniform(0.2,0.95)*(1 if r.random()<.5 else -1)
        on=0.5+0.5*math.sin(t*6+j*1.7); c=[(255,210,120),(255,90,80),(120,200,255),(255,240,200)][j%4]
        if lt>0.4+j*0.01: gd.ellipse([cx+half-9,yv-9,cx+half+9,yv+9],fill=c+(int(140+115*on),))
    s=eob((lt-0.5)/0.5); 
    pts=[(cx+math.cos(-math.pi/2+i*math.pi/5)*(60 if i%2==0 else 25)*s,130+math.sin(-math.pi/2+i*math.pi/5)*(60 if i%2==0 else 25)*s) for i in range(10)]
    gd.polygon(pts,fill=GOLD+(255,))
    img.alpha_composite(L); glow(img,Lg,16,2)
    return img
def mug(t,lt):
    img=WARM2.copy(); bokeh(img,t); L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    cx,cy=W/2,H/2+120
    d.ellipse([cx-380,cy+170,cx+380,cy+230],fill=(0,0,0,90))
    d.rounded_rectangle([cx-220,cy-200,cx+220,cy+200],radius=60,fill=RED+(255,))
    d.ellipse([cx+170,cy-110,cx+360,cy+110],outline=RED+(255,),width=42)
    d.ellipse([cx-220,cy-240,cx+220,cy-160],fill=(90,45,30,255))
    for k in range(6):  # pattern
        x=cx-170+k*68; d.polygon([(x,cy+20),(x+20,cy-15),(x+40,cy+20),(x+20,cy+55)],fill=(255,240,230,255))
    S=Image.new("RGBA",(W,H),(0,0,0,0)); sd=ImageDraw.Draw(S)
    for k in range(3):
        pts=[(cx-80+k*80+math.sin(y/45+t*3+k)*28,cy-240-y) for y in range(0,int(380*ease(lt/0.8)),6)]
        if len(pts)>1: sd.line(pts,fill=(255,250,240,150),width=14,joint="curve")
    img.alpha_composite(L); img.alpha_composite(S.filter(ImageFilter.GaussianBlur(7)))
    return img
CONF=[(random.Random(i).uniform(-1,1),random.Random(i+99).uniform(0.4,1.2),random.Random(i+7).choice([(255,214,140),(230,70,70),(255,255,255),(120,200,255),(80,190,120)])) for i in range(140)]
def gift(t,lt):
    img=WARM.copy(); bokeh(img,t); L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    cx,cy=W/2,H/2+170; wob=math.sin(lt*30)*6*(1-cl((lt-0.5)/0.3)) if lt<0.8 else 0
    d.rectangle([cx-230+wob,cy-180,cx+230+wob,cy+170],fill=(30,110,75,255)); d.rectangle([cx-30+wob,cy-180,cx+30+wob,cy+170],fill=GOLD+(255,))
    op=ease((lt-0.6)/0.35); ly=cy-180-op*260; la=-op*25
    lid=Image.new("RGBA",(560,140),(0,0,0,0)); ld=ImageDraw.Draw(lid)
    ld.rectangle([20,60,540,130],fill=(35,125,85,255)); ld.rectangle([250,60,310,130],fill=GOLD+(255,))
    ld.ellipse([170,0,280,70],outline=GOLD+(255,),width=18); ld.ellipse([280,0,390,70],outline=GOLD+(255,),width=18)
    lid=lid.rotate(la,expand=True,resample=Image.BILINEAR); L.alpha_composite(lid,(int(cx-lid.width/2+op*120+wob),int(ly-lid.height+70)))
    if lt>0.65:
        q=lt-0.65; Lg=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(Lg)
        gd.ellipse([cx-300,cy-450,cx+300,cy-50],fill=(255,220,150,int(160*cl(1-q/1.2))))
        img.alpha_composite(Lg.filter(ImageFilter.GaussianBlur(60)))
        for a,v,c in CONF:
            x=cx+a*v*1400*ease(q/0.9)+math.sin(q*8+a*9)*20; y=cy-200-v*900*ease(q/0.7)+q*q*350
            s=10; ang=q*9+a*5
            d.polygon([(x+math.cos(ang)*s,y+math.sin(ang)*s*0.4),(x-math.cos(ang)*s,y-math.sin(ang)*s*0.4),(x+math.sin(ang)*4,y-math.cos(ang)*8)],fill=c+(255,))
    img.alpha_composite(L); return img
def clock(t,lt):
    img=NIGHT.copy(); bokeh(img,t,0.7); L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    cx,cy,R=W/2,H/2,360
    d.ellipse([cx-R-24,cy-R-24,cx+R+24,cy+R+24],fill=GOLD+(255,)); d.ellipse([cx-R,cy-R,cx+R,cy+R],fill=(250,243,228,255))
    for k in range(60):
        a=k/60*6.283; r1=R-(46 if k%5==0 else 22)
        d.line([(cx+math.cos(a)*r1,cy+math.sin(a)*r1),(cx+math.cos(a)*(R-10),cy+math.sin(a)*(R-10))],fill=(60,40,40,255),width=8 if k%5==0 else 3)
    p=eio(lt/3.2); mins=55+5*p+ (0)  # hands sweep to 12
    sweep=(1-p)*720  # extra spin
    am=math.radians(mins*6-90-sweep); ah=math.radians((11+mins/60)*30-90-sweep/12)
    d.line([(cx,cy),(cx+math.cos(ah)*R*0.5,cy+math.sin(ah)*R*0.5)],fill=(40,25,25,255),width=22)
    d.line([(cx,cy),(cx+math.cos(am)*R*0.8,cy+math.sin(am)*R*0.8)],fill=(40,25,25,255),width=12)
    sa=math.radians(lt*360*1.2-90); d.line([(cx,cy),(cx+math.cos(sa)*R*0.88,cy+math.sin(sa)*R*0.88)],fill=RED+(255,),width=4)
    d.ellipse([cx-20,cy-20,cx+20,cy+20],fill=RED+(255,))
    img.alpha_composite(L); return img
def countdown(t,lt):
    img=NIGHT.copy(); bokeh(img,t,1); d=ImageDraw.Draw(img); k=int(lt); q=lt-k
    num=str(3-k) if k<3 else ""
    # radial burst lines
    L=Image.new("RGBA",(W,H),(0,0,0,0)); ld=ImageDraw.Draw(L)
    for j in range(36):
        a=j/36*6.283+k; r0=200+q*900; r1=r0+200
        ld.line([(W/2+math.cos(a)*r0,H/2+math.sin(a)*r0),(W/2+math.cos(a)*r1,H/2+math.sin(a)*r1)],fill=GOLD+(int(200*(1-q)),),width=6)
    r=ease(q/0.5)*700; ld.ellipse([W/2-r,H/2-r,W/2+r,H/2+r],outline=GOLD+(int(255*(1-q)),),width=10)
    img.alpha_composite(L)
    s=1.6-0.6*eob(q/0.35)+0.1*q
    Lt=Image.new("RGBA",(W,H),(0,0,0,0)); T(ImageDraw.Draw(Lt),num,W/2,H/2,int(520*s),CREAM+(255,))
    glow(img,Lt,30,2); return img
FW=[]
r=random.Random(11)
for k in range(16):
    FW.append((r.uniform(200,W-200),r.uniform(130,520),r.choice([(255,210,140),(255,110,100),(140,200,255),(255,240,200),(200,140,255),(120,230,170)]),r.uniform(0,4.8),r.uniform(220,380),r.randint(36,60)))
def fireworks(img,lt):
    L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    for cx,cy,c,st,R,n in FW:
        q=lt-st
        if -0.6<q<0:  # rising rocket
            p=(q+0.6)/0.6; y=H-(H-cy)*ease(p); d.ellipse([cx-4,y-4,cx+4,y+4],fill=(255,240,200,255))
            for s in range(8): d.ellipse([cx-2,y+s*14-2,cx+2,y+s*14+2],fill=(255,200,120,int(200*(1-s/8))))
        if 0<=q<2.4:
            p=ease(q/1.0); fade=cl(1-q/2.4)
            for i in range(n):
                a=i/n*6.283
                for tr in range(6):
                    rr=R*max(0,p-tr*0.04); x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr+q*q*45
                    s=5-tr*0.7; d.ellipse([x-s,y-s,x+s,y+s],fill=c+(int(255*fade*(1-tr/6)),))
            if q<0.15: d.ellipse([cx-40,cy-40,cx+40,cy+40],fill=(255,255,240,int(200*(1-q/0.15))))
    glow(img,L,10,2)
def glasses(t,lt):
    img=WARM2.copy(); bokeh(img,t,1.2); L=Image.new("RGBA",(W,H),(0,0,0,0))
    def glass(tilt):
        g0=Image.new("RGBA",(300,720),(0,0,0,0)); gd=ImageDraw.Draw(g0)
        gd.polygon([(60,20),(240,20),(205,330),(95,330)],fill=(255,255,255,50),outline=(255,255,255,200))
        gd.polygon([(70,110),(230,110),(205,330),(95,330)],fill=(250,200,100,220))
        for b in range(10):
            by=330-((t*120+b*37)%220); bx=110+(b*29)%80; gd.ellipse([bx-4,by-4,bx+4,by+4],fill=(255,250,220,230))
        gd.rectangle([142,330,158,620],fill=(255,255,255,170)); gd.ellipse([70,600,230,650],fill=(255,255,255,150))
        g=Image.new("RGBA",(900,720),(0,0,0,0)); g.alpha_composite(g0,(300,0)); return g.rotate(tilt,resample=Image.BILINEAR,center=(450,620))
    p=eio(lt/0.9); hit=lt>0.9
    gap=360*(1-p); tilt=18*p
    L.alpha_composite(glass(-tilt),(int(W/2-730-gap),220)); L.alpha_composite(glass(tilt),(int(W/2-170+gap),220))
    img.alpha_composite(L)
    if hit:
        q=lt-0.9; S=Image.new("RGBA",(W,H),(0,0,0,0)); sd=ImageDraw.Draw(S); cx,cy=W/2,250
        rr=ease(q/0.4)*300; sd.ellipse([cx-rr,cy-rr,cx+rr,cy+rr],outline=(255,240,200,int(255*cl(1-q/0.6))),width=6)
        rnd=random.Random(4)
        for j in range(60):
            a=rnd.random()*6.283; v=rnd.uniform(200,700); x=cx+math.cos(a)*v*ease(q/1.2); y=cy+math.sin(a)*v*ease(q/1.2)+q*q*120
            s=rnd.uniform(3,8)*cl(1-q/2.5); sd.polygon([(x,y-s*2),(x+s*0.5,y),(x,y+s*2),(x-s*0.5,y)],fill=GOLD+(255,)); sd.polygon([(x-s*2,y),(x,y+s*0.5),(x+s*2,y),(x,y-s*0.5)],fill=GOLD+(255,))
        glow(img,S,8,2)
    return img
PART=[(random.Random(i).uniform(0,W),random.Random(i+5).uniform(0,H)) for i in range(500)]
def finale(t,lt):
    img=NIGHT.copy(); bokeh(img,t,1); fireworks(img,lt+3)
    # particles converge
    L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L); p=eio(lt/1.4)
    for k,(x,y) in enumerate(PART):
        a=k*2.39996; tr=60+(k%50)*9; tx=W/2+math.cos(a)*tr*1.6; ty=H/2+math.sin(a)*tr*0.55
        X=x+(tx-x)*p; Y=y+(ty-y)*p; s=3 if p<1 else 2
        d.ellipse([X-s,Y-s,X+s,Y+s],fill=GOLD+(int(255*(1-0.7*cl((lt-1.4)/0.6))),))
    glow(img,L,6)
    if lt>1.2:
        stagger(img,"HAPPY NEW YEAR",W/2,H/2-30,150,CREAM,lt-1.2,per=0.05,dur=0.5,sp=8)
        stagger(img,"2027",W/2,H/2+140,110,GOLD,lt-1.9,per=0.1,dur=0.5,sp=40)
    if lt>2.6:
        Lt=Image.new("RGBA",(W,H),(0,0,0,0)); T(ImageDraw.Draw(Lt),"새해 복 많이 받으세요",W/2,H/2+270,50,CREAM+(int(255*ease((lt-2.6)/0.8)),),k=True,sp=6); img.alpha_composite(Lt)
    return img
def caption(img,s,lt,k=True,y=H*0.86,size=72):
    if lt<0: return
    a=cl(lt/0.3)*cl((1.45-lt)/0.2) if lt<1.5 else 0
    if a<=0: return
    L=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(L)
    f=F(size,k); w=d.textlength(s,font=f); x0=W/2-w/2-40
    d.rounded_rectangle([x0,y-size*0.85,x0+(w+80)*ease(lt/0.3),y+size*0.85],radius=size*0.85,fill=(20,8,8,int(160*a)))
    T(d,s,W/2+(1-ease(lt/0.4))*60,y,size,CREAM+(int(255*a),),k=k)
    img.alpha_composite(L)
def frame(i):
    t=i/FPS; s=1; dx=dy=0; rot=0; shake=0
    if t<3:
        img=town(t); s=1.25-0.2*eio(t/3); dy=-120*(1-eio(t/3))
        snow(img,t)
        if t>1.0: stagger(img,"2026",W/2,H*0.36,200,CREAM,t-1.0,per=0.1,dur=0.6,sp=30)
    elif t<9:
        lt=t-3; seg=int(lt/1.5); q=lt-seg*1.5
        img=[tree,mug,gift,tree][seg](t,q) if seg<3 else None
        if seg==3: img=town(t)
        caption(img,["메리 크리스마스","따뜻한 한 잔","고마운 마음","올해도 고마웠어요"][seg],q)
        snow(img,t,drift=0)
        s=1.05+0.06*q; 
        # whip pan in/out
        if q<0.18: dx=W*0.6*(1-ease(q/0.18))
        if q>1.32: dx=-W*0.6*ein((q-1.32)/0.18)
        rot=(1 if seg%2 else -1)*1.2*(q-0.75)
    elif t<12.5:
        lt=t-9; img=clock(t,lt); snow(img,t,(0,1)); s=0.9+0.25*eio(lt/3.5)
        Lt=Image.new("RGBA",(W,H),(0,0,0,0)); 
        if lt>0.3: caption(img,"2026년의 마지막 순간",lt-0.3)
        if lt>1.9: caption(img,"11 : 59 : 57",lt-1.9,k=False)
    elif t<15:
        lt=t-12.5
        if lt<0.5: img=clock(t,3.5); s=1.15+ein(lt/0.5)*3
        else: img=countdown(t,(lt-0.5)*1.5 if False else (lt-0.5)/ (2.0/3)); shake=max(0,(0.15-((lt-0.5)%(2/3))))*120
        snow(img,t,(0,1))
    elif t<21.5:
        lt=t-15; img=NIGHT.copy(); bokeh(img,t,1.3)
        # light rays
        R=Image.new("RGBA",(W,H),(0,0,0,0)); rd=ImageDraw.Draw(R)
        for j in range(16):
            a=j/16*6.283+lt*0.25; rd.polygon([(W/2,H/2),(W/2+math.cos(a)*2200,H/2+math.sin(a)*2200),(W/2+math.cos(a+0.12)*2200,H/2+math.sin(a+0.12)*2200)],fill=(255,210,140,int(40*ease(lt/0.5))))
        img.alpha_composite(R.filter(ImageFilter.GaussianBlur(10)))
        fireworks(img,lt)
        sc=2.2-1.2*eob(lt/0.5)
        Lt=Image.new("RGBA",(W,H),(0,0,0,0)); T(ImageDraw.Draw(Lt),"2027",W/2,H/2,int(380*sc),GOLD+(255,),sp=20); glow(img,Lt,30,3)
        if lt>1.0: stagger(img,"HELLO, NEW YEAR",W/2,H/2+260,64,CREAM,lt-1.0,per=0.04,dur=0.5,sp=10)
        # confetti
        Lc=Image.new("RGBA",(W,H),(0,0,0,0)); cd=ImageDraw.Draw(Lc)
        for j,(a,v,c) in enumerate(CONF):
            x=(W/2+a*W*0.6+math.sin(lt*3+j)*40)%W; y=-50+((lt*v*420+j*37)%(H+100)); ang=lt*6+j
            cd.polygon([(x+math.cos(ang)*10,y+math.sin(ang)*4),(x-math.cos(ang)*10,y-math.sin(ang)*4),(x,y+9)],fill=c+(255,))
        img.alpha_composite(Lc)
        s=1+0.05*lt; shake=max(0,0.4-lt)*90
        if lt<0.25: img.alpha_composite(Image.new("RGBA",(W,H),(255,250,235,int(255*(1-lt/0.25)))))
    elif t<26:
        lt=t-21.5; img=glasses(t,lt); snow(img,t,(0,1))
        s=1.08-0.06*eio(lt/4.5); shake=max(0,(0.12-(lt-0.9)))*60 if lt>0.9 else 0
        if lt>1.3: stagger(img,"새해 복 많이 받으세요",W/2,H*0.86,92,CREAM,lt-1.3,k=True,per=0.07,dur=0.5,sp=8)
    else:
        lt=t-26; img=finale(t,lt); snow(img,t); s=1+0.03*lt
        if lt>3.0: img.alpha_composite(Image.new("RGBA",(W,H),(0,0,0,int(255*cl((lt-3.0)/1.0)))))
    # light leak
    lk=Image.new("RGBA",(W,H),(0,0,0,0)); ld=ImageDraw.Draw(lk); x=(t*260)%(W*2)-W/2
    ld.ellipse([x-500,-300,x+500,500],fill=(255,170,90,40)); img.alpha_composite(lk.filter(ImageFilter.GaussianBlur(120)))
    img=camera(img,s,dx,dy,rot,shake,i)
    for ct in (3,4.5,6,7.5,9,13.0,13.67,14.33,15,21.5,26):
        if 0<=t-ct<0.1: img.alpha_composite(Image.new("RGBA",(W,H),(255,245,230,int(150*(1-(t-ct)/0.1)))))
    img.convert("RGB").save(f"frames2/f{i:04d}.jpg",quality=90)
if __name__=="__main__":
    import os; os.makedirs("frames2",exist_ok=True)
    rr=list(range(N)) if len(sys.argv)<2 else [int(x) for x in sys.argv[1:]]
    with Pool() as p: p.map(frame,rr,chunksize=3)

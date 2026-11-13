import numpy as np, math, sys, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from multiprocessing import Pool
W,H,FPS,DUR=1920,1080,30,30
N=FPS*DUR
FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_fc={}
def F(s):
    s=int(s)
    if s not in _fc:_fc[s]=ImageFont.truetype(FB,s)
    return _fc[s]
def ease(t):t=max(0,min(1,t));return 1-(1-t)**3
def eob(t):  # ease out back
    t=max(0,min(1,t));c=1.9;return 1+(c+1)*(t-1)**3+c*(t-1)**2
rng=random.Random(7)
BUB=[(rng.random()*W,rng.random()*H*1.5,rng.uniform(3,18),rng.uniform(120,420)) for _ in range(160)]
yy=np.linspace(0,1,H)[:,None]; xx=np.linspace(0,1,W)[None,:]
def grad(c1,c2,t):
    r=np.sqrt((xx-0.5)**2*3+(yy-0.45)**2)
    m=np.clip(r*1.3,0,1)[...,None]
    a=np.array(c1)*(1-m)+np.array(c2)*m
    return Image.fromarray(a.astype(np.uint8))
BG_BLUE=grad((40,120,255),(0,10,60),0)
BG_BLACK=grad((25,30,45),(0,0,0),0)
BG_ICE=grad((200,235,255),(40,140,230),0)
def bubbles(d,t,col=(255,255,255),k=1.0):
    for x,y,r,v in BUB:
        yy_=(y-t*v*k)%(H*1.5)-H*0.25
        xx_=x+math.sin(t*2+y)*12
        d.ellipse([xx_-r,yy_-r,xx_+r,yy_+r],outline=col+(170,),width=2)
        d.ellipse([xx_-r*0.5,yy_-r*0.6,xx_-r*0.1,yy_-r*0.2],fill=col+(200,))
def ctext(d,s,cx,cy,size,fill,anchor="mm",stroke=0,sc=None):
    d.text((cx,cy),s,font=F(size),fill=fill,anchor=anchor,stroke_width=stroke,stroke_fill=sc)
def can(img,cx,cy,h,rot=0.0):
    w=int(h*0.42); h=int(h)
    c=Image.new("RGBA",(w,h),(0,0,0,0)); d=ImageDraw.Draw(c)
    # body with cylindrical shading
    xs=np.linspace(-1,1,w); sh=np.clip(0.35+0.65*np.cos(xs*1.3+rot*0.5)**2,0,1)
    spec=np.exp(-((xs-0.45+rot*0.2)**2)/0.004)*0.8
    body=np.zeros((h,w,4),np.uint8)
    base=np.array([12,14,20])
    col=(base[None,:]*sh[:,None]+255*spec[:,None]).clip(0,255)
    body[:,:,:3]=col[None,:,:].astype(np.uint8); body[:,:,3]=255
    c=Image.fromarray(body,"RGBA")
    # rounded mask
    m=Image.new("L",(w,h),0); md=ImageDraw.Draw(m)
    md.rounded_rectangle([0,int(h*0.04),w-1,h-1],radius=int(w*0.18),fill=255)
    md.rectangle([int(w*0.08),0,int(w*0.92),int(h*0.1)],fill=255)
    d=ImageDraw.Draw(c)
    # top rim
    d.rectangle([0,0,w,int(h*0.06)],fill=(170,175,185,255))
    d.rectangle([0,int(h*0.06),w,int(h*0.075)],fill=(90,95,105,255))
    d.rectangle([0,h-int(h*0.04),w,h],fill=(150,155,165,255))
    # blue wave band
    ph=rot*w*0.6
    pts=[(x,int(h*0.62+math.sin((x+ph)/w*6.28)*h*0.03)) for x in range(0,w+1,4)]
    d.polygon(pts+[(w,int(h*0.7)),(0,int(h*0.7))],fill=(0,90,255,255))
    pts2=[(x,int(h*0.66+math.sin((x+ph)/w*6.28+1)*h*0.025)) for x in range(0,w+1,4)]
    d.polygon(pts2+[(w,int(h*0.73)),(0,int(h*0.73))],fill=(230,20,50,255))
    # rotated text "ZERO" vertical-ish
    tx=Image.new("RGBA",(h,w),(0,0,0,0)); td=ImageDraw.Draw(tx)
    off=int(math.sin(rot)*w*0.15)
    td.text((h*0.3,w/2+off),"ZERO",font=F(w*0.42),fill=(255,255,255,255),anchor="mm")
    tx=tx.rotate(90,expand=True); c.alpha_composite(tx,(0,-int(h*0.2)))
    d.text((w/2+off,h*0.84),"SUGAR",font=F(w*0.13),fill=(0,140,255,255),anchor="mm")
    # re-apply shading overlay
    shade=np.zeros((h,w,4),np.uint8); shade[:,:,3]=((1-sh)*140).astype(np.uint8)[None,:]
    c.alpha_composite(Image.fromarray(shade,"RGBA"))
    hl=np.zeros((h,w,4),np.uint8); hl[:,:,:3]=255; hl[:,:,3]=(spec*170).astype(np.uint8)[None,:]
    c.alpha_composite(Image.fromarray(hl,"RGBA"))
    c.putalpha(Image.fromarray(np.minimum(np.array(c)[:,:,3],np.array(m))))
    # condensation drops
    dd=ImageDraw.Draw(c); r2=random.Random(3)
    for _ in range(int(w*0.25)):
        x=r2.random()*w; y=h*0.12+r2.random()*h*0.8; r=r2.uniform(1.5,w*0.012)
        dd.ellipse([x-r,y-r,x+r,y+r*1.3],fill=(255,255,255,90))
    glow=Image.new("RGBA",img.size,(0,0,0,0)); gd=ImageDraw.Draw(glow)
    gd.ellipse([cx-w,cy-h*0.6,cx+w,cy+h*0.6],fill=(60,160,255,90))
    glow=glow.filter(ImageFilter.GaussianBlur(80)); img.alpha_composite(glow)
    img.alpha_composite(c,(int(cx-w/2),int(cy-h/2)))
def frame(i):
    t=i/FPS
    if t<3: img=BG_BLACK.copy().convert("RGBA")
    elif t<8: img=(BG_BLUE if int(t*4)%2==0 or t>4 else BG_BLACK).copy().convert("RGBA")
    elif t<14: img=BG_BLUE.copy().convert("RGBA")
    elif t<22: img=[BG_BLUE,BG_BLACK,BG_ICE][int((t-14)/(8/6))%3].copy().convert("RGBA")
    else: img=BG_BLUE.copy().convert("RGBA")
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    shake=0
    if t<3:
        k=ease(t/1.5)
        bubbles(d,t,k=0.3+t)
        ctext(d,"psst...",W/2,H/2,int(60+40*k),(255,255,255,int(255*min(1,t*2))))
        if t>2.4:
            a=int(255*(1-(t-2.4)/0.6)); ctext(d,"TSSSS!",W/2,H/2+150,140+int((t-2.4)*200),(0,160,255,a))
    elif t<8:
        lt=t-3; bubbles(d,t,k=2)
        words=[("ZERO",0.0),("SUGAR.",1.2),("ZERO",2.4),("COMPROMISE.",3.4)]
        for j,(w_,st) in enumerate(words):
            if lt>=st and (j+1>=len(words) or lt<words[j+1][1]+0.15):
                p=(lt-st)/0.35; s=eob(p)
                size=int((420 if len(w_)<6 else 230)*(2.2-1.2*s))
                a=int(255*min(1,p*2))
                ctext(d,w_,W/2,H/2,size,(255,255,255,a),stroke=4,sc=(0,40,140,a))
                shake=max(0,(0.25-(lt-st)))*60
        # thin line sweep
        x=(lt%1.2)/1.2*W; d.rectangle([x-400,H*0.82,x,H*0.82+6],fill=(255,255,255,200))
    elif t<14:
        lt=t-8; bubbles(d,t,k=1.5)
        img.alpha_composite(ov); ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
        s=ease(lt/1.2); ch=max(60,820*s)
        cx=W/2+(0 if lt<2 else -380*ease((lt-2)/0.8))
        can(img,cx,H/2+40+(1-s)*500+math.sin(t*2)*10,ch,rot=lt*0.8)
        if lt>2.2:
            for j,(w_,yo) in enumerate([("MAXIMUM",-140),("TASTE",40),("ZERO SUGAR",190)]):
                p=ease((lt-2.2-j*0.35)/0.5)
                if p>0:
                    sz=[120,190,70][j]
                    ctext(d,w_,W*0.47+(1-p)*900,H/2+yo,sz,(255,255,255,int(255*p)),anchor="lm")
    elif t<22:
        lt=t-14; seg=int(lt/(8/6)); sl=lt-seg*(8/6)
        bg=seg%3
        col=[(255,255,255),(0,150,255),(10,40,120)][bg]
        bubbles(d,t,col=(255,255,255) if bg!=2 else (255,255,255),k=3)
        word=["ICE","COLD","CRISP","BOLD","FIZZ","REFRESH"][seg%6]
        p=eob(sl/0.3)
        # stacked repeating outlines (kinetic echo)
        for e in range(4,0,-1):
            ctext(d,word,W/2,H/2-e*110*p+ (0),300,(0,0,0,0),stroke=3,sc=col+(60*e//2,))
            ctext(d,word,W/2,H/2+e*110*p,300,(0,0,0,0),stroke=3,sc=col+(60*e//2,))
        sc=1+0.08*sl
        ctext(d,word,W/2,H/2,int(300*sc*(0.5+0.5*p)),col+(255,))
        # ice cubes
        for k in range(5):
            r=random.Random(seg*10+k); x=r.random()*W; y=r.random()*H; s_=r.uniform(60,140)
            a=t*r.uniform(-60,60)+r.random()*90
            cube=Image.new("RGBA",(int(s_*1.6),int(s_*1.6)),(0,0,0,0)); cd=ImageDraw.Draw(cube)
            cd.rounded_rectangle([s_*0.3,s_*0.3,s_*1.3,s_*1.3],radius=s_*0.2,fill=(220,245,255,110),outline=(255,255,255,200),width=3)
            cube=cube.rotate(a); ov.alpha_composite(cube,(int(x),int(y)))
        shake=max(0,(0.15-sl))*80
    else:
        lt=t-22; bubbles(d,t,k=1)
        img.alpha_composite(ov); ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
        s=ease(lt/0.8)
        can(img,W/2,H/2-30,700+120*s+lt*8,rot=lt*0.4)
        if lt>0.6:
            p=ease((lt-0.6)/0.6)
            ctext(d,"PEPSI",W/2-560*p,H/2-60,170,(255,255,255,int(255*p)))
            ctext(d,"ZERO",W/2+560*p,H/2-60,170,(255,255,255,int(255*p)))
        if lt>2:
            p=ease((lt-2)/0.7)
            ctext(d,"ZERO SUGAR. ALL THE FIZZ.",W/2,H*0.9,70,(255,255,255,int(255*p)))
        if lt>7.4:
            a=int(255*(lt-7.4)/0.6); d.rectangle([0,0,W,H],fill=(0,0,0,min(255,a)))
    img.alpha_composite(ov)
    # flash on cuts
    for ct in [3,8,14,22]:
        if 0<=t-ct<0.12:
            fl=Image.new("RGBA",(W,H),(255,255,255,int(255*(1-(t-ct)/0.12)))); img.alpha_composite(fl)
    if shake: img=img.transform(img.size,Image.AFFINE,(1,0,math.sin(i*7)*shake,0,1,math.cos(i*5)*shake))
    img.convert("RGB").save(f"frames/f{i:04d}.jpg",quality=92)
if __name__=="__main__":
    import os; os.makedirs("frames",exist_ok=True)
    rng_=list(range(N)) if len(sys.argv)<2 else [int(x) for x in sys.argv[1:]]
    with Pool() as p: p.map(frame,rng_,chunksize=4)

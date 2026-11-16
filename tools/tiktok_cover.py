import sys, json, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
src, frac, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
lines = json.loads(sys.argv[4]); accent = sys.argv[5] if len(sys.argv)>5 else ""
d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',src]))
subprocess.run(['ffmpeg','-v','error','-y','-ss',str(d*frac),'-i',src,'-frames:v','1','/tmp/bg.png'],check=True)
bg=Image.open('/tmp/bg.png').convert('RGB').resize((1080,1920))
bg=ImageEnhance.Brightness(bg).enhance(0.8)
# dark gradient over lower half to hide burned captions
grad=Image.new('L',(1,1920))
for y in range(1920):
    v=0 if y<650 else min(252,int((y-650)/330*252))
    grad.putpixel((0,y),v)
grad=grad.resize((1080,1920))
dark=Image.new('RGB',(1080,1920),(6,10,30))
im=Image.composite(dark,bg,grad)
dr=ImageDraw.Draw(im)
bold='/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
# brand tag
tag=ImageFont.truetype(bold,40)
t="what ai does next"
w=dr.textlength(t,font=tag)
dr.rounded_rectangle((90,1040,90+w+50,1040+70),radius=35,fill=(124,92,255))
dr.text((115,1046),t,font=tag,fill='white')
# headline
size=104
f=ImageFont.truetype(bold,size)
while max(dr.textlength(l,font=f) for l in lines)>840: size-=4; f=ImageFont.truetype(bold,size)
y=1140
acc=set(w.strip("?!.,") for w in accent.split()) if accent else set()
for l in lines:
    x=90
    for word in l.split(' '):
        col=(255,214,64) if word.strip('?!.,') in acc else (255,255,255)
        dr.text((x+4,y+5),word,font=f,fill=(0,0,0))
        dr.text((x,y),word,font=f,fill=col)
        x+=dr.textlength(word+' ',font=f)
    y+=int(size*1.12)
im.save(out,quality=95)

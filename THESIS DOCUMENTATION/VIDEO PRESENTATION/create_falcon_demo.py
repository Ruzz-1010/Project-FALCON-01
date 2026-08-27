#!/usr/bin/env python3
"""Render the Project FALCON 150-second animated demo with original music."""
from __future__ import annotations

import math
import shutil
import subprocess
import sys
import wave
from array import array
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
OUT = ROOT / "Project_FALCON_Animated_Demo_V2_1080p.mp4"
MUSIC = ROOT / "falcon_ambient_original.wav"
FFMPEG = Path(shutil.which("ffmpeg") or "/tmp/falcon-ffmpeg/usr/bin/ffmpeg")
W, H, FPS, DURATION = 1280, 720, 24, 150

NAVY = (5, 22, 34)
PANEL = (8, 32, 45)
CYAN = (87, 205, 218)
BLUE = (67, 142, 216)
GOLD = (226, 166, 55)
WHITE = (235, 244, 247)
MUTED = (153, 178, 188)
GREEN = (105, 190, 143)


def font(size: int, bold=False):
    path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(path, size)


F_TITLE, F_H1, F_H2 = font(54, True), font(36, True), font(24, True)
F_BODY, F_SMALL, F_TINY = font(21), font(16), font(13)


def cover(im: Image.Image, scale=1.0, pan_x=0.5, pan_y=0.5) -> Image.Image:
    ratio = max(W / im.width, H / im.height) * scale
    sized = im.resize((round(im.width * ratio), round(im.height * ratio)), Image.Resampling.LANCZOS)
    left = max(0, round((sized.width - W) * pan_x))
    top = max(0, round((sized.height - H) * pan_y))
    return sized.crop((left, top, left + W, top + H))


def darken(im, amount=0.35):
    return ImageEnhance.Brightness(im).enhance(1 - amount)


def moving_prototype(t, darkness=.24, zoom=1.08):
    """Animate the approved photograph with buoy-like heave/roll and live water."""
    heave = math.sin(t * math.tau * .32) * 7 + math.sin(t * math.tau * .13) * 3
    roll = math.sin(t * math.tau * .21) * 1.15
    base = cover(prototype, zoom + .008 * math.sin(t * .35), .60, .52)
    base = base.rotate(roll, Image.Resampling.BICUBIC, center=(760, 440))
    canvas = Image.new("RGB", (W, H), NAVY)
    canvas.paste(base, (0, round(heave)))
    canvas = darken(canvas, darkness)
    d = ImageDraw.Draw(canvas, "RGBA")
    for layer, (y0, amp, speed, alpha) in enumerate(((590, 13, 1.0, 105), (625, 9, 1.35, 80), (670, 7, .72, 58))):
        pts = []
        for x in range(-20, W + 21, 10):
            y = y0 + amp * math.sin(x / (72 + layer * 18) - t * speed * 2.5) + 3 * math.sin(x / 24 + t)
            pts.append((x, y))
        d.line(pts, fill=(102, 210, 226, alpha), width=3 if layer == 0 else 2)
        d.polygon(pts + [(W + 20, H), (-20, H)], fill=(7, 78, 104, 20 + layer * 7))
    for i in range(9):
        x = ((t * 150 + i * 173) % (W + 260)) - 180
        y = 105 + (i % 5) * 38
        d.arc((x, y, x + 125, y + 34), 195, 345, fill=(210, 240, 246, 65), width=2)
    hub = (586, 81)
    angle = t * 5.5
    for i in range(4):
        a = angle + i * math.pi / 2
        ex, ey = hub[0] + math.cos(a) * 23, hub[1] + math.sin(a) * 12
        d.line((hub[0], hub[1], ex, ey), fill=(235, 244, 246, 185), width=3)
        d.ellipse((ex - 6, ey - 4, ex + 6, ey + 4), fill=(8, 20, 27, 220), outline=(220, 238, 242, 130))
    d.ellipse((hub[0]-4, hub[1]-4,hub[0]+4,hub[1]+4),fill=GOLD)
    return canvas


def live_readout(draw, xy, label, value, color=CYAN):
    x, y = xy
    draw.rounded_rectangle((x, y, x + 205, y + 67), 11, fill=(4, 24, 35, 210), outline=(65, 102, 113, 180), width=2)
    draw.text((x + 14, y + 10), label, font=F_TINY, fill=MUTED)
    draw.text((x + 14, y + 31), value, font=F_H2, fill=color)


def pill(draw, xy, text, color=CYAN, fill=(7, 31, 44, 230), size=16):
    f = font(size, True)
    box = draw.textbbox((0, 0), text, font=f)
    width = box[2] - box[0] + 28
    x, y = xy
    draw.rounded_rectangle((x, y, x + width, y + 34), 17, fill=fill, outline=color, width=2)
    draw.text((x + 14, y + 7), text, font=f, fill=WHITE)
    return width


def header(draw, kicker, title, subtitle=""):
    draw.text((58, 42), kicker.upper(), font=F_SMALL, fill=CYAN)
    draw.text((58, 70), title, font=F_H1, fill=WHITE)
    if subtitle:
        draw.text((60, 116), subtitle, font=F_BODY, fill=MUTED)


def panel(draw, box, title, body, accent=CYAN):
    draw.rounded_rectangle(box, 16, fill=PANEL + (235,), outline=(46, 83, 96), width=2)
    x1, y1, x2, _ = box
    draw.rectangle((x1, y1, x1 + 6, box[3]), fill=accent)
    draw.text((x1 + 22, y1 + 18), title, font=F_H2, fill=WHITE)
    for index, line in enumerate(body):
        draw.text((x1 + 22, y1 + 56 + index * 29), line, font=F_SMALL, fill=MUTED)


def arrow(draw, start, end, progress=1.0, color=CYAN, width=5):
    x1, y1 = start; x2, y2 = end
    xe, ye = x1 + (x2 - x1) * progress, y1 + (y2 - y1) * progress
    draw.line((x1, y1, xe, ye), fill=color, width=width)
    if progress > .96:
        a = math.atan2(y2 - y1, x2 - x1)
        p1 = (x2 - 15 * math.cos(a - .55), y2 - 15 * math.sin(a - .55))
        p2 = (x2 - 15 * math.cos(a + .55), y2 - 15 * math.sin(a + .55))
        draw.polygon((end, p1, p2), fill=color)


def data_dots(draw, start, end, phase, count=5, color=CYAN):
    for i in range(count):
        q = (phase + i / count) % 1
        x = start[0] + (end[0] - start[0]) * q
        y = start[1] + (end[1] - start[1]) * q
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=color)


prototype = Image.open(ASSETS / "falcon-approved-prototype.png").convert("RGB")
wiring = Image.open(ASSETS / "falcon-electronics-data-path.png").convert("RGB")
logo = Image.open(ASSETS / "falcon-logo.jpg").convert("RGB")


def intro(local):
    bg = moving_prototype(local * 12, .22, 1.03 + .03 * local)
    d = ImageDraw.Draw(bg, "RGBA")
    d.rectangle((0, 0, W, H), fill=(0, 15, 25, 40))
    d.text((65, 76), "PROJECT FALCON", font=F_TITLE, fill=WHITE)
    d.text((68, 145), "AI-POWERED LIVE COASTAL OBSERVATION NETWORK", font=F_H2, fill=CYAN)
    d.text((70, 585), "FROM OCEAN MOVEMENT TO ACTIONABLE COASTAL DATA", font=F_BODY, fill=WHITE)
    d.text((70, 625), "A connected sensor-to-cloud demonstration", font=F_SMALL, fill=MUTED)
    return bg


def movement(local):
    seconds = 12 + local * 18
    bg = moving_prototype(seconds, .31, 1.08)
    d = ImageDraw.Draw(bg, "RGBA")
    header(d, "Stage 01 · Physical environment", "The ocean moves. FALCON measures.", "One buoy continuously converts real-world motion and weather into digital observations.")
    # Wave/motion traces.
    pts=[]
    for x in range(40, 600, 8):
        y=575 + math.sin(x/45 + local*8)*14 + math.sin(x/17)*4
        pts.append((x,y))
    d.line(pts, fill=CYAN, width=4)
    labels=[("WIND SPEED",(715,150)),("GPS POSITION",(914,185)),("BUOY MOTION",(675,310)),("WATER PRESSURE",(810,515))]
    for i,(text,pos) in enumerate(labels):
        alpha=min(1,max(0,local*3-i*.45));
        if alpha>0:pill(d,pos,text)
    live_readout(d,(42,430),"LIVE HEAVE",f"{0.51 + .06*math.sin(seconds*1.7):.2f} m")
    live_readout(d,(42,507),"IMU ROLL",f"{2.8*math.sin(seconds*1.31):+.1f}°",GOLD)
    return bg


def sensors(local):
    bg = Image.new("RGB",(W,H),NAVY)
    d=ImageDraw.Draw(bg,"RGBA"); header(d,"Stage 02 · Sensor acquisition","Multiple sensors. One synchronized sample.","The ESP32 reads each interface using the protocol best suited to that sensor.")
    cards=[("BAR02 PRESSURE","I²C","PRESSURE · EST. WAVE"),("GPS + SECURITY","UART / GPIO","GEOFENCE · TAMPER"),("WIND SENSORS","GPIO / ADC","SPEED · DIRECTION"),("DS18B20 WATER","ONEWIRE","WATER TEMPERATURE")]
    for i,(name,bus,data) in enumerate(cards):
        x=58+i*300; y=210
        d.rounded_rectangle((x,y,x+264,y+235),18,fill=PANEL,outline=(45,78,91),width=2)
        d.ellipse((x+24,y+25,x+68,y+69),fill=(20,68,83),outline=CYAN,width=2)
        d.text((x+84,y+29),name,font=F_H2,fill=WHITE)
        pill(d,(x+24,y+92),bus,size=14)
        d.text((x+24,y+150),data,font=F_SMALL,fill=MUTED)
        sample = 18420 + int(local * 360) + i
        d.text((x+24,y+185),f"Sample #{sample:05d}",font=F_TINY,fill=GREEN)
        q=(local*1.8+i*.18)%1; d.rectangle((x+24,y+213,x+24+210*q,y+218),fill=CYAN)
    arrow(d,(95,510),(1180,510),min(1,local*1.6)); data_dots(d,(95,510),(1180,510),local)
    d.text((470,548),"TIMESTAMPED SENSOR FRAME",font=F_H2,fill=WHITE)
    return bg


def wiring_scene(local):
    bg=darken(cover(wiring,1.0,.5,.5),.18)
    d=ImageDraw.Draw(bg,"RGBA"); d.rectangle((0,0,W,145),fill=(3,18,28,220))
    header(d,"Stage 03 · ESP32 controller","Signals converge at the ESP32","The microcontroller validates timing, applies calibration, and packages one clean telemetry frame.")
    # Animated sensor-to-controller paths.
    paths=[((250,270),(600,310)),((290,415),(600,330)),((1015,280),(690,330)),((1030,470),(705,360))]
    for i,(a,b) in enumerate(paths):
        arrow(d,a,b,min(1,max(0,local*2-i*.18)),CYAN,5); data_dots(d,a,b,local+i*.13,4)
    d.rounded_rectangle((485,555,800,660),14,fill=(4,24,35,225),outline=CYAN,width=2)
    d.text((510,575),"ESP32 TELEMETRY FRAME",font=F_H2,fill=WHITE)
    d.text((510,615),'{"pressure": 0.56, "roll": 1.2, "gps": "VALID"}',font=F_TINY,fill=GREEN)
    return bg


def usb_scene(local):
    bg=darken(cover(wiring,1.0,.5,.5),.44); d=ImageDraw.Draw(bg,"RGBA")
    header(d,"Stage 04 · Local transfer","ESP32 → USB serial → Orange Pi","A wired USB link carries validated telemetry into the edge computer inside the enclosure.")
    start,end=(630,360),(1015,485)
    arrow(d,start,end,min(1,local*1.5),CYAN,8); data_dots(d,start,end,local,8,GOLD)
    pill(d,(635,420),"USB SERIAL · JSON LINES",GOLD)
    panel(d,(60,505,500,660),"Why a wired link?",["Stable inside the sealed enclosure","Simple diagnostics and recovery","Independent power for the Orange Pi"],CYAN)
    return bg


def edge_ai(local):
    bg=Image.new("RGB",(W,H),NAVY); d=ImageDraw.Draw(bg,"RGBA")
    header(d,"Stage 05 · Edge intelligence","Orange Pi processes data near the source","Local processing continues even when the internet connection is unstable.")
    stages=[("1","INGEST","Read USB telemetry"),("2","VALIDATE","Reject stale or invalid data"),("3","FEATURES","Build wave and motion history"),("4","AI MODEL","Predict near-term wave height"),("5","ALERTS","Evaluate operational limits")]
    for i,(n,t,b) in enumerate(stages):
        x=45+i*246; y=240
        d.rounded_rectangle((x,y,x+210,y+180),16,fill=PANEL,outline=(45,82,94),width=2)
        d.ellipse((x+18,y+20,x+58,y+60),fill=CYAN); d.text((x+32,y+28),n,font=F_SMALL,fill=NAVY)
        d.text((x+18,y+82),t,font=F_H2,fill=WHITE); d.text((x+18,y+126),b,font=F_TINY,fill=MUTED)
        if i<4: arrow(d,(x+210,y+90),(x+244,y+90),1,CYAN,3)
        if local>i*.12:d.rectangle((x+18,y+158,x+18+174*min(1,(local-i*.12)*3),y+163),fill=GREEN)
    d.text((400,520),"OUTPUT",font=F_SMALL,fill=GOLD)
    d.text((400,552),"Predicted wave height: 0.49 m  ·  Confidence: 80%  ·  Status: CALM",font=F_H2,fill=WHITE)
    return bg


def cloud_scene(local):
    bg=Image.new("RGB",(W,H),NAVY); d=ImageDraw.Draw(bg,"RGBA")
    header(d,"Stage 06 · Internet and cloud","Send results—not raw confusion","The Orange Pi publishes compact telemetry and AI results through the internet while retaining a local copy.")
    nodes=[((155,350),"ORANGE PI","EDGE"),((640,250),"SECURE CLOUD","STORE · RELAY"),((1080,350),"DASHBOARD","DISPLAY")]
    for (x,y),a,b in nodes:
        d.ellipse((x-82,y-82,x+82,y+82),fill=PANEL,outline=CYAN,width=3)
        d.text((x,y-15),a,font=F_H2,fill=WHITE,anchor="mm"); d.text((x,y+24),b,font=F_TINY,fill=MUTED,anchor="mm")
    arrow(d,(238,350),(555,270),min(1,local*2),GOLD,6); arrow(d,(725,270),(995,350),min(1,max(0,local*2-.5)),CYAN,6)
    data_dots(d,(238,350),(555,270),local,6,GOLD); data_dots(d,(725,270),(995,350),local+.3,6,CYAN)
    panel(d,(390,470,890,630),"Resilient delivery",["HTTPS / authenticated API","Local database buffers connection loss","Queued records synchronize after reconnection"],GREEN)
    return bg


def dashboard(local):
    bg=Image.new("RGB",(W,H),(4,22,31)); d=ImageDraw.Draw(bg,"RGBA")
    header(d,"Stage 07 · Operational dashboard","Live conditions become understandable","Operators see current measurements, AI predictions, system health, and actionable alerts.")
    metrics=[("SYSTEM","ONLINE",GREEN),("CURRENT WAVE","0.56 m",CYAN),("PREDICTED","0.49 m",GOLD),("SEA STATE","CALM",GREEN)]
    for i,(a,b,c) in enumerate(metrics):
        x=55+i*300; d.rounded_rectangle((x,165,x+270,260),13,fill=PANEL,outline=(40,74,86),width=2)
        d.text((x+18,182),a,font=F_TINY,fill=MUTED); d.text((x+18,213),b,font=F_H2,fill=c)
    d.rounded_rectangle((55,290,905,650),16,fill=PANEL,outline=(40,74,86),width=2)
    d.text((80,315),"WAVE HEIGHT · MEASURED AND PREDICTED",font=F_H2,fill=WHITE)
    # Grid and animated dual series.
    for y in range(380,610,55): d.line((85,y,870,y),fill=(24,57,68),width=1)
    pts1=[];pts2=[]
    for i in range(80):
        x=90+i*9.5; base=500-math.sin(i*.28)*42-math.sin(i*.09)*20
        pts1.append((x,base)); pts2.append((x,base+12+math.sin(i*.18+1)*15))
    n=max(2,int(len(pts1)*min(1,local*1.5))); d.line(pts1[:n],fill=CYAN,width=4); d.line(pts2[:n],fill=GOLD,width=3)
    panel(d,(930,290,1225,650),"Coastal snapshot",["Wind      11.7 km/h","Pressure  101.3 kPa","GPS       VALID","Battery   87%","Alerts     0"],CYAN)
    return bg


def full_flow(local):
    bg=moving_prototype(140 + local * 7,.57,1.08); d=ImageDraw.Draw(bg,"RGBA")
    header(d,"Complete system","One continuous data journey","Every stage is connected, timestamped, and visible from the deployed buoy to the dashboard.")
    labels=[("MOVEMENT",90),("SENSORS",300),("ESP32",500),("USB",675),("ORANGE PI",820),("CLOUD",1010),("DASHBOARD",1160)]
    y=420
    for i,(text,x) in enumerate(labels):
        d.ellipse((x-42,y-42,x+42,y+42),fill=(5,31,43,235),outline=CYAN,width=3)
        d.text((x,y),str(i+1),font=F_H2,fill=WHITE,anchor="mm")
        d.text((x,y+65),text,font=F_TINY,fill=WHITE,anchor="mm")
        if i<len(labels)-1: arrow(d,(x+44,y),(labels[i+1][1]-44,y),min(1,local*2-i*.13),GOLD,4)
    d.text((640,585),"MEASURE  ·  PROCESS  ·  PREDICT  ·  DELIVER",font=F_H2,fill=CYAN,anchor="mm")
    return bg


def outro(local):
    bg=moving_prototype(147 + local * 3,.36,1.03+.025*local); d=ImageDraw.Draw(bg,"RGBA")
    d.rectangle((0,0,W,H),fill=(0,14,24,55))
    d.text((640,230),"PROJECT FALCON",font=F_TITLE,fill=WHITE,anchor="mm")
    d.text((640,305),"Coastal intelligence—from the water to the dashboard.",font=F_H2,fill=CYAN,anchor="mm")
    d.text((640,560),"FULLBRIGHT COLLEGE · FALCON-01",font=F_SMALL,fill=WHITE,anchor="mm")
    return bg


SCENES=[(0,12,intro),(12,30,movement),(30,48,sensors),(48,67,wiring_scene),(67,83,usb_scene),(83,103,edge_ai),(103,121,cloud_scene),(121,140,dashboard),(140,147,full_flow),(147,150,outro)]


def render_frame(t):
    for index, (start,end,fn) in enumerate(SCENES):
        if start<=t<end:
            local=(t-start)/(end-start)
            im=fn(local)
            if index and t-start < 1.0:
                previous=SCENES[index-1][2](1.0)
                im=Image.blend(previous,im,(t-start))
            return im
    return outro(1)


def make_music():
    rate=48000; total=rate*DURATION; samples=array('h')
    chords=[(110.0,164.81,220.0),(98.0,146.83,196.0),(130.81,196.0,261.63),(87.31,130.81,174.61)]
    for n in range(total):
        t=n/rate; chord=chords[int(t//12)%len(chords)]
        env=min(1,(t%12)/2,(12-t%12)/2); value=0
        for i,f in enumerate(chord): value += math.sin(2*math.pi*f*t+i*.7)/(i+1)
        pulse=max(0,math.sin(2*math.pi*(chord[0]*2)*t))*math.exp(-((t%2.0)*3.2))
        value=(value*.11*env+pulse*.035)*.72
        s=max(-32767,min(32767,int(value*32767))); samples.extend((s,s))
    with wave.open(str(MUSIC),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(rate);w.writeframes(samples.tobytes())


def main():
    raise SystemExit(
        "Archived V2 visual generator disabled: the physical prototype is under redesign. "
        "Use FLOW_AI_REALISTIC_DEPLOYMENT_PROMPTS.md for the current non-mechanical system-flow brief."
    )
    if not FFMPEG.exists(): raise SystemExit("ffmpeg was not found. Install it with: sudo apt install ffmpeg")
    make_music()
    cmd=[str(FFMPEG),'-y','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}','-framerate',str(FPS),'-i','-', '-i',str(MUSIC),'-vf','scale=1920:1080:flags=lanczos','-c:v','libx264','-preset','veryfast','-crf','21','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-shortest','-movflags','+faststart',str(OUT)]
    process=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    assert process.stdin
    for frame in range(FPS*DURATION):
        process.stdin.write(render_frame(frame/FPS).tobytes())
        if frame%(FPS*10)==0: print(f"Rendered {frame/FPS:.0f}/{DURATION} seconds",flush=True)
    process.stdin.close(); code=process.wait()
    if code: raise SystemExit(code)
    print(f"Created {OUT}")


if __name__=='__main__': main()

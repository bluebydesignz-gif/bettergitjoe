"""Assemble the rough cut from beatmap.json -> rough/rough_cut.mp4, rough/cut_audio.wav, rough/edl.json
(certified-wild-reel build_rough.py; the hook VO is optional: omit "vo" when Marcos's own line is the hook)"""
import json, subprocess, sys, os, wave
import numpy as np
SR=48000; FPS=30
bm=json.load(open(sys.argv[1])); src=bm['source']; os.makedirs('rough',exist_ok=True)
def run(c): subprocess.run(c,check=True)
def pcm(cmd): return np.frombuffer(subprocess.run(cmd,capture_output=True,check=True).stdout,np.float32)
clean='rough/clean_full.wav'
run(['ffmpeg','-v','error','-y','-i',src,'-ac','1','-ar',str(SR),'-af',
     'highpass=f=80,afftdn=nr=12:nf=-42:tn=1,equalizer=f=250:t=q:w=1.2:g=-2.5,'
     'equalizer=f=3500:t=q:w=1.4:g=4,highshelf=f=8000:g=2.5,'
     'acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2',clean])
A=pcm(['ffmpeg','-v','error','-i',clean,'-f','f32le','-'])
keys=np.array(bm['face_keys'])
def face(t): return np.interp(t,keys[:,0],keys[:,1]),np.interp(t,keys[:,0],keys[:,2])
W,H=2160,3840
out=[]; edl=[]; tcur=0.0; parts=[]; xf=int(0.012*SR)
for i,b in enumerate(bm['beats']):
    t0,t1,z=b['in'],b['out'],b['zoom']
    hold=b.get('hold',0.0)
    nsrc=int(round((t1-t0)*FPS)); nfr=nsrc+int(round(hold*FPS)); dur=nfr/FPS
    cw,ch=int(W/z)//2*2,int(H/z)//2*2
    if 'center' in b: fx,fy=b['center']; cx,cy=fx*W,fy*H; top=cy-ch/2
    else: fx,fy=face((t0+t1)/2); cx=fx*W; top=fy*H-b.get('face_y',0.32)*ch
    x=int(min(max(cx-cw/2,0),W-cw))//2*2; y=int(min(max(top,0),H-ch))//2*2
    seg=f'rough/seg{i:02d}.mp4'
    run(['ffmpeg','-v','error','-y','-ss',f'{t0:.3f}','-i',src,'-frames:v',str(nfr),'-an',
         '-vf',f'crop={cw}:{ch}:{x}:{y},scale=1080:1920:flags=lanczos,fps={FPS},setsar=1,tpad=stop_mode=clone:stop_duration={hold+0.5}',
         '-c:v','libx264','-preset','fast','-crf','14','-pix_fmt','yuv420p',seg])
    parts.append(seg)
    n=int(round(dur*SR)); s=int(t0*SR); ns=int(round(nsrc/FPS*SR)); a=A[s:s+ns].copy()
    if len(a)<n: a=np.pad(a,(0,n-len(a)))
    kind=b.get('audio','voice')
    if kind=='ambient': a*=0.45
    if kind=='ambient_low': a*=0.35
    if kind=='mute': a*=0.0
    fade=np.ones(n); fade[:xf]=np.linspace(0,1,xf); fade[-xf:]=np.linspace(1,0,xf); a*=fade
    out.append(a)
    edl.append({'id':b['id'],'start':round(tcur,3),'end':round(tcur+dur,3),'src_in':t0,'zoom':z,
                'text':b.get('text',''),'crop':[x,y,cw,ch]})
    tcur+=dur
voice=np.concatenate(out); vlen=0.0
vo=bm.get('vo')
if vo:
    v=pcm(['ffmpeg','-v','error','-ss',str(vo['trim_start']),'-i',vo['file'],'-ac','1','-ar',str(SR),'-af',
           'highpass=f=140,lowpass=f=7500,equalizer=f=2800:t=q:w=1.5:g=1.5,aecho=0.8:0.5:28|47:0.13|0.08','-f','f32le','-'])
    v=v/np.abs(v).max()*0.55; vlen=len(v)/SR
    i0=int(vo['at']*SR); voice[i0:i0+len(v)]+=v[:len(voice)-i0]
w=wave.open('rough/cut_audio.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((np.clip(voice,-1,1)*32767).astype(np.int16).tobytes()); w.close()
open('rough/list.txt','w').write(''.join(f"file '{os.path.basename(p)}'\n" for p in parts))
run(['ffmpeg','-v','error','-y','-f','concat','-safe','0','-i','rough/list.txt','-c','copy','rough/video_only.mp4'])
run(['ffmpeg','-v','error','-y','-i','rough/video_only.mp4','-i','rough/cut_audio.wav','-map','0:v','-map','1:a',
     '-c:v','copy','-c:a','aac','-b:a','256k','-shortest','rough/rough_cut.mp4'])
json.dump({'duration':round(tcur,3),'vo_at':vo['at'] if vo else None,'vo_len':round(vlen,3),'beats':edl},open('rough/edl.json','w'),indent=1)
print(f'rough cut {tcur:.2f}s, {len(edl)} beats')

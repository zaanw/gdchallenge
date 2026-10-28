import csv
import hashlib
import json
import zipfile
from pathlib import Path
from .core.level import Level,Section,Sample
from .core.objects import Object
from .core.serialization import encode_raw,decode_raw,export_gmd,read_gmd
from .core.validation import validate
from .gameplay import cube,ship,wave
from .gameplay.portals import portal
from .gameplay.slopes import wall_pair
from .decoration import particles,pulses


def build():
    level=Level()
    spec=[('Rupture','cube',0,.10,False,80),
          ('Needle ignition','wave',.10,.25,True,36),
          ('Crimson interference','wave',.25,.40,False,44),
          ('Event horizon','ship',.40,.55,False,68),
          ('Oblique fracture','wave',.55,.70,False,40),
          ('Zero tolerance','wave',.70,.85,False,34),
          ('Collapse gauntlet','wave',.85,1,False,38)]
    level.sections=[Section(n,m,a*44,b*44,mini,gap) for n,m,a,b,mini,gap in spec]
    dt=1/240
    y,vy,direction=15.0,0.0,1
    # Thresholds change at a nonperiodic sequence of reversals.
    reversal=0
    for tick in range(round(level.duration/dt)+1):
        t=tick*dt
        s=level.section_at(t)
        if s.mode=='cube':
            y,hold=cube.state(t)
        elif s.mode=='ship':
            target=155+45*__import__('math').sin((t-s.start)*2.4)
            y,vy,hold=ship.step(y,vy,dt,target)
        else:
            low=100+(reversal*19)%55
            high=225+(reversal*13)%50
            old=direction
            y,direction=wave.advance(y,direction,level.speed*dt,s.mini,low,high)
            if old != direction: reversal+=1
            hold=direction>0
        radius=15 if s.mode in {'cube','ship'} else (5 if s.mini else 9)
        level.trajectory.append(Sample(t,level.x_at(t),y,radius,s.mode,hold))
    # Classic ground is supplied by the game; jump spikes are inside the ballistic arcs.
    for t in cube.jump_times(level.sections[0].end):
        x=level.x_at(t+cube.IMPULSE/cube.GRAVITY)
        level.add(Object(8,x,15,channel=1))
        level.add(Object(8,x+34,15,scale=.7,channel=1))
        level.add(Object(8,x+60,15,scale=.7,channel=1))
        for dx in (-30,0,30):
            level.add(Object(1,x+dx,125,channel=1))
    # Collect conservative witness extrema over each cell including player width.
    samples=level.trajectory
    for i,x in enumerate(range(150,int(level.x_at(level.duration))-30,30)):
        t=(x-level.lead)/level.speed
        s=level.section_at(t)
        if s.mode=='cube': continue
        # Wide, unobstructed approach to all portals, including size-only changes.
        if any(abs(t-sec.start)<.20 for sec in level.sections[1:]): continue
        nearby=[a.y for a in samples[max(0,int((t-.08)*240)):min(len(samples),int((t+.08)*240)+1)]]
        bottom,top=min(nearby),max(nearby)
        wall_pair(level,x,(top+bottom)/2,s.gap/2,(top-bottom)/2,i,slopes=s.name=='Oblique fracture')
    for s in level.sections[1:]:
        sample=min(samples,key=lambda a:abs(a.t-s.start))
        for obj in portal(s.mode,level.x_at(s.start),sample.y,s.mini): level.add(obj)
    particles.decorate(level)
    pulses.decorate(level)
    return level


def preview(level,path):
    # Standalone vector preview is diagnostic, not an in-game screenshot.
    width=1600
    scale=width/level.x_at(level.duration)
    pts=' '.join(f'{s.x*scale:.3f},{(640-s.y)*.8:.3f}' for s in level.trajectory[::6])
    shapes=[]
    for o in level.objects:
        if o.id in {1,8,289}:
            a,b,c,d=o.bounds()
            shapes.append(f'<rect x="{a*scale:.3f}" y="{(640-d)*.8:.3f}" width="{(c-a)*scale:.3f}" height="{(d-b)*.8:.3f}" fill="#95132c"/>')
    labels=[]
    for s in level.sections:
        x=level.x_at(s.start)*scale
        labels.append(f'<text x="{x:.2f}" y="28" fill="white" font-size="12">{s.name}</text>')
    Path(path).write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 560"><rect width="1600" height="560" fill="#090207"/>'+''.join(shapes)+f'<polyline points="{pts}" fill="none" stroke="#ffb6c4" stroke-width="1"/>'+''.join(labels)+'</svg>')


def generate(output):
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    level=build()
    report=validate(level)
    raw=encode_raw(level)
    decode_raw(raw)
    (output/'ABSOLUTE_COLLAPSE.level').write_text(raw)
    export_gmd(level,output/'ABSOLUTE_COLLAPSE.gmd')
    fields,decoded=read_gmd(output/'ABSOLUTE_COLLAPSE.gmd')
    if decoded != raw or int(fields['k48']) != len(level.objects):
        raise ValueError('Export round-trip mismatch')
    report['export_roundtrip']='PASS'
    report['level_sha256']=hashlib.sha256(raw.encode()).hexdigest()
    report['sections']=[vars(s) for s in level.sections]
    (output/'validation_report.json').write_text(json.dumps(report,indent=2))
    (output/'validation_report.txt').write_text(
        'ABSOLUTE COLLAPSE — validation\n'+report['status']+'\n'+
        f"Objects: {len(level.objects)}; swept segments: {len(level.trajectory)-1}\n"+
        'XML, gzip/base64 and object stream round-trip: PASS\n'+
        'Geometry errors: '+str(report['errors'])+'\n\nLIMITATIONS\n'+
        '\n'.join(report['limitations'])+'\n')
    with (output/'trajectory.csv').open('w',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['time_s','x','y','radius','mode','hold'])
        for a in level.trajectory:
            writer.writerow([round(a.t,6),round(a.x,6),round(a.y,6),a.radius,a.mode,int(a.hold)])
    (output/'sections.json').write_text(json.dumps([vars(s) for s in level.sections],indent=2))
    preview(level,output/'layout_preview.svg')
    instructions=Path(__file__).resolve().parents[1]/'docs/import_instructions.md'
    (output/'import_instructions.md').write_text(instructions.read_text())
    (output/'format_sources.md').write_text((instructions.parent/'format_sources.md').read_text())
    members=['ABSOLUTE_COLLAPSE.gmd','ABSOLUTE_COLLAPSE.level','validation_report.txt',
             'validation_report.json','trajectory.csv','sections.json','layout_preview.svg',
             'import_instructions.md','format_sources.md']
    with zipfile.ZipFile(output/'ABSOLUTE_COLLAPSE.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name in members:
            info=zipfile.ZipInfo(name,date_time=(2026,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,(output/name).read_bytes())
        z.writestr('README.md',(instructions.parent.parent/'README.md').read_text())
    with zipfile.ZipFile(output/'ABSOLUTE_COLLAPSE.zip') as z:
        if z.testzip() is not None or not set(members)<=set(z.namelist()):
            raise ValueError('Invalid release archive')
    if report['errors']: raise ValueError('Geometry validation failed: '+str(report['errors']))
    return report

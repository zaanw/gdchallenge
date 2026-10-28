"""Swept conservative geometry checks, independent of rendering and raw export.
No exact GD 2.281 physics, collision meshes or engine tick emulation is claimed.
"""
from collections import defaultdict
from math import hypot
from .objects import SOLIDS

def swept_hit(a,b,bounds,radius):
    """Segment vs Minkowski-expanded AABB (slab method), inclusive contact."""
    xmin,ymin,xmax,ymax=bounds
    low,high=0.0,1.0
    for p,q,left,right in ((a.x,b.x,xmin-radius,xmax+radius),
                           (a.y,b.y,ymin-radius,ymax+radius)):
        delta=q-p
        if abs(delta)<1e-12:
            if p<left or p>right: return False
        else:
            enter,leave=sorted(((left-p)/delta,(right-p)/delta))
            low,high=max(low,enter),min(high,leave)
            if low>high: return False
    return True

def overlap(a,b):
    return min(a[2],b[2])>max(a[0],b[0])+1e-6 and min(a[3],b[3])>max(a[1],b[1])+1e-6

def validate(level):
    errors=[]
    groups={g for obj in level.objects for g in obj.groups}
    solids=[]
    index=defaultdict(list)
    for i,obj in enumerate(level.objects):
        try: obj.validate()
        except ValueError as e: errors.append(f'object {i}: {e}')
        if obj.channel not in level.colors: errors.append(f'Undefined color {obj.channel}')
        if obj.id in {901,1007,1049} and obj.properties.get(51) not in groups:
            errors.append(f'Dangling group on trigger {i}')
        if obj.id in {899,1006}:
            target=obj.properties.get(23 if obj.id==899 else 51)
            if target not in level.colors: errors.append(f'Dangling color on trigger {i}')
        if obj.id==901:
            target=obj.properties.get(51)
            if any(o.id in SOLIDS and target in o.groups for o in level.objects):
                errors.append('Moving solid: static checker cannot validate it')
        if obj.id in SOLIDS:
            bounds=obj.bounds()
            solids.append((i,obj,bounds))
            for cell in range(int(bounds[0]//60),int(bounds[2]//60)+1): index[cell].append((i,obj,bounds))
    collisions=[]
    min_ground=1e9
    for a,b in zip(level.trajectory,level.trajectory[1:]):
        radius=max(a.radius,b.radius)
        min_ground=min(min_ground,a.y-a.radius,b.y-b.radius)
        candidates={item[0]:item for cell in range(int((a.x-radius)//60),int((b.x+radius)//60)+1) for item in index[cell]}
        for i,obj,bounds in candidates.values():
            if swept_hit(a,b,bounds,radius):
                if len(collisions)<30: collisions.append({'object_index':i,'id':obj.id,'time':round(a.t,6)})
    if collisions: errors.append(f'Witness intersects solid geometry: {len(collisions)} recorded contacts')
    if min_ground < -1e-6: errors.append('Witness crosses ground')
    overlaps=[]
    for i,obj,bounds in solids:
        candidates={entry[0]:entry for cell in range(int(bounds[0]//60),int(bounds[2]//60)+1) for entry in index[cell]}
        for j,other,box in candidates.values():
            if j>i and overlap(bounds,box): overlaps.append((i,j))
    transitions=[]
    for before,after in zip(level.sections,level.sections[1:]):
        a=min(level.trajectory,key=lambda s:abs(s.t-after.start))
        portals=[o for o in level.objects if o.id in {12,13,660} and abs(o.x-level.x_at(after.start))<.1]
        ok=abs(before.end-after.start)<1e-9 and len(portals)==1 and abs(portals[0].y-a.y)<6
        transitions.append({'time':after.start,'from':before.mode,'to':after.mode,'geometry_continuous':ok})
        if not ok: errors.append(f'Invalid transition at {after.start}')
    if len(level.trajectory)<2: errors.append('No witness trajectory')
    if not level.sections or level.sections[0].start != 0 or level.sections[-1].end != level.duration:
        errors.append('Incomplete section coverage')
    if overlaps: errors.append(f'Overlapping obstacle envelopes: {len(overlaps)}')
    return {'status':'PASS_CONSERVATIVE_MODEL' if not errors else 'FAIL',
        'errors':errors,'objects':len(level.objects),'solid_objects':len(solids),
        'samples':len(level.trajectory),'sample_rate_hz':240,'duration_model_seconds':level.duration,
        'obstacle_envelope_overlaps':len(overlaps),'contacts':collisions,
        'minimum_ground_clearance':round(min_ground,5),'transitions':transitions,
        'exact_gd_physics_verified':False,'game_import_tested':False,
        'music_synchronized':False,'top1_difficulty_verified':False,
        'limitations':[
            'GD 2.281 executable unavailable: real hitboxes, portal activation, camera and end timing untested.',
            'Cube/ship are assumed ballistic and acceleration models; wave uses nominal slopes 1 and 2.',
            'Swept AABB envelope test proves this model path avoids static solids only.',
            'Portal entry and size changes require manual in-game testing; no exact transition physics.',
            '44s traversal estimate excludes automatic end-screen travel and engine-specific speed deviations.',
            'Creo — Flow audio not included; no verified Newgrounds ID, offset or beat analysis.',
            '140 BPM provisional effect grid is not a claim about the song tempo.',
            'TOP 1 is a design target, requiring human difficulty assessment and verification.']}

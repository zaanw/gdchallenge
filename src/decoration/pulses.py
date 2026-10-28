from ..core.triggers import pulse,alpha,move,color

def decorate(level,bpm=140.0):
    # This is an editable provisional beat grid, not analyzed Creo audio.
    beat=60/bpm
    t=0.0
    while t<level.duration:
        level.add(pulse(level.x_at(t),rgb=(255,25+int(t*17)%50,55)))
        t+=beat
    for i,s in enumerate(level.sections):
        x=level.x_at(s.start)
        level.add(color(x,1,(100+20*(i%4),3,15),.18))
        level.add(alpha(x,102,.15 if i%2 else .35,.2))
        level.add(move(x,101,dy=12 if i%2 else -12,duration=.3))
    level.add(alpha(10,100,.65,0))
    level.add(alpha(10,101,.25,0))

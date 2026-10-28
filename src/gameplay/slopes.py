from ..core.objects import Object

def wall_pair(level,x,y,half_gap,variation,index,slopes=False):
    # Both triangles and blocks use full 30x30 conservative envelopes.
    # variation covers every witness height under this cell, not only its center.
    for sign in (-1,1):
        obj=Object(289 if slopes else 1,x,y+sign*(half_gap+15+variation),
                   rotation=0,properties={5:int(sign>0)},channel=1)
        level.add(obj)
        if index%3==0:
            from ..decoration.glow import glow
            level.add(glow(x,obj.y,scale=1.15,group=100))

from ..core.objects import Object

def glow(x,y,scale=1,group=100):
    return Object(211,x,y,scale=scale,groups=(group,),channel=2,properties={24:-1,25:-2})

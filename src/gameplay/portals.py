from ..core.objects import Object
MODES={'cube':12,'ship':13,'wave':660}

def portal(mode,x,y,mini=False):
    return [Object(MODES[mode],x,y,properties={13:1}),
            Object(101 if mini else 99,x+4,y,properties={13:1})]

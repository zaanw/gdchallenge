from .objects import Object

def alpha(x, group, opacity, duration=.2):
    return Object(1007,x,-120,properties={51:group,35:opacity,10:duration})

def move(x, group, dx=0, dy=12, duration=.3):
    return Object(901,x,-150,properties={51:group,28:dx,29:dy,10:duration,30:0})

def pulse(x, channel=2, rgb=(255,70,85), fade_in=.04, hold=.03, fade_out=.18):
    return Object(1006,x,-180,properties={51:channel,52:0,48:0,7:rgb[0],8:rgb[1],9:rgb[2],45:fade_in,46:hold,47:fade_out})

def color(x, channel, rgb, duration=.25):
    return Object(899,x,-210,properties={23:channel,7:rgb[0],8:rgb[1],9:rgb[2],10:duration})

def toggle(x, group, enabled):
    return Object(1049,x,-240,properties={51:group,56:int(enabled)})

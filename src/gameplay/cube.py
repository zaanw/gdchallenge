"""Approximate ballistic cube model, explicitly not a GD physics emulator."""
GRAVITY=2600.0
IMPULSE=620.0
PERIOD=.69
START=.38

def state(t):
    if t<START: return 15.0,False
    age=(t-START)%PERIOD
    height=max(0.0,IMPULSE*age-GRAVITY*age*age/2)
    return 15+height,age<1/240

def jump_times(end):
    t=START
    while t+2*IMPULSE/GRAVITY < end-.18:
        yield t
        t+=PERIOD

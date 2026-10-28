"""Lightweight static glow motes, animated as a background group.
These are not 2.2 particle-system objects (no guessed particle properties).
"""
from .glow import glow

def decorate(level):
    for i,x in enumerate(range(180,int(level.x_at(level.duration)),180)):
        # Far above ship ceiling; only visual objects receive Move/Alpha.
        level.add(glow(x,430+(i*37)%150,.4+(i%3)*.2,101))
        if i%2==0:
            level.add(glow(x,390,1.8,102))

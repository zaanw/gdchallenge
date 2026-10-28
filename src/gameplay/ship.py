"""Bounded acceleration witness; constants are model assumptions."""
ACCELERATION=1100.0
MAX_VELOCITY=220.0

def step(y,vy,dt,target):
    hold=y < target-0.22*vy
    vy=max(-MAX_VELOCITY,min(MAX_VELOCITY,vy+(ACCELERATION if hold else -ACCELERATION)*dt))
    return y+vy*dt,vy,hold

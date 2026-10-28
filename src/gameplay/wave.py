"""Piecewise straight wave witness, slopes +/-1 normal, +/-2 mini.
Input changes are deterministic but nonperiodic across the five wave motifs.
"""
def advance(y, direction, dx, mini, target_low, target_high):
    slope=2 if mini else 1
    y+=direction*slope*dx
    if y >= target_high: direction=-1
    if y <= target_low: direction=1
    return y,direction

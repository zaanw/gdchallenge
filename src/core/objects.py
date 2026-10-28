"""Restricted legacy object vocabulary; unknown IDs/properties fail closed."""
from dataclasses import dataclass, field
from math import isfinite, sin, cos, radians

CATALOG = {1: "block", 8: "spike", 12: "cube", 13: "ship", 660: "wave",
           99: "normal-size", 101: "mini-size", 1334: "4x-speed",
           289: "45-degree-slope", 211: "glow", 899: "color",
           901: "move", 1006: "pulse", 1007: "alpha", 1049: "toggle"}
SOLIDS = {1, 8, 289}
PROPERTIES = {4,5,6,7,8,9,10,13,17,20,21,22,23,24,25,28,29,30,32,
              35,45,46,47,48,51,52,56,57,64,67,96}
TRIGGERS = {899,901,1006,1007,1049}

@dataclass
class Object:
    id: int
    x: float
    y: float
    rotation: float = 0
    scale: float = 1
    groups: tuple[int, ...] = ()
    channel: int = 1
    properties: dict[int, float | int | str] = field(default_factory=dict)

    def validate(self):
        if self.id not in CATALOG:
            raise ValueError(f"Unsupported object ID: {self.id}")
        if not all(isfinite(v) for v in (self.x,self.y,self.rotation,self.scale)):
            raise ValueError("Non-finite coordinate/transform")
        if not .1 <= self.scale <= 4:
            raise ValueError("Scale outside supported range .1..4")
        if not 1 <= self.channel <= 1012:
            raise ValueError("Invalid color channel")
        if len(set(self.groups)) != len(self.groups) or any(type(g) is not int or not 1 <= g <= 999 for g in self.groups):
            raise ValueError("Invalid groups")
        if self.properties.keys() - (PROPERTIES - {6,21,32,57}):
            raise ValueError("Unsupported/reserved property")
        for k,v in self.properties.items():
            if not isinstance(v,(int,float)) or not isfinite(v):
                raise ValueError("Property must be a finite number")
            if k in {4,5,13,17,56,64,67,96} and v not in (0,1):
                raise ValueError("Invalid boolean property")
            if k in {7,8,9,20,22,23,24,25,30,48,51,52} and int(v) != v:
                raise ValueError("Expected integer property")
            if any(c in str(v) for c in ',;\n\r'):
                raise ValueError("Delimiter in property")
        for k in (7,8,9):
            if k in self.properties and not 0 <= self.properties[k] <= 255:
                raise ValueError("Invalid RGB")
        for k in (10,45,46,47):
            if k in self.properties and self.properties[k] < 0:
                raise ValueError("Negative duration")
        if 35 in self.properties and not 0 <= self.properties[35] <= 1:
            raise ValueError("Invalid opacity")
        if self.id in {901,1007,1049} and not 1 <= self.properties.get(51,0) <= 999:
            raise ValueError("Missing target group")
        if self.id == 1006 and not (self.properties.get(52) == 0 and 1 <= self.properties.get(51,0) <= 1012):
            raise ValueError("Only channel pulses supported")
        if self.id == 899 and not 1 <= self.properties.get(23,0) <= 1012:
            raise ValueError("Missing target channel")

    def fields(self):
        self.validate()
        d={1:self.id,2:self.x,3:self.y,6:self.rotation,21:self.channel,32:self.scale}
        if self.groups: d[57]='.'.join(map(str,self.groups))
        return d | self.properties

    def bounds(self):
        """Conservative square envelope, including full spike/slope visual bounds.
        Does NOT claim to reproduce the game's smaller lethal hitboxes.
        """
        a=radians(self.rotation)
        h=15*self.scale*(abs(cos(a))+abs(sin(a)))
        return self.x-h,self.y-h,self.x+h,self.y+h

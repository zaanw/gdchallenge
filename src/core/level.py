from dataclasses import dataclass, field
from .objects import Object

@dataclass
class Section:
    name: str
    mode: str
    start: float
    end: float
    mini: bool = False
    gap: float = 50

@dataclass
class Sample:
    t: float
    x: float
    y: float
    radius: float
    mode: str
    hold: bool

@dataclass
class Level:
    name: str = "ABSOLUTE COLLAPSE"
    duration: float = 44.0
    speed: float = 576.0
    lead: float = 120.0
    objects: list[Object] = field(default_factory=list)
    sections: list[Section] = field(default_factory=list)
    trajectory: list[Sample] = field(default_factory=list)
    colors: dict = field(default_factory=lambda: {
        1:(130,8,20,False),2:(255,22,48,True),3:(45,0,7,False),
        1000:(3,0,2,False),1001:(8,0,3,False),1002:(100,0,16,False)})

    def add(self, obj):
        obj.validate()
        self.objects.append(obj)
        return obj

    def x_at(self,t):
        return self.lead+self.speed*t

    def section_at(self,t):
        return next((s for s in self.sections if s.start <= t < s.end), self.sections[-1])

from enum import Enum


class ZoneEnum(str, Enum):
    RESTRICTED = 'restricted'
    NORMAL = 'normal'
    PRIORITY = 'priority'
    BLOCKED = 'blocked'


# TODO pas sur de ca, ca doit etre juste un seul mot
# mais y'a pas de liste defini
class ColorEnum(str, Enum):
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'
    YELLOW = 'yellow'
    NONE = 'none'


class Connection():
    def __init__(self, linked_to: str, max_link_capacity: int):
        self.linked_to: str = linked_to
        self.max_link_capacity: int = max_link_capacity

class Hub():
    def __init__(
        self,
        name,
        end,
        start,
        y,
        x,
        zone,
        color,
        max_cap
    ):
        self.name = name
        self.end: bool = end
        self.start: bool = start
        self.x: int = x
        self.y: int = y
        self.zone = zone
        self.color = color
        self.max_cap = max_cap
        self.connection: list[Connection] = []

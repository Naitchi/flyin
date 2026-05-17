from enum import Enum


# TODO c'est pas utilise ca encore, il faudrait et il faudra que je comprenne
class ZoneEnum(str, Enum):
    RESTRICTED = 'restricted'
    NORMAL = 'normal'
    PRIORITY = 'priority'
    BLOCKED = 'blocked'


class Connection():
    def __init__(self, linked_to: str, max_link_capacity: int):
        self.linked_to: str = linked_to
        self.max_link_capacity: int = max_link_capacity


class Hub():
    def __init__(
        self,
        name: str,
        end: bool,
        start: bool,
        y: int,
        x: int,
        zone: str,
        color: str,
        max_cap: int,
        nb_drone: int = 0
    ):
        self.nb_drone: int = nb_drone  # TODO init ca au nombre de drone total si c'est le start et bien check si son max_cap est pas depasse sinon raise error
        self.name: str = name
        self.end: bool = end
        self.start: bool = start
        self.x: int = x
        self.y: int = y
        self.x_px: int = 0
        self.y_px: int = 0
        self.zone: str = zone
        self.color: str = color
        self.max_cap: int = max_cap
        self.connection: list[Connection] = []
        self.score = -1  # TODO faire une fonction pour init ca.
        if start:
            self.score = 0

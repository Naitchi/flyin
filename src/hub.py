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
        self.nb_drone: int = nb_drone
        self.nb_drone_waiting_restricted: int = 0
        self.name: str = name
        self.end: bool = end
        self.start: bool = start
        self.x: int = x
        self.y: int = y
        self.x_px: int = 0
        self.y_px: int = 0
        self.zone: str = zone  # TODO la du coup c'est pas un str mais un ZoneEnum
        self.color: str = color
        self.max_cap: int = max_cap
        self.connection: list[Connection] = []
        self.score = 9999
        self.done: bool = False  # TODO je check ca pour savoir si je peux double le nombre de drone et quand jai deja deplace je repasse tout les done a False a la fin de chaque tour Faire en recursif pour remonter petit a petit en passant que par les hubs qui ont des drones
        if start:
            self.score = 0

# TODO donc en gros je fais une fonction qui recupere tout les hubs qui ont des drones. je vais au hub le plus proche du end et je remonte petit a petit. avec une recursive ou que sais-je.

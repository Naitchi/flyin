from .hub import Hub, Connection
import sys
from typing import Any
import re


class Parser():
    nb_drone = 0
    start_hub = False
    end_hub = False
    hubs: list[Hub] = []
    coordonnates: set[tuple[int, int]] = set()

    @classmethod
    def run_trough_file(cls, content: str):
        for line in content.split('\n'):
            if not line.strip() or line.strip().startswith('#'):
                continue
            words = line.split(' ')
            if cls.nb_drone == 0:
                cls.check_for_nb_drone(words)
            elif words[0] in ("start_hub:", "end_hub:", "hub:"):
                cls.check_for_hub(words)
            elif words[0] == "connection:":
                cls.add_connection(words)
        # TODO check si y'a bien un start et un end sinon raise
        return (cls.hubs)

    @classmethod
    def check_for_nb_drone(cls, words: list[str]):
        try:
            if words[0] == "nb_drones:":
                cls.nb_drone = int(words[1])
                if cls.nb_drone < 1:
                    raise ValueError
            else:
                raise ValueError
        except (ValueError, Exception):
            print("Error in value of drone. ",
                  "The value must be a positif number. ",
                  "The first line should be: nb_drone: <nb_drone>")
            sys.exit()

    @classmethod
    def check_for_hub(cls, words: list[str]) -> Hub:
        start: bool = False
        end: bool = False
        name: str = ""
        x: Any = ""
        y: Any = ""
        metadata: list[str] = []
        try:
            if len(words) < 4:
                raise ValueError("Error, not enough arguments on hub. ",
                                 "<start_/end_>hub: <name> <x> <y> [metadata]")
            if words[0] == "start_hub:":
                if cls.start_hub:
                    raise ValueError(
                        "Error Two or more start_hub. ",
                        "There should be only one.")
                cls.start_hub = True
                start = True
            elif words[0] == "end_hub:":
                if cls.end_hub:
                    raise ValueError(
                        "Error Two or more end_hub. ",
                        "There should be only one.")
                cls.end_hub = True
                end = True
            name = words[1]
            x = words[2]
            y = words[3]
            if len(words) > 4:
                metadata = words[4:]
            cls.hubs.append(
                cls.create_hub(
                    start,
                    end,
                    name,
                    x,
                    y,
                    metadata))
        except (ValueError, Exception) as e:
            print(e)
            sys.exit()

    @classmethod
    def create_hub(
            cls,
            start: bool,
            end: bool,
            name: str,
            x: Any,
            y: Any,
            metadata: list[str]
    ) -> Hub:
        color: str = "none"
        zone: str = "normal"
        max_drones: int = 1
        try:
            if not re.fullmatch(r"\w+", name):
                raise ValueError("Error in name of hub. ",
                                 "The value of name must be a letter ",
                                 "upper or lower caps or underscore. ",
                                 "With no space or '-'.")
            x = int(x)
            y = int(y)
            cls.coordonnates.add((x, y))
            if len(cls.coordonnates) > len(cls.hubs)+1:
                raise ValueError("Error in coordonnates of hub. ",
                                 "Two hubs cannot have the same coordonnates.")
            color, zone, max_drones = cls.get_metadata_hub(
                [word.replace("[", "").replace("]", "") for word in metadata])
            if start or end:
                return Hub(
                    start=start,
                    end=end,
                    name=name,
                    x=x,
                    y=y,
                    color=color,
                    zone=zone,
                    max_cap=cls.nb_drone,
                    nb_drone=cls.nb_drone)
            return Hub(
                start=start,
                end=end,
                name=name,
                x=x,
                y=y,
                color=color,
                zone=zone,
                max_cap=max_drones)
        except (ValueError, Exception) as e:
            print(e)
            sys.exit()

    @staticmethod
    def get_metadata_hub(metadata: list[str]) -> tuple[str, str, int]:
        color: str = "none"
        zone: str = "normal"
        max_drones: int = 1
        try:
            for data in metadata:
                words = data.split("=")
                if words[0] == "zone":
                    zone = words[1]
                elif words[0] == "color":
                    color = words[1]
                elif words[0] == "max_drones":
                    max_drones = int(words[1])
        except (ValueError, Exception) as e:
            print(e)
            sys.exit()
        return (color, zone, max_drones)

    @classmethod
    def add_connection(cls, words: list[str]) -> None:
        max_link_capacity: int = 1
        try:
            if len(words) < 2:
                raise ValueError("Error, not enough arguments on connection. ",
                                 "connection: <name1>-<name2> [metadata]")
            connections = words[1].split('-')
            if len(connections) > 2:
                raise ValueError("Error too much '-' in the connections line")
            # TODO check ca c'est pas bon je geres pas les metadata atm je
            # crois
            # if len(words) > 2:
            #    words[2].split('')
            hub1: Hub = next(
                (h for h in cls.hubs if h.name == connections[0]), None)
            hub2: Hub = next(
                (h for h in cls.hubs if h.name == connections[1]), None)
            if not hub1 or not hub2:
                raise ValueError("Error hub name not found in connection.")
            hub1.connection.append(
                Connection(hub2.name, max_link_capacity))
            for connection in hub2.connection:
                if connection.linked_to == hub1.name:
                    raise ValueError("Error two connection between the same ",
                                     "hub.")
        except (ValueError, Exception) as e:
            print(e)
            sys.exit()

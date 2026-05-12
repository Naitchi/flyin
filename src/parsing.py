from .hub import Hub
import sys
from typing import Any
import re


class Parser():
    nb_drone = 0
    start_hub = False
    end_hub = False
    hubs: list[Hub] = []
    coordonnates: set[tuple[int, int]] = set()

    @staticmethod
    def run_trough_file(content: str):
        for line in content.split('\n'):
            if not line.strip() or line.strip().startswith('#'):
                continue
            words = line.split(' ')
            if Parser.nb_drone == 0:
                Parser.check_for_nb_drone(words)
            elif words[0] in ("start_hub", "end_hub", "hub"):
                Parser.check_for_hub(words)
            elif words[0] == "connection:":
                Parser.add_connection(words)
        return (Parser.nb_drone, Parser.hubs)

    @staticmethod
    def check_for_nb_drone(words: list[str]):
        if words[0] == "nb_drone:":
            try:
                Parser.nb_drone = int(words[1])
                if Parser.nb_drone < 1:
                    raise ValueError
            except (ValueError, Exception):
                print("Error in value of drone. ",
                      "The value must be a positif number. ",
                      "The first line should be: nb_drone: <nb_drone>")
                sys.exit()

    @staticmethod  # TODO passer cette methode en clsmethods? Et les autres qui utilise bcp Parser?
    def check_for_hub(words: list[str]) -> Hub:
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
            if words[0] == "start_hub":
                if Parser.start_hub:
                    raise ValueError(
                        "Error Two or more start_hub. ",
                        "There should be only one.")
                Parser.start_hub = True
            elif words[0] == "end_hub":
                if Parser.end_hub:
                    raise ValueError(
                        "Error Two or more end_hub. ",
                        "There should be only one.")
                Parser.end_hub = True
            name = words[1]
            x = words[2]
            y = words[3]
            if len(words) > 4:
                metadata = words[4:]
            Parser.hubs.append(
                Parser.create_hub(
                    start,
                    end,
                    name,
                    x,
                    y,
                    metadata))
        except (ValueError, Exception) as e:
            print(e)
            sys.exit()

    @staticmethod
    def create_hub(
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
            if x < 1:
                raise ValueError("Error in value of hub. ",
                                 "The value of x must be a positif number.")
            y = int(y)
            if y < 1:
                raise ValueError("Error in value of hub. ",
                                 "The value of y must be a positif number.")
            Parser.coordonnates.add((x, y))
            if len(Parser.coordonnates) > len(Parser.hubs)+1:
                raise ValueError("Error in coordonnates of hub. ",
                                 "Two hubs cannot have the same coordonnates.")
            color, zone, max_drones = Parser.get_metadata_hub(
                [word.replace("[", "").replace("]", "") for word in metadata])
            return Hub(
                start=start,
                end=end,
                name=name,
                x=x,
                y=y,
                color=color,
                zone=zone,
                max_drones=max_drones)
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

    @staticmethod
    def add_connection(words: list[str]) -> None:
        max_link_capacity: int = 1
        try:
            if len(words) < 2:
                raise ValueError("Error, not enough arguments on connection. ",
                                 "connection: <name1>-<name2> [metadata]")
            connections = words[1].split('-')
            if len(connections) > 2:
                raise ValueError("Error too much '-' in the connections line")
            if len(words) > 2:
                words[2].split('')
            hub1: Hub = next(
                (h for h in Parser.hubs if h.name == connections[0]), None)
            hub2: Hub = next(
                (h for h in Parser.hubs if h.name == connections[1]), None)
            if not hub1 or not hub2:
                raise ValueError("Error hub name not found in connection.")

            # TODO enfaite je devrais d'abord voir comment je vais creer
            # TODO oh ptn quelle emmerde, il me faut une fonction pour voir si les noms existe dans les hubs, check si la connection est pas deja faite
        except (ValueError, Exception) as e:
            print(e)
            sys.exit()

    # TODO faire une fonctions pour chaque:
    # Si le nbr de drone est pas defini on cherche ca (requis: entier positif, premier ligne (hors commentaires/ligne vide))
    # Si le nb_drone est defini on cherche les hubs (les trucs qui commencent par "start_hub:", "end_hub:" et "hub:"?) (requis: pas de '-' dans le nom, et pas deux hub avec les memes coordonnees)
    # Si le la ligne commence par "connection:" on cherche les connections (requis: )

    # Permettre de melanger hub et connection mais pour que la connection marche il faut que les deux hubs existe bien sinon crash

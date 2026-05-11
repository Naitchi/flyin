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
            # TODO ca c'est pas bon il faudrait le strip avant eviter les full espace/tabs etc puis le #
            if len(line) < 1 or line[0] == '#':
                continue
            words = line.split(' ')
            if Parser.nb_drone == 0:
                Parser.check_for_nb_drone(words)

                # TODO ici on refait une fonction pour verifier que toutes les donnees sont la et si elles sont des positifs int
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

    @staticmethod
    def check_for_hub(words: list[str]) -> Hub:
        try:
            if words[0] == "start_hub":
                if Parser.start_hub == True:
                    raise ValueError(
                        "Error Two or more start_hub. ",
                        "There should be only one.")
                Parser.start_hub = True
                Parser.hubs.append(Parser.create_hub())
            if words[0] == "end_hub":
                if Parser.end_hub == True:
                    raise ValueError(
                        "Error Two or more end_hub. ",
                        "There should be only one.")
                Parser.end_hub = True
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
            Parser.get_meta_data(
                [word.replace("[", "").replace("]", "") for word in metadata])

            # TODO ajouter le truc de metadonnees (faire une fonction a part et enlever les [])
        except (ValueError, Exception) as e:
            print(e)
            sys.exit()

    @staticmethod
    def get_meta_data(metadata: list[str]) -> tuple[str, str, int]:
        color: str = "none"
        zone: str = "normal"
        max_drones: int = 1
        try:
            for data in metadata:
                words = data.split("=")
                
        except (ValueError, Exception) as e:
            print(e)
            sys.exit()
        return (color, zone, max_drones)
    # TODO faire une fonctions pour chaque:
    # Si le nbr de drone est pas defini on cherche ca (requis: entier positif, premier ligne (hors commentaires/ligne vide))
    # Si le nb_drone est defini on cherche les hubs (les trucs qui commencent par "start_hub:", "end_hub:" et "hub:"?) (requis: pas de '-' dans le nom)
    # Si le la ligne commence par "connection:" on cherche les connections (requis: )

    # Permettre de melanger hub et connection mais pour que la connection marche il faut que les deux hubs existe bien sinon crash

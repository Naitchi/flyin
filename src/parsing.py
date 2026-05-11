# from pydantic import Field, BaseModel
from .hub import Hub
import sys


class Parser():
    @staticmethod
    def run_trough_file(content: str):
        nb_drone: int = 0
        hub: list[Hub] = []
        for line in content.split('\n'):
            # TODO ca c'est pas bon il faudrait le strip avant
            if len(line) < 1 or line[0] == '#':
                continue
            words = line.split(' ')
            if nb_drone == 0:
                nb_drone = Parser.check_for_nb_drone(words)

                # TODO ici on refait une fonction pour verifier que toutes les donnees sont la et si elles sont des positifs int
        return (nb_drone, hub)

    @staticmethod
    def check_for_nb_drone(words: list[str]) -> int:
        nb_drone = 0
        if words[0] == "nb_drone:":
            try:
                nb_drone = int(words[1])
                if nb_drone < 1:
                    raise (ValueError)
            except (ValueError, Exception):
                print("Error in value of drone. ",
                      "The value must be a positif number. ",
                      "The first line should be: nb_drone: <nb_drone>")
                sys.exit()
            return nb_drone

    @staticmethod
    def check_for_hub(words: list[str]) -> Hub:
        pass
# TODO faire une fonctions pour chaque:
# Si le nbr de drone est pas defini on cherche ca (requis: entier positif, premier ligne (hors commentaires/ligne vide))
# Si le nb_drone est defini on cherche les hubs (les trucs qui commencent par "start_hub:", "end_hub:" et "hub:"?) (requis: pas de '-' dans le nom)
# Si le la ligne commence par "connection:" on cherche les connections (requis: )

# Permettre de melanger hub et connection mais pour que la connection marche il faut que les deux hubs existe bien sinon crash

from enum import Enum
import argparse
from .parsing import Parser


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
        self.connection = []


class FlyInApp():
    def __init__(self):
        self.nb_drone: int = 0
        self.hub = []

    def run(self):
        argparser = argparse.ArgumentParser(description="FlyIn")
        argparser.add_argument(
            "--map",
            type=str,
            default="./maps/easy/01_linear_path.txt",
            help="Input file for your map"
        )
        args = argparser.parse_args()
        try:
            with open(args.map, "r") as f:
                content = f.read()
                Parser.run_trough_file(content)
        except (
            FileNotFoundError,
            PermissionError,
            IsADirectoryError,
            Exception
        ) as e:
            print(e)


def main():
    FlyInApp().run()


main()

import argparse
from .parsing import Parser


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

import argparse
from .parsing import Parser
from .display import Display


class FlyInApp():
    def __init__(self):
        self.hubs = []

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
                self.hubs = Parser.run_trough_file(content)
            Display.run(self.hubs)
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

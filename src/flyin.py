import argparse

from .hub import Hub, ZoneEnum
from .parsing import Parser
from .display import Display


class FlyInApp():
    """Application controller for loading maps and running the simulation."""

    hubs: list[Hub] = []

    @classmethod
    def run(cls) -> None:
        """Parse the selected map, compute scores, and start the UI."""
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
                cls.hubs = Parser.run_trough_file(content)
            start: Hub
            for hub in cls.hubs:
                if hub.start:
                    start = hub
                    break
            cls.calculate_score(start)
            Display.run(cls.hubs)
        except (
            FileNotFoundError,
            PermissionError,
            IsADirectoryError,
            Exception
        ) as e:
            print(e)

    @classmethod
    def calculate_score(cls, hub: Hub) -> None:
        """Propagate a cost score from a hub to all reachable hubs.

        Args:
            hub: Current hub used as the recursion source.
        """
        for connection in hub.connection:
            next_hub = cls.get_hub_from_name(connection.linked_to)
            if next_hub.zone == ZoneEnum.PRIORITY and \
                    hub.score + 1 < next_hub.score:
                next_hub.score = hub.score + 1
            elif next_hub.zone == ZoneEnum.NORMAL and \
                    hub.score + 2 < next_hub.score:
                next_hub.score = hub.score + 2
            elif next_hub.zone == ZoneEnum.RESTRICTED and \
                    hub.score + 3 < next_hub.score:
                next_hub.score = hub.score + 3
            cls.calculate_score(next_hub)

    @classmethod
    def get_hub_from_name(cls, name: str) -> Hub:
        """Return the hub matching the provided name.

        Args:
            name: Hub identifier to search for.

        Returns:
            The matching hub.

        Raises:
            ValueError: If no hub matches the provided name.
        """
        rslt: Hub
        for hub in cls.hubs:
            if hub.name == name:
                rslt = hub
                break
        return rslt

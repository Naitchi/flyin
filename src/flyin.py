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
            default="./maps/hard/02_capacity_hell.txt",
            help="Input file for your map"
        )
        args = argparser.parse_args()
        try:
            with open(args.map, "r") as f:
                content = f.read()
                cls.hubs = Parser.run_trough_file(content)
            end = next(hub for hub in cls.hubs if hub.end)
            cls.calculate_remaining_cost(end)
            Display.run(cls.hubs)
        except (
            FileNotFoundError,
            PermissionError,
            IsADirectoryError,
            Exception
        ) as e:
            print(e)

    @classmethod
    def calculate_remaining_cost(cls, hub: Hub) -> None:
        """Propagate remaining cost from end hub to all hubs.

        This calculates how much it costs to reach the end hub from
        any given hub. Needed for optimal path decisions during routing.

        Args:
            hub: Current hub used as the recursion source (typically end).
        """
        if hub.start:
            return

        weights = {
            ZoneEnum.PRIORITY: 1,
            ZoneEnum.NORMAL: 2,
            ZoneEnum.RESTRICTED: 3,
        }
        for incoming_name in hub.incoming:
            prev_hub = cls.get_hub_from_name(incoming_name)
            if prev_hub.zone == ZoneEnum.BLOCKED:
                continue
            cost = hub.remaining_cost + weights.get(prev_hub.zone, 2)
            if cost < prev_hub.remaining_cost:
                prev_hub.remaining_cost = cost
                if prev_hub.start:
                    continue
                cls.calculate_remaining_cost(prev_hub)

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

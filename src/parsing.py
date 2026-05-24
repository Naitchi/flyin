from .hub import Hub, Connection, ZoneEnum, ColorEnum
import sys
from typing import Any
import re


class Parser():
    """Parse map files into hubs and connections."""

    nb_drone: int = 0
    start_hub: bool = False
    end_hub: bool = False
    hubs: list[Hub] = []
    coordonnates: set[tuple[int, int]] = set()

    # TODO check hubs/properties and compare with the map after parsing
    @classmethod
    def run_trough_file(cls, content: str) -> list[Hub]:
        """Parse a map file content into a list of hubs.

        Args:
            content: Raw text content of the map file.

        Returns:
            The parsed hubs in declaration order.
        """
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
        if not cls.start_hub or not cls.end_hub:
            print("Error missing a start_hub or end_hub.")
            sys.exit()
        return cls.hubs

    @classmethod
    def check_for_nb_drone(cls, words: list[str]) -> None:
        """Parse and validate the number of drones line.

        Args:
            words: Tokenized line content.
        """
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
    def check_for_hub(cls, words: list[str]) -> None:
        """Parse a hub declaration and append the resulting hub.

        Args:
            words: Tokenized line content.
        """
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
        """Build a validated hub instance from parsed values.

        Args:
            start: Whether the hub is the start hub.
            end: Whether the hub is the end hub.
            name: Hub name.
            x: Raw X coordinate value.
            y: Raw Y coordinate value.
            metadata: Raw metadata tokens.

        Returns:
            A validated hub instance.
        """
        color: str = "none"
        zone_str: str = "normal"
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
            color, zone_str, max_drones = cls.get_metadata_hub(
                [word.replace("[", "").replace("]", "") for word in metadata])
            try:
                zone_enum = ZoneEnum(zone_str)
            except ValueError:
                raise ValueError(f"Unknown zone type: {zone_str}")
            hub_kwargs = {
                "start": start,
                "end": end,
                "name": name,
                "x": x,
                "y": y,
                "color": color,
                "zone": zone_enum,
                "max_cap": cls.nb_drone if (start or end) else max_drones,
            }
            if start:
                hub_kwargs["nb_drone"] = cls.nb_drone
            return Hub(**hub_kwargs)
        except (ValueError, Exception) as e:
            print(e)
            sys.exit()

    @staticmethod
    def get_metadata_hub(metadata: list[str]) -> tuple[ColorEnum, str, int]:
        """Extract color, zone, and capacity metadata from a hub line.

        Args:
            metadata: List of raw metadata tokens.

        Returns:
            A tuple containing the color enum, zone string, and max drones.
        """
        color_str: str = "none"
        zone: str = "normal"
        max_drones: int = 1
        try:
            for data in metadata:
                words = data.split("=")
                if words[0] == "zone":
                    zone = words[1]
                elif words[0] == "color":
                    color_str = words[1]
                elif words[0] == "max_drones":
                    max_drones = int(words[1])
        except (ValueError, Exception) as e:
            print(e)
            sys.exit()
        try:
            color_enum = ColorEnum(color_str)
        except ValueError:
            raise ValueError(f"Unknown color type: {color_str}")
        return (color_enum, zone, max_drones)

    @classmethod
    def add_connection(cls, words: list[str]) -> None:
        """Parse and attach a connection between two hubs.

        Args:
            words: Tokenized line content.
        """
        max_link_capacity: int = 1
        metadata: list[str] = []
        try:
            if len(words) < 2:
                raise ValueError("Error, not enough arguments on connection. ",
                                 "connection: <name1>-<name2> [metadata]")
            connections = words[1].split('-')
            if len(connections) > 2:
                raise ValueError("Error too much '-' in the connections line")
            if len(words) > 2:
                metadata.append(
                    words[2].replace("[", "").replace("]", ""))
                metadata = metadata[0].split('=')
                if len(metadata) < 2:
                    raise ValueError("Error in a metadata of a connection. ",
                                     "Should be connection: <name1>-<name2> ",
                                     "[max_link_capacity=<number>]")
                max_link_capacity = int(metadata[1])
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

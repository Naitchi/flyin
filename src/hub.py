from enum import Enum


class ZoneEnum(str, Enum):
    """Enumeration of hub movement constraints."""

    RESTRICTED = 'restricted'
    NORMAL = 'normal'
    PRIORITY = 'priority'
    BLOCKED = 'blocked'


class ColorEnum(str, Enum):
    """Enumeration of visual hub colors used by the renderer."""

    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'
    YELLOW = 'yellow'
    NONE = 'none'

    def to_rgb(self) -> tuple[int, int, int]:
        """Return the RGB color associated with the enum value."""
        color_map: dict[ColorEnum, tuple[int, int, int]] = {
            ColorEnum.RED:    (220, 60,  60),
            ColorEnum.GREEN:  (60,  200, 80),
            ColorEnum.BLUE:   (60,  100, 220),
            ColorEnum.YELLOW: (240, 210, 40),
            ColorEnum.NONE:   (180, 180, 180),
        }
        return color_map[self]

    def label_rgb(self) -> tuple[int, int, int, int]:
        """Return the RGBA color used for labels on this color."""
        label_map: dict[ColorEnum, tuple[int, int, int, int]] = {
            ColorEnum.RED:    (255, 255, 255, 255),
            ColorEnum.GREEN:  (0,   0,   0,   255),
            ColorEnum.BLUE:   (255, 255, 255, 255),
            ColorEnum.YELLOW: (30,  30,  30,  255),
            ColorEnum.NONE:   (0,   0,   0,   255),
        }
        return label_map[self]


class Connection():
    """Directed edge between two hubs with a maximum drone capacity."""

    def __init__(self, linked_to: str, max_link_capacity: int):
        """Create a connection to another hub.

        Args:
            linked_to: Name of the destination hub.
            max_link_capacity: Maximum number of drones that may cross.
        """
        self.linked_to: str = linked_to
        self.max_link_capacity: int = max_link_capacity


class Hub():
    """Node in the map graph representing a drone hub."""

    def __init__(
        self,
        name: str,
        end: bool,
        start: bool,
        y: int,
        x: int,
        zone: ZoneEnum,
        color: ColorEnum,
        max_cap: int,
        nb_drone: int = 0
    ):
        """Initialize a hub with coordinates, metadata, and capacity.

        Args:
            name: Hub identifier.
            end: Whether this hub is the end hub.
            start: Whether this hub is the start hub.
            y: Map Y coordinate.
            x: Map X coordinate.
            zone: Movement zone for the hub.
            color: Display color for the hub.
            max_cap: Maximum number of drones allowed on the hub.
            nb_drone: Initial number of drones present on the hub.
        """
        self.nb_drone: int = nb_drone
        self.nb_drone_waiting_restricted: int = 0
        self.name: str = name
        self.end: bool = end
        self.start: bool = start
        self.x: int = x
        self.y: int = y
        self.x_px: int = 0
        self.y_px: int = 0
        self.zone: ZoneEnum = zone
        self.color: ColorEnum = color
        self.max_cap: int = max_cap
        self.connection: list[Connection] = []
        self.score = 9999
        if start:
            self.score = 0

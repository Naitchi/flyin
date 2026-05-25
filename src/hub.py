from enum import Enum


class ZoneEnum(str, Enum):
    """Enumeration of hub movement constraints."""

    RESTRICTED = 'restricted'
    NORMAL = 'normal'
    PRIORITY = 'priority'
    BLOCKED = 'blocked'


class ColorEnum(str, Enum):
    """Enumeration of visual hub colors used by the renderer."""

    RED = "red"
    GREEN = "green"
    BLUE = "blue"
    YELLOW = "yellow"
    PURPLE = "purple"
    BLACK = "black"
    BROWN = "brown"
    MAROON = "maroon"
    ORANGE = "orange"
    GOLD = "gold"
    DARKRED = "darkred"
    VIOLET = "violet"
    CRIMSON = "crimson"
    RAINBOW = "rainbow"
    CYAN = "cyan"
    LIME = "lime"
    MAGENTA = "magenta"
    NONE = "none"

    def to_rgb(self) -> tuple[int, int, int]:
        """Return the RGB color associated with the enum value."""
        color_map: dict[ColorEnum, tuple[int, int, int]] = {
            ColorEnum.RED:      (220, 60,  60),
            ColorEnum.GREEN:    (60,  200, 80),
            ColorEnum.BLUE:     (60,  100, 220),
            ColorEnum.YELLOW:   (240, 210, 40),
            ColorEnum.PURPLE:   (150, 50,  200),
            ColorEnum.BLACK:    (0,   0,   0),
            ColorEnum.BROWN:    (139, 69,  19),
            ColorEnum.MAROON:   (128, 0,   0),
            ColorEnum.ORANGE:   (255, 165, 0),
            ColorEnum.GOLD:     (255, 215, 0),
            ColorEnum.DARKRED:  (139, 0,   0),
            ColorEnum.VIOLET:   (238, 130, 238),
            ColorEnum.CRIMSON:  (220, 20,  60),
            ColorEnum.RAINBOW:  (255, 127, 0),
            ColorEnum.CYAN:     (0,   255, 255),
            ColorEnum.LIME:     (50,  205, 50),
            ColorEnum.MAGENTA:  (255, 0,   255),
            ColorEnum.NONE:     (180, 180, 180),
        }
        return color_map[self]

    def label_rgb(self) -> tuple[int, int, int, int]:
        """Return the RGBA color used for labels on this color."""
        label_map: dict[ColorEnum, tuple[int, int, int, int]] = {
            ColorEnum.RED:      (255, 255, 255, 255),
            ColorEnum.GREEN:    (0,   0,   0,   255),
            ColorEnum.BLUE:     (255, 255, 255, 255),
            ColorEnum.YELLOW:   (30,  30,  30,  255),
            ColorEnum.PURPLE:   (255, 255, 255, 255),
            ColorEnum.BLACK:    (255, 255, 255, 255),
            ColorEnum.BROWN:    (255, 255, 255, 255),
            ColorEnum.MAROON:   (255, 255, 255, 255),
            ColorEnum.ORANGE:   (0,   0,   0,   255),
            ColorEnum.GOLD:     (0,   0,   0,   255),
            ColorEnum.DARKRED:  (255, 255, 255, 255),
            ColorEnum.VIOLET:   (0,   0,   0,   255),
            ColorEnum.CRIMSON:  (255, 255, 255, 255),
            ColorEnum.RAINBOW:  (255, 255, 255, 255),
            ColorEnum.CYAN:     (0,   0,   0,   255),
            ColorEnum.LIME:     (0,   0,   0,   255),
            ColorEnum.MAGENTA:  (255, 255, 255, 255),
            ColorEnum.NONE:     (0,   0,   0,   255),
        }
        return label_map[self]


class Drone():
    """Represents an individual drone with unique ID and state."""

    next_id: int = 1

    def __init__(self) -> None:
        """Create a new drone with a unique ID."""
        self.id: int = Drone.next_id
        Drone.next_id += 1
        self.hub: str = ""

    def __repr__(self) -> str:
        """Return string representation of drone."""
        return f"D{self.id}"


class Connection():
    """Directed edge between two hubs with a maximum drone capacity."""

    def __init__(self, linked_to: str, max_link_capacity: int) -> None:
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
    ) -> None:
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
        self.drones: list[Drone] = []
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
        self.incoming: list[str] = []
        self.restricted_transit_drones: list[Drone] = []
        self.restricted_drones: list[Drone] = []
        self.remaining_cost = 9999
        if end:
            self.remaining_cost = 0

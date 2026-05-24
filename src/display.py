import math
import pyglet

from .hub import Hub, ZoneEnum
from collections import Counter
from typing import Any, Callable, TypedDict


class PossibleMove(TypedDict):
    """Structure representing a potential drone destination."""

    max_cap_link: int
    hub: Hub


class Display():
    """Render and advance the drone simulation using Pyglet."""

    legend_visible = False
    legend_threshold = 15

    @staticmethod
    def hub_color(hub: Hub) -> tuple[int, int, int]:
        """Return the display color for a hub."""
        result: tuple[int, int, int] = hub.color.to_rgb()
        return result

    @staticmethod
    def hub_label_color(hub: Hub) -> tuple[int, int, int, int]:
        """Return the label color for a hub."""
        result: tuple[int, int, int, int] = hub.color.label_rgb()
        return result

    @staticmethod
    def make_drone(hub: Hub) -> tuple[pyglet.sprite.Sprite, pyglet.text.Label]:
        """Create the sprite and label used to represent drones on a hub."""
        image = pyglet.image.load("./assets/drone.png")
        sprite = pyglet.sprite.Sprite(image, x=hub.x_px-37, y=hub.y_px-37)
        label = pyglet.text.Label(
            str(hub.nb_drone),
            x=hub.x_px, y=hub.y_px,
            anchor_x="center", anchor_y="center",
            font_size=10,
            font_name="Arial Bold",
            color=(0, 0, 0),
        )
        return sprite, label

    @staticmethod
    def make_arrow(
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        radius: int = 25,
        color: tuple[int, int, int] = (255, 255, 255),
    ) -> tuple[pyglet.shapes.Line, pyglet.shapes.Triangle]:
        """Create an arrow between two points.

        Args:
            x1: Starting X coordinate.
            y1: Starting Y coordinate.
            x2: Ending X coordinate.
            y2: Ending Y coordinate.
            radius: Padding to keep the arrow away from hub circles.
            color: RGB color for the arrow.

        Returns:
            The line and triangle shapes composing the arrow.
        """
        angle = math.atan2(y2 - y1, x2 - x1)

        sx = x1 + radius * math.cos(angle)
        sy = y1 + radius * math.sin(angle)
        ex = x2 - radius * math.cos(angle)
        ey = y2 - radius * math.sin(angle)

        line = pyglet.shapes.Line(sx, sy, ex, ey, color=color)

        size = 12
        left_x = ex - size * math.cos(angle - math.pi / 6)
        left_y = ey - size * math.sin(angle - math.pi / 6)
        right_x = ex - size * math.cos(angle + math.pi / 6)
        right_y = ey - size * math.sin(angle + math.pi / 6)

        tip = pyglet.shapes.Triangle(
            ex, ey, left_x, left_y, right_x, right_y, color=color)
        return line, tip

    @classmethod
    def make_circle(
        cls,
        x: float,
        y: float,
        hub: Hub,
        radius: int = 25,
        color: tuple[int, int, int] | None = None,
    ) -> pyglet.shapes.Circle:
        """Create a hub circle using the hub's display color."""
        if color is None:
            color = cls.hub_color(hub)
        return pyglet.shapes.Circle(x, y, radius, color=color)

    @classmethod
    def make_label(
        cls,
        x: float,
        y: float,
        text: str,
        hub: Hub,
    ) -> pyglet.text.Label:
        """Create a centered text label for a hub."""
        return pyglet.text.Label(
            text,
            x=x, y=y,
            anchor_x="center", anchor_y="center",
            font_size=10,
            font_name="Arial Bold",
            color=cls.hub_label_color(hub),
        )

    @staticmethod
    def get_hub_from_name(hubs: list[Hub], name: str) -> Hub:
        """Return the hub with the given name.

        Args:
            hubs: Available hubs.
            name: Hub name to search for.

        Returns:
            The matching hub.

        Raises:
            ValueError: If the hub does not exist.
        """
        rslt: Hub
        for hub in hubs:
            if hub.name == name:
                rslt = hub
                break
        return rslt

    @classmethod
    def action(cls, data: list[Hub]) -> None:
        """Advance the simulation by one turn.

        Args:
            data: All hubs in the simulation.
        """
        hubs: list[Hub] = [
            hub for hub in data
            if hub.nb_drone or hub.nb_drone_waiting_restricted
        ]
        for hub in hubs[::-1]:
            possible_move: list[PossibleMove] = []
            if hub.nb_drone_waiting_restricted:
                hub.nb_drone += hub.nb_drone_waiting_restricted
                hub.nb_drone_waiting_restricted = 0
            if hub.end:
                continue
            for connection in hub.connection:

                possible_move.append({
                    "max_cap_link": connection.max_link_capacity,
                    "hub": cls.get_hub_from_name(data, connection.linked_to),
                })
            possible_move.sort(key=lambda x: x["hub"].score)
            for best_hub in possible_move:
                nb_drones_to_move: int = 0
                if best_hub["hub"].max_cap > best_hub["hub"].nb_drone:
                    nb_drones_to_move = (
                        best_hub["hub"].max_cap - best_hub["hub"].nb_drone
                    )
                    if nb_drones_to_move > best_hub["max_cap_link"]:
                        nb_drones_to_move = best_hub["max_cap_link"]
                    if nb_drones_to_move > hub.nb_drone:
                        nb_drones_to_move = hub.nb_drone
                    if best_hub["hub"].zone == ZoneEnum.RESTRICTED:
                        best_hub["hub"].nb_drone_waiting_restricted += (
                            nb_drones_to_move
                        )
                        hub.nb_drone -= nb_drones_to_move
                    elif best_hub["hub"].zone in (
                        ZoneEnum.NORMAL,
                        ZoneEnum.PRIORITY,
                    ):
                        best_hub["hub"].nb_drone += nb_drones_to_move
                        hub.nb_drone -= nb_drones_to_move

    @classmethod
    def make_legend_item(
        cls,
        idx: int,
        hub: Hub,
        lx: float,
        ly: float,
        line_h: int,
        col_width: int,
        padding: int,
    ) -> tuple[pyglet.shapes.Rectangle, pyglet.text.Label]:
        """Create a legend entry for one hub.

        Args:
            idx: Zero-based hub index.
            hub: Hub to display.
            lx: Left X coordinate.
            ly: Top Y coordinate.
            line_h: Row height.
            col_width: Column width.
            padding: Inner padding.

        Returns:
            The legend background rectangle and label.
        """
        bg = pyglet.shapes.Rectangle(
            lx, ly - line_h + 4, col_width - 10, line_h - 2,
            color=cls.hub_color(hub),
        )
        lbl = pyglet.text.Label(
            f"{idx + 1}. {hub.name}",
            x=lx + padding, y=ly - line_h // 2 + 4,
            anchor_x="left", anchor_y="center",
            font_size=9,
            font_name="Arial",
            color=cls.hub_label_color(hub),
        )
        return bg, lbl

    @staticmethod
    def make_help_label(window: Any, use_legend: bool) -> pyglet.text.Label:
        """Create the on-screen help label."""
        hints = ["Echap : quit"]
        if use_legend:
            hints.append("L : Show hubs names")
        return pyglet.text.Label(
            "    ".join(hints),
            x=window.width - 10, y=10,
            anchor_x="right", anchor_y="bottom",
            font_size=9, color=(200, 200, 200, 180),
        )

    @classmethod
    def build_hubs(
        cls,
        hubs: list[Hub],
        to_screen: Callable[[int, int], tuple[float, float]],
        use_legend: bool,
    ) -> tuple[
        list[pyglet.shapes.Circle],
        list[pyglet.shapes.Circle],
        list[pyglet.text.Label],
        list[pyglet.sprite.Sprite],
        list[pyglet.text.Label],
    ]:
        """Build all drawable hub-related objects.

        Args:
            hubs: All hubs in the map.
            to_screen: Coordinate transform from map space to screen space.
            use_legend: Whether to display numeric labels instead of names.

        Returns:
            Drawable circles, borders, labels, drone sprites, and drone labels.
        """
        cercles, borders, labels, drones, label_drones = [], [], [], [], []
        for idx, hub in enumerate(hubs):
            x, y = to_screen(hub.x, hub.y)
            hub.x_px = x
            hub.y_px = y
            text = str(idx + 1) if use_legend else hub.name
            cercles.append(cls.make_circle(x, y, hub))
            borders.append(cls.make_circle(x, y, hub, 27, (117, 124, 136)))
            labels.append(cls.make_label(x, y, text, hub))
            if hub.nb_drone:
                drone, label_drone = cls.make_drone(hub)
                drones.append(drone)
                label_drones.append(label_drone)
        return cercles, borders, labels, drones, label_drones

    @classmethod
    def build_arrows(
        cls,
        hubs: list[Hub],
        to_screen: Callable[[int, int], tuple[float, float]],
    ) -> list[tuple[pyglet.shapes.Line, pyglet.shapes.Triangle]]:
        """Build all connection arrows for the map.

        Args:
            hubs: All hubs in the map.
            to_screen: Coordinate transform from map space to screen space.

        Returns:
            A list of arrow shape pairs.
        """
        arrows = []
        for hub in hubs:
            for connection in hub.connection:
                target = next(
                    (h for h in hubs if h.name == connection.linked_to), None)
                if target is None:
                    continue
                x1, y1 = to_screen(hub.x, hub.y)
                x2, y2 = to_screen(target.x, target.y)
                arrows.append(cls.make_arrow(x1, y1, x2, y2))
        return arrows

    @classmethod
    def build_legend(
        cls,
        hubs: list[Hub],
        window: Any,
    ) -> list[tuple[pyglet.shapes.Rectangle, pyglet.text.Label]]:
        """Build the legend items for the visible hubs.

        Args:
            hubs: All hubs in the map.
            window: Window used to compute legend placement.

        Returns:
            A list of legend background and label pairs.
        """
        legend_x = 20
        legend_y_top = window.height - 40
        line_h = 22
        col_width = 200
        cols = 3
        padding = 6

        items = []
        for idx, hub in enumerate(hubs):
            col = idx % cols
            row = idx // cols
            lx = legend_x + col * col_width
            ly = legend_y_top - row * line_h
            items.append(cls.make_legend_item(
                idx, hub, lx, ly, line_h, col_width, padding))
        return items

    @staticmethod
    def compute_layout(
        hubs: list[Hub],
        window: Any,
    ) -> Callable[[int, int], tuple[float, float]]:
        """Compute a map-to-screen coordinate transform.

        Args:
            hubs: All hubs in the map.
            window: Window used to fit the map on screen.

        Returns:
            A function mapping map coordinates to screen coordinates.
        """
        min_x = min(h.x for h in hubs)
        min_y = min(h.y for h in hubs)
        max_x = max(h.x for h in hubs)
        max_y = max(h.y for h in hubs)

        margin = 50
        scale_x = (window.width - margin * 2) / (max_x - min_x or 1)
        scale_y = (window.height - margin * 2) / (max_y - min_y or 1)
        scale = min(scale_x, scale_y)
        content_w = (max_x - min_x) * scale
        content_h = (max_y - min_y) * scale
        offset_x = (window.width - content_w) / 2
        offset_y = (window.height - content_h) / 2

        def to_screen(x: int, y: int) -> tuple[float, float]:
            return (x - min_x) * scale + offset_x, \
                   (y - min_y) * scale + offset_y

        return to_screen

    @classmethod
    def run(cls, hubs: list[Hub]) -> None:
        """Launch the fullscreen simulation window.

        Args:
            hubs: All hubs to render and simulate.
        """
        window = pyglet.window.Window(fullscreen=True)
        pyglet.gl.glClearColor(0.1, 0.4, 0.1, 1.0)

        to_screen = cls.compute_layout(hubs, window)
        use_legend = max(Counter(round(h.y)
                         for h in hubs).values()) > cls.legend_threshold

        cercles, borders, labels, drones, label_drones = cls.build_hubs(
            hubs, to_screen, use_legend)
        arrows = cls.build_arrows(hubs, to_screen)
        legend_items = cls.build_legend(hubs, window) if use_legend else []
        help_label = cls.make_help_label(window, use_legend)

        def step() -> None:
            """Advance one simulation step and refresh drone sprites."""
            cls.action(hubs)
            drones.clear()
            label_drones.clear()
            for hub in hubs:
                if hub.nb_drone:
                    drone, label_drone = cls.make_drone(hub)
                    drones.append(drone)
                    label_drones.append(label_drone)
            window.dispatch_event("on_draw")

        def update(dt: float) -> None:
            """Pyglet clock callback that advances the simulation."""
            step()

        @window.event
        def on_draw() -> None:
            """Draw a full frame of the simulation window."""
            window.clear()
            for border in borders:
                border.draw()
            for cercle in cercles:
                cercle.draw()
            for line, tip in arrows:
                line.draw()
                tip.draw()
            for label in labels:
                label.draw()
            if use_legend and cls.legend_visible:
                for bg, lbl in legend_items:
                    bg.draw()
                    lbl.draw()
            help_label.draw()
            for drone in drones:
                drone.draw()
            for label_drone in label_drones:
                label_drone.draw()

        @window.event
        def on_key_press(symbol: int, modifiers: int) -> None:
            """Handle keyboard shortcuts for simulation control."""
            if symbol == pyglet.window.key.ESCAPE:
                window.close()
            if symbol == pyglet.window.key.L and use_legend:
                cls.legend_visible = not cls.legend_visible
            if symbol == pyglet.window.key.RIGHT:
                step()
                for hub in hubs:
                    print(hub.name, hub.nb_drone)

        pyglet.app.run()

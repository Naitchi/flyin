import math
import pyglet
from .hub import Hub
from enum import Enum
from collections import Counter


class ColorEnum(str, Enum):
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'
    YELLOW = 'yellow'
    NONE = 'none'

    def to_rgb(self) -> tuple[int, int, int]:
        return {
            ColorEnum.RED:    (220, 60,  60),
            ColorEnum.GREEN:  (60,  200, 80),
            ColorEnum.BLUE:   (60,  100, 220),
            ColorEnum.YELLOW: (240, 210, 40),
            ColorEnum.NONE:   (180, 180, 180),
        }[self]

    def label_rgb(self) -> tuple[int, int, int, int]:
        return {
            ColorEnum.RED:    (255, 255, 255, 255),
            ColorEnum.GREEN:  (0,   0,   0,   255),
            ColorEnum.BLUE:   (255, 255, 255, 255),
            ColorEnum.YELLOW: (30,  30,  30,  255),
            ColorEnum.NONE:   (0,   0,   0,   255),
        }[self]


class Display():
    legend_visible = False
    legend_threshold = 15

    @staticmethod
    def hub_color(hub: Hub) -> tuple[int, int, int]:
        color_attr = getattr(hub, 'color', ColorEnum.NONE)
        if isinstance(color_attr, ColorEnum):
            return color_attr.to_rgb()
        return (255, 80, 80)

    @staticmethod
    def hub_label_color(hub: Hub) -> tuple[int, int, int, int]:
        color_attr = getattr(hub, 'color', ColorEnum.NONE)
        if isinstance(color_attr, ColorEnum):
            return color_attr.label_rgb()
        return (0, 0, 0, 255)

    @staticmethod
    def make_arrow(x1, y1, x2, y2, radius=25, color=(255, 255, 255)):
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
    def make_circle(cls, x, y, hub: Hub) -> pyglet.shapes.Circle:
        return pyglet.shapes.Circle(x, y, 25, color=cls.hub_color(hub))

    @classmethod
    def make_label(cls, x, y, text, hub: Hub) -> pyglet.text.Label:
        return pyglet.text.Label(
            text,
            x=x, y=y,
            anchor_x="center", anchor_y="center",
            font_size=10,
            font_name="Arial Bold",
            color=cls.hub_label_color(hub),
        )

    @classmethod
    def make_legend_item(
        cls, idx, hub, lx, ly, line_h, col_width, padding
    ) -> tuple[pyglet.shapes.Rectangle, pyglet.text.Label]:
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
    def make_help_label(window, use_legend) -> pyglet.text.Label:
        hints = ["Echap : quit", "F11 : Fullscreen"]
        if use_legend:
            hints.append("L : Show hubs names")
        return pyglet.text.Label(
            "    ".join(hints),
            x=window.width - 10, y=10,
            anchor_x="right", anchor_y="bottom",
            font_size=9, color=(200, 200, 200, 180),
        )

    @classmethod
    def build_hubs(cls, hubs, to_screen, use_legend):
        cercles, labels = [], []
        for idx, hub in enumerate(hubs):
            x, y = to_screen(hub.x, hub.y)
            text = str(idx + 1) if use_legend else hub.name
            cercles.append(cls.make_circle(x, y, hub))
            labels.append(cls.make_label(x, y, text, hub))
        return cercles, labels

    @classmethod
    def build_arrows(cls, hubs, to_screen):
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
    def build_legend(cls, hubs, window):
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
    def compute_layout(hubs, window):
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

        def to_screen(x, y):
            return (x - min_x) * scale + offset_x, \
                   (y - min_y) * scale + offset_y

        return to_screen

    @classmethod
    def run(cls, hubs: list[Hub]):
        window = pyglet.window.Window(fullscreen=True)
        pyglet.gl.glClearColor(0.1, 0.4, 0.1, 1.0)

        to_screen = cls.compute_layout(hubs, window)
        use_legend = max(Counter(round(h.y)
                         for h in hubs).values()) > cls.legend_threshold

        cercles, labels = cls.build_hubs(hubs, to_screen, use_legend)
        arrows = cls.build_arrows(hubs, to_screen)
        legend_items = cls.build_legend(hubs, window) if use_legend else []
        help_label = cls.make_help_label(window, use_legend)

        @window.event
        def on_draw():
            window.clear()
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

        @window.event
        def on_key_press(symbol, modifiers):
            if symbol == pyglet.window.key.ESCAPE:
                window.close()
            if symbol == pyglet.window.key.F11:
                window.set_fullscreen(not window.fullscreen)
            if symbol == pyglet.window.key.L and use_legend:
                cls.legend_visible = not cls.legend_visible

        pyglet.app.run()

import math
import pyglet
from .hub import Hub
from enum import Enum


# TODO modifier ca pour que ca donnes les valeurs rgb
class ColorEnum(str, Enum):
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'
    YELLOW = 'yellow'
    NONE = 'none'
# TODO faire un enum pareil de couleur mais qui choisi la couleur du label
# en fonction de la couleur du hub
# par exemple pour l'enum yellow ca donnera du noir pour qu'on voit bien
# et pour blue ca sera du blanc (fin ca depends du bleu mais on verra)


class Display():
    @staticmethod
    def make_arrow(x1, y1, x2, y2, radius=25, color=(255, 255, 255)):
        angle = math.atan2(y2 - y1, x2 - x1)

        # Décaler le départ et l'arrivée sur le bord des cercles
        sx = x1 + radius * math.cos(angle)
        sy = y1 + radius * math.sin(angle)
        ex = x2 - radius * math.cos(angle)
        ey = y2 - radius * math.sin(angle)

        line = pyglet.shapes.Line(sx, sy, ex, ey, color=color)

        size = 12
        left_x = ex - size * math.cos(angle - math.pi/6)
        left_y = ey - size * math.sin(angle - math.pi/6)
        right_x = ex - size * math.cos(angle + math.pi/6)
        right_y = ey - size * math.sin(angle + math.pi/6)

        tip = pyglet.shapes.Triangle(
            ex, ey, left_x, left_y, right_x, right_y, color=color)
        return line, tip

    @classmethod
    def run(cls, hubs: list[Hub]):
        window = pyglet.window.Window(fullscreen=True)
        pyglet.gl.glClearColor(0.1, 0.4, 0.1, 1.0)

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
            sx = (x - min_x) * scale + offset_x
            sy = (y - min_y) * scale + offset_y
            return sx, sy

        cercles = []
        labels = []
        arrows = []
        for hub in hubs:
            x, y = to_screen(hub.x, hub.y)
            cercles.append(pyglet.shapes.Circle(x, y, 25, color=(255, 80, 80)))
            for connection in hub.connection:
                target = next(
                    (h for h in hubs if h.name == connection.linked_to), None)
                x1, y1 = to_screen(hub.x, hub.y)
                x2, y2 = to_screen(target.x, target.y)
                arrows.append(cls.make_arrow(x1, y1, x2, y2))
            labels.append(pyglet.text.Label(
                    hub.name,
                    x=x, y=y,
                    anchor_x="center", anchor_y="center",
                    font_size=10,
                    font_name="Arial Bold",
                    color=(0, 0, 0, 255)
            ))

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

        @window.event
        def on_key_press(symbol, modifiers):
            if symbol == pyglet.window.key.ESCAPE:
                window.close()
            if symbol == pyglet.window.key.F11:
                window.set_fullscreen(!window.fullscreen)

        pyglet.app.run()

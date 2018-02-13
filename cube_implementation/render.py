from PIL import Image, ImageDraw

colors = [
    (0xFF, 0xFF, 0xFF),  # White
    (0x02, 0xD0, 0x40),  # Green
    (0xEC, 0x00, 0x00),  # Red
    (0x30, 0x4F, 0xFE),  # Blue
    (0xFF, 0x8B, 0x24),  # Orange
    (0xFD, 0xD8, 0x35)   # Yellow
]


class Canvas:
    def set_size(self, size):
        raise NotImplementedError

    def draw_rect(self, xy, color):
        raise NotImplementedError

    def draw_poly(self, points, color):
        raise NotImplementedError

class ImageCanvas(Canvas):
    def __init__(self):
        self.img = None
        self.draw = None

    def set_size(self, size):
        self.img = Image.new("RGB", size)
        self.draw = ImageDraw.Draw(self.img)

    def draw_rect(self, xy, color):
        self.draw.rectangle(xy, fill=color)

    def draw_poly(self, points, color):
        self.draw.polygon(points, fill=color)

    def output(self, filename):
        del self.draw
        self.img.save(filename)

class Drawable:
    @staticmethod
    def render(p, screen):
        raise NotImplementedError

class SkewbDrawable(Drawable):
    face_size = 13

    initial_state = [
        0, 0, 0, 0, 0,
        1, 1, 1, 1, 1,
        2, 2, 2, 2, 2,
        3, 3, 3, 3, 3,
        4, 4, 4, 4, 4,
        5, 5, 5, 5, 5
    ]

    @classmethod
    def draw_face(cls, screen, xy, state, stickers):
        x, y = xy
        def translate(*points):
            return [(x + dx, y + dy) for dx, dy in points]

        def get_color(n):
            return colors[state[stickers[n]]]
        # center
        screen.draw_poly(
            translate((6, 2), (10, 6), (6, 10), (2, 6)),
            get_color(0)
        )
        # top left
        screen.draw_poly(translate((1, 1), (5, 1), (1, 5)), get_color(1))
        # top right
        screen.draw_poly(translate((7, 1), (11, 1), (11, 5)), get_color(2))
        # bottom left
        screen.draw_poly(translate((1, 7), (5, 11), (1, 11)), get_color(3))
        # bottom right
        screen.draw_poly(translate((11, 7), (11, 11), (7, 11)), get_color(4))

    @classmethod
    def render(cls, p, screen):
        p **= -1
        state = [cls.initial_state[p[i]] for i in range(30)]

        screen.set_size((4 * cls.face_size, 3 * cls.face_size))

        cls.draw_face(screen, (cls.face_size, 0), state, ( # top face
            0, 1, 2, 3, 4
        ))

        cls.draw_face(screen, (0, cls.face_size), state, ( # left face
            20, 21, 22, 23, 24
        ))

        cls.draw_face(screen, (cls.face_size, cls.face_size), state, ( # front face
            5, 6, 7, 8, 9
        ))

        cls.draw_face(screen, (2 * cls.face_size, cls.face_size), state, ( # right face
            10, 11, 12, 13, 14
        ))

        cls.draw_face(screen, (3 * cls.face_size, cls.face_size), state, ( # back face
            15, 16, 17, 18, 19
        ))

        cls.draw_face(screen, (cls.face_size, 2 * cls.face_size), state, ( # bottom face
            25, 28, 29, 26, 27
        ))


class CubeDrawable(Drawable):
    tile_size = 5
    border_size = 1
    face_size = 3 * tile_size + 4 * border_size

    initial_state = [
        0, 0, 0,
        0, 0, 0,
        0, 0, 0,

        1, 1, 1,  2, 2, 2,  3, 3, 3,  4, 4, 4,
        1, 1, 1,  2, 2, 2,  3, 3, 3,  4, 4, 4,
        1, 1, 1,  2, 2, 2,  3, 3, 3,  4, 4, 4,

        5, 5, 5,
        5, 5, 5,
        5, 5, 5
    ]

    @classmethod
    def draw_tile(cls, screen, xy, color):
        x, y = xy
        screen.draw_rect((x, y, x + cls.tile_size - 1, y + cls.tile_size - 1), colors[color])

    @classmethod
    def draw_face(cls, screen, xy, state, stickers):
        x, y = xy
        for j in range(3):
            for i in range(3):
                cls.draw_tile(screen, (
                        x + cls.border_size + i * (cls.tile_size + cls.border_size),
                        y + cls.border_size + j * (cls.tile_size + cls.border_size)
                    ),
                    state[stickers[3 * j + i]]
                )

    @classmethod
    def render(cls, p, screen):
        p **= -1
        state = [cls.initial_state[p[i]] for i in range(54)]

        screen.set_size((4 * cls.face_size, 3 * cls.face_size))

        cls.draw_face(screen, (cls.face_size, 0), state, (  # top face
            0, 1, 2,
            3, 4, 5,
            6, 7, 8
        ))

        cls.draw_face(screen, (0, cls.face_size), state, (  # left face
            18, 19, 20,
            30, 31, 32,
            42, 43, 44
        ))

        cls.draw_face(screen, (cls.face_size, cls.face_size), state, (  # front face
            9, 10, 11,
            21, 22, 23,
            33, 34, 35
        ))

        cls.draw_face(screen, (2 * cls.face_size, cls.face_size), state, (  # right face
            12, 13, 14,
            24, 25, 26,
            36, 37, 38
        ))

        cls.draw_face(screen, (3 * cls.face_size, cls.face_size), state, (  # back face
            15, 16, 17,
            27, 28, 29,
            39, 40, 41
        ))

        cls.draw_face(screen, (cls.face_size, 2 * cls.face_size), state, (  # bottom face
            51, 52, 53,
            48, 49, 50,
            45, 46, 47
        ))

from .render import Canvas, CubeDrawable, SkewbDrawable
from . import cube, skewb
from .perm import P
import pygame as pg
import time
import math
import threading
import collections


class InteractiveCanvas(Canvas):
    def __init__(self):
        self.surface = None

    def set_size(self, size):
        self.surface = pg.Surface(size)
        self.surface.fill((0, 0, 0))

    def draw_rect(self, xy, color):
        x0, y0, x1, y1 = xy
        w = x1 - x0 + 1
        h = y1 - y0 + 1
        pg.draw.rect(self.surface, color, (x0, y0, w, h))

    def draw_poly(self, points, color):
        pg.draw.polygon(self.surface, color, points)

    def get_surface(self):
        return self.surface


class Scene:
    def update(self, events, dt):
        pass

    def render(self, screen):
        pass

class DrawableScene(Scene):
    def __init__(self, drawable, initial_state = P(dict())):
        self.drawable = drawable
        self.state = initial_state
        self.initial_state = initial_state

    def render(self, screen):
        canvas = InteractiveCanvas()
        self.drawable.render(self.state, canvas)
        screen.blit(pg.transform.scale(canvas.get_surface(), screen.get_size()), (0, 0))

class CubeScene(DrawableScene):
    def __init__(self, initial_state = P(dict())):
        super().__init__(CubeDrawable, initial_state=initial_state)

class InteractiveCubeScene(CubeScene):
    def update(self, events, dt):
        for event in events:
            if event.type == pg.KEYDOWN:
                turn = {
                    30: cube.U,
                    40: cube.D,
                    46: cube.L,
                    27: cube.R,
                    41: cube.F,
                    56: cube.B,
                    58: cube.M,
                    26: cube.E,
                    39: cube.S,
                    53: cube.X,
                    29: cube.Y,
                    52: cube.Z
                }.get(event.scancode, None)
                if turn is None:
                    continue

                if pg.key.get_mods() & pg.KMOD_SHIFT != 0:
                    turn **= -1

                self.state @= turn

class InteractiveSkewbScene(DrawableScene):
    def __init__(self, initial_state = P(dict())):
         super().__init__(SkewbDrawable, initial_state=initial_state)

    def update(self, events, dt):
        for event in events:
            if event.type == pg.KEYDOWN:
                turn = {
                    30: skewb.U,
                    46: skewb.L,
                    27: skewb.R,
                    56: skewb.B,
                }.get(event.scancode, None)
                if turn is None:
                    continue

                if pg.key.get_mods() & pg.KMOD_SHIFT != 0:
                    turn **= -1

                self.state @= turn


class PlaybackCubeScene(CubeScene):
    def __init__(self, sequence, initial_state = P(dict()), frametime = 1):
        super().__init__(initial_state)
        self.sequence = list(sequence)
        self.initial_state = initial_state
        self.time = 0
        self.i = 0
        self.frametime = frametime

    def update(self, events, dt):
        self.time += dt
        if self.time > self.frametime:
            self.time -= self.frametime
            if self.i >= len(self.sequence):
                self.state = self.initial_state
                self.i = 0
            else:
                self.state @= self.sequence[self.i]
                self.i += 1

class StepCubeScene(CubeScene):
    def __init__(self, sequence, initial_state = P(dict())):
        super().__init__(initial_state)
        self.sequence = list(sequence)
        self.i = -1

    def update(self, events, dt):
        for event in events:
            if event.type == pg.KEYDOWN:
                if event.scancode == 113 or \
                   (pg.key.get_mods() & pg.KMOD_SHIFT != 0 and event.scancode == 65):
                    # step back
                    if self.i >= 0:
                        self.state @= (self.sequence[self.i] ** -1)
                        self.i -= 1
                elif event.scancode in (65, 114):
                    # step fwd
                    if (self.i + 1) < len(self.sequence):
                        self.i += 1
                        self.state @= self.sequence[self.i]

class StdinCubeScene(CubeScene):
    def __init__(self, initial_state = P(dict())):
        super().__init__(initial_state)
        self.q = collections.deque()
        self.lock = threading.Lock()

        def stdin_reader(q, lock):
            while True:
                try:
                    inputs = list(input())
                except EOFError:
                    continue
                for s in inputs:
                    s = s.upper()
                    if s in "UDLRFBMESXYZ'":
                        with lock:
                            q.append(s)

        self.reader = threading.Thread(target=stdin_reader, args=(self.q, self.lock), daemon=True)
        self.reader.start()

    def update(self, events, dt):
        with self.lock:
            for event in events:
                if event.type == pg.KEYDOWN and event.scancode == 65:
                    # spacebar pressed
                    self.state = self.initial_state
            while len(self.q) > 0:
                s = self.q.popleft()
                t = getattr(cube, s)
                if len(self.q) > 0 and self.q[0] == '\'':
                    t **= -1
                    self.q.popleft()
                self.state @= t


def run(scene):

    W, H = win_w, win_h = 640, 480

    pg.init()

    win_offset_x = win_offset_y = 0

    W_FLAGS = (pg.HWSURFACE | pg.DOUBLEBUF | pg.RESIZABLE)

    window = pg.display.set_mode((win_w, win_h), W_FLAGS)
    screen = pg.Surface((W, H), pg.SRCALPHA, 32)

    font = pg.font.SysFont(None, 24)  # default font
    frames = 0
    fpstext = font.render(f"{frames} FPS", True, (255, 128, 0))
    running_t = time.time()

    FPS = 60
    clock = pg.time.Clock()
    running = True

    try:
        while running:
            dt = clock.tick(FPS) / 1000  # milliseconds
            current_t = time.time()
            if current_t - running_t > 1:
                fpstext = font.render(f"{frames} FPS", True, (255, 128, 0))
                running_t += 1
                frames = 0

            events = []
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                elif event.type == pg.VIDEORESIZE:
                    # the window has been resized
                    win_w, win_h = event.size
                    pg.display.set_mode((win_w, win_h), W_FLAGS)

                    # keep aspect ratio of screen
                    if (win_w / win_h) < (W / H):
                        tmp = int(H / W * win_w)
                        win_offset_x = 0
                        win_offset_y = (win_h - tmp) // 2
                        win_h = tmp
                    else:
                        tmp = int(W / H * win_h)
                        win_offset_x = (win_w - tmp) // 2
                        win_offset_y = 0
                        win_w = tmp
                else:
                    events.append(event)

            scene.update(events, dt)

            # render stuff on screen
            screen.fill((0, 0, 0))  # clear
            screen.blit(fpstext, (0, 0))

            scene.render(screen)

            # fit screen to window
            window.blit(pg.transform.scale(screen, (win_w, win_h)), (win_offset_x, win_offset_y))
            pg.display.flip()  # update window
            frames += 1
    except KeyboardInterrupt:
        pass

    pg.quit()

if __name__ == "__main__":
    run(InteractiveCubeScene())

"""Generate the pixel-art GIFs for the profile README."""
import math
import os
import sys

from PIL import Image

OUT = sys.argv[1]

PAL = {
    "K": (31, 35, 40),     # outline
    "W": (255, 255, 255),
    "G": (139, 148, 158),
    "g": (208, 215, 222),
    "B": (88, 166, 255),
    "b": (31, 111, 235),
    "N": (63, 185, 80),
    "n": (35, 134, 54),
    "R": (248, 81, 73),
    "r": (190, 45, 45),
    "Y": (242, 204, 96),
    "y": (210, 153, 34),
    "O": (219, 109, 40),
    "S": (240, 185, 141),
    "s": (201, 138, 94),
    "D": (22, 27, 34),     # terminal body
    "L": (48, 54, 61),     # terminal border
    "l": (33, 38, 45),     # terminal title bar
    "T": (201, 209, 217),  # terminal text
    "H": (74, 48, 36),     # hair
    "h": (110, 74, 54),    # hair highlight
    "M": (166, 112, 70),   # desk wood
    "m": (122, 80, 50),    # desk wood shade
    "p": (255, 150, 150),  # blush
}
KEYS = list(PAL)


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.p = [[None] * w for _ in range(h)]

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.p[y][x] = c

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, c)

    def ellipse(self, cx, cy, rx, ry, c, ymax=None):
        for y in range(self.h):
            for x in range(self.w):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1 and (ymax is None or y <= ymax):
                    self.set(x, y, c)

    def grid(self, x0, y0, rows):
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch != ".":
                    self.set(x0 + i, y0 + j, ch)

    def outline(self, c="K"):
        add = []
        for y in range(self.h):
            for x in range(self.w):
                if self.p[y][x] is not None:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.w and 0 <= ny < self.h and self.p[ny][nx] not in (None, c):
                        add.append((x, y))
                        break
        for x, y in add:
            self.p[y][x] = c
        return self


def to_image(c, scale):
    im = Image.new("P", (c.w, c.h), 0)
    im.putpalette([255, 0, 255] + [v for k in KEYS for v in PAL[k]])
    px = im.load()
    for y in range(c.h):
        for x in range(c.w):
            ch = c.p[y][x]
            px[x, y] = 0 if ch is None else KEYS.index(ch) + 1
    return im.resize((c.w * scale, c.h * scale), Image.NEAREST)


def save(name, frames, durations, scale):
    ims = [to_image(f, scale) for f in frames]
    if isinstance(durations, int):
        durations = [durations] * len(ims)
    ims[0].save(os.path.join(OUT, name), save_all=True, append_images=ims[1:],
                duration=durations, loop=0, transparency=0, disposal=2, optimize=False)


# --- waving hand -----------------------------------------------------------
def wave():
    frames = []
    for k in (0, 0.2, 0.38, 0.2, 0, -0.2, -0.38, -0.2):
        base = Canvas(24, 18)
        ox = 5
        for x0, top in ((4, 4), (6, 2), (8, 3), (10, 5)):
            base.rect(ox + x0, top, ox + x0 + 1, 10, "S")
        for x in (5, 7, 9):
            base.rect(ox + x, 3, ox + x, 9, "s")
        base.rect(ox + 4, 10, ox + 11, 14, "S")
        base.rect(ox + 2, 9, ox + 3, 11, "S")
        base.set(ox + 3, 12, "S")
        base.rect(ox + 5, 15, ox + 10, 16, "b")
        sheared = Canvas(24, 18)
        for y in range(18):
            shift = round(k * (16 - y))
            for x in range(24):
                if base.p[y][x]:
                    sheared.set(x + shift, y, base.p[y][x])
        frames.append(sheared.outline())
    save("wave.gif", frames, 90, 4)


# --- crawling bug ----------------------------------------------------------
def bug():
    frames = []
    for f in range(4):
        c = Canvas(22, 15)
        bob = f % 2
        legs = (0, 1, 0, -1)[f]
        for lx in (6, 9, 12):
            c.set(lx, 11, "G")
            c.set(lx + legs, 12, "G")
        c.ellipse(9, 9 - bob, 6.5, 5, "R", ymax=10 - bob)
        c.rect(3, 10 - bob, 15, 10 - bob, "r")
        for sx, sy in ((6, 6), (10, 5), (8, 8), (12, 8)):
            c.set(sx, sy - bob, "K")
            c.set(sx + 1, sy - bob, "K")
        c.ellipse(17, 8 - bob, 2.6, 2.4, "L")
        c.set(18, 7 - bob, "W")
        tw = f in (1, 2)
        c.set(18, 4 - bob, "G")
        c.set(19, 3 - bob - tw, "G")
        frames.append(c.outline())
    save("bug.gif", frames, 130, 4)


# --- robot -----------------------------------------------------------------
def robot():
    frames = []
    for f in range(8):
        c = Canvas(18, 18)
        c.rect(8, 2, 9, 3, "G")
        c.rect(7, 0, 10, 1, "R" if f % 2 == 0 else "r")
        c.rect(3, 4, 14, 13, "g")
        c.rect(1, 7, 2, 10, "G")
        c.rect(15, 7, 16, 10, "G")
        c.rect(5, 6, 12, 11, "D")
        if f == 5:
            c.rect(6, 8, 7, 8, "B")
            c.rect(10, 8, 11, 8, "B")
        else:
            c.rect(6, 7, 7, 8, "B")
            c.rect(10, 7, 11, 8, "B")
        c.rect(7 if f % 4 < 2 else 8, 10, 10 if f % 4 < 2 else 9, 10, "N")
        c.rect(6, 14, 11, 16, "b")
        frames.append(c.outline())
    save("robot.gif", frames, 160, 4)


# --- location pin ----------------------------------------------------------
def pin():
    frames = []
    for lift in (0, 1, 2, 3, 3, 2, 1, 0):
        c = Canvas(16, 20)
        top = 4 - lift
        c.ellipse(7.5, top + 4.5, 5, 5, "R")
        for i, (x0, x1) in enumerate(((4, 11), (5, 10), (6, 9), (7, 8))):
            c.rect(x0, top + 9 + i, x1, top + 9 + i, "R")
        c.ellipse(7.5, top + 4.5, 1.8, 1.8, "W")
        c.outline()
        half = 4 - lift // 2
        c.rect(8 - half, 19, 7 + half, 19, "G")
        frames.append(c)
    save("pin.gif", frames, 100, 4)


# --- heart -----------------------------------------------------------------
HEART_S = [
    ".RR...RR.",
    "RWRR.RRRR",
    "RRRRRRRRR",
    "RRRRRRRRr",
    ".RRRRRRr.",
    "..RRRRr..",
    "...RRr...",
    "....R....",
]
HEART_L = [
    ".RRR...RRR.",
    "RRWRR.RRRRR",
    "RWRRRRRRRRR",
    "RRRRRRRRRRR",
    "RRRRRRRRRRr",
    ".RRRRRRRRr.",
    "..RRRRRRr..",
    "...RRRRr...",
    "....RRr....",
    ".....R.....",
]


def heart():
    def frame(big):
        c = Canvas(15, 14)
        if big:
            c.grid(2, 2, HEART_L)
        else:
            c.grid(3, 3, HEART_S)
        return c.outline()
    seq = [False, True, False, True, False]
    save("heart.gif", [frame(b) for b in seq], [500, 110, 110, 110, 500], 4)


# --- small terminal icon ---------------------------------------------------
def terminal_icon():
    frames = []
    for on in (True, False):
        c = Canvas(18, 15)
        c.rect(0, 0, 17, 14, "L")
        c.rect(1, 1, 16, 2, "l")
        c.rect(1, 3, 16, 13, "D")
        c.set(2, 1, "R")
        c.set(4, 1, "y")
        c.set(6, 1, "N")
        c.grid(3, 5, ["N..", ".N.", "..N", ".N.", "N.."])
        if on:
            c.rect(8, 9, 12, 9, "T")
        frames.append(c)
    save("terminal.gif", frames, 450, 4)


# --- rocket ----------------------------------------------------------------
def rocket():
    flames = [
        ["YYYY", ".OO.", "...."],
        ["OYYO", "YOOY", ".OO."],
        ["YYYY", "OYYO", ".YO."],
    ]
    frames = []
    for f in range(6):
        c = Canvas(14, 20)
        dy = 1 if f % 2 else 0
        c.rect(6, 1 + dy, 7, 1 + dy, "W")
        c.rect(5, 2 + dy, 8, 2 + dy, "W")
        c.rect(4, 3 + dy, 9, 12 + dy, "W")
        c.rect(9, 3 + dy, 9, 12 + dy, "g")
        c.rect(6, 5 + dy, 7, 6 + dy, "B")
        c.set(6, 5 + dy, "W")
        for i in range(4):
            c.rect(3 - (i > 0), 9 + i + dy, 3, 9 + i + dy, "R")
            c.rect(10, 9 + i + dy, 10 + (i > 0), 9 + i + dy, "R")
        c.rect(5, 13 + dy, 8, 13 + dy, "G")
        c.grid(5, 14 + dy, flames[f % 3])
        frames.append(c.outline())
    save("rocket.gif", frames, 110, 4)


if __name__ == "__main__":
    wave(); bug(); robot(); pin(); heart(); terminal_icon(); rocket()
    print("ok")

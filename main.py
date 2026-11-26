#!/usr/bin/env python3
"""news-image-20261126: draw one 1024x1024 PNG summing up the world news of
Thursday 26 November 2026. Pure Python 3.13 standard library only (no Pillow):
a hand-written PNG encoder (zlib) over a small raster canvas, a 5x7 bitmap
font, and procedural pictograms. Deterministic: same bytes on every run.

Writes $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font: 5x7
# Each glyph is 7 rows of 5 bits, '#' = on.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '*': ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '>': ("10000", "01000", "00100", "00010", "00100", "01000", "10000"),
    '<': ("00001", "00010", "00100", "01000", "00100", "00010", "00001"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
}

CHAR_W, CHAR_H = 6, 7  # 5 px glyph + 1 px tracking


def text_width(s, scale):
    return len(s) * CHAR_W * scale - scale


def wrap_text(s, max_width, scale):
    """Greedy word wrap; returns a list of lines that fit max_width px."""
    words = s.split(' ')
    lines, cur = [], ''
    for w in words:
        trial = w if not cur else cur + ' ' + w
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def _off(self, x, y):
        return (y * self.w + x) * 3

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            o = self._off(x, y)
            self.px[o:o + 3] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + w, self.w), min(y + h, self.h)
        for yy in range(y0, y1):
            o = self._off(x0, yy)
            self.px[o:o + (x1 - x0) * 3] = c * (x1 - x0)

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        x, y, d = 0, r, 3 - 2 * r
        while x <= y:
            for px, py in ((cx + x, cy + y), (cx - x, cy + y), (cx + x, cy - y),
                           (cx - x, cy - y), (cx + y, cy + x), (cx - y, cy + x),
                           (cx + y, cy - x), (cx - y, cy - x)):
                self.set(px, py, c)
            x += 1
            if d > 0:
                y -= 1
                d += 4 * (x - y) + 10
            else:
                d += 4 * x + 6

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
            self.rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def poly(self, pts, c):
        """Scanline fill of a simple polygon (list of (x, y))."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), y, max(1, int(xs[i + 1]) - int(xs[i])), 1, c)

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT['?'])
            for r in range(7):
                row = g[r]
                for col in range(5):
                    if row[col] == '1':
                        self.rect(cx + col * scale, y + r * scale,
                                  scale, scale, c)
            cx += CHAR_W * scale
        return cx

    def text_center(self, cx, y, s, scale, c):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, c)

    def text_lines(self, x, y, lines, scale, c, gap=4):
        for ln in lines:
            self.text(x, y, ln, scale, c)
            y += CHAR_H * scale + gap
        return y


# ---------------------------------------------------------------- PNG encode
def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack('>I', len(data)) + tag + data
        return out + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)

    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', comp) + chunk(b'IEND', b''))

# ---------------------------------------------------------------- palette
PAPER = bytes((248, 244, 233))
WHITE = bytes((255, 255, 255))
INK = bytes((26, 26, 26))
NAVY = bytes((20, 33, 61))
GOLD = bytes((201, 162, 39))
RED = bytes((185, 28, 28))
BLUE = bytes((37, 99, 235))
SKY = bytes((125, 190, 235))
TEAL = bytes((13, 148, 136))
GREEN = bytes((22, 163, 74))
ORANGE = bytes((234, 88, 12))
AMBER = bytes((245, 158, 11))
GREY = bytes((100, 116, 139))
LIGHT = bytes((226, 232, 240))
DARKGREY = bytes((71, 85, 105))
PURPLE = bytes((126, 34, 206))
BROWN = bytes((120, 53, 15))
YELLOW = bytes((250, 204, 21))
PINK = bytes((219, 39, 119))

# ---------------------------------------------------------------- pictograms
# Each draws inside a box (ox, oy, w, h) and returns nothing.


def pic_ship(cv, ox, oy, w, h):
    # Cargo ship under a tariff chart: hull, stacked containers, waves.
    cv.poly([(ox + 6, oy + h - 34), (ox + w - 6, oy + h - 34),
             (ox + w - 22, oy + h - 12), (ox + 22, oy + h - 12)], NAVY)
    cv.rect(ox + 14, oy + h - 58, 26, 24, RED)
    cv.rect(ox + 44, oy + h - 58, 26, 24, BLUE)
    cv.rect(ox + 74, oy + h - 58, 26, 24, AMBER)
    cv.rect(ox + 28, oy + h - 82, 26, 24, TEAL)
    cv.rect(ox + 58, oy + h - 82, 26, 24, GREEN)
    cv.rect(ox + w - 26, oy + h - 78, 14, 44, WHITE)
    cv.rect(ox + w - 26, oy + h - 78, 14, 8, RED)
    for i, wx in enumerate((ox + 2, ox + 34, ox + 66, ox + 98)):
        cv.line(wx, oy + h - 4, wx + 16, oy + h - 4, SKY if i % 2 else BLUE)
    # tariff bars rising top-right
    bx = ox + w - 52
    for i, bh in enumerate((10, 18, 28)):
        cv.rect(bx + i * 14, oy + 30 - bh, 10, bh, RED if i == 2 else AMBER)


def pic_storm(cv, ox, oy, w, h):
    # Nor'easter cloud, rain, lightning, grounded parade balloon.
    cx, cy = ox + w // 2, oy + 34
    cv.disc(cx - 26, cy, 20, DARKGREY)
    cv.disc(cx + 4, cy - 8, 24, DARKGREY)
    cv.disc(cx + 30, cy, 18, DARKGREY)
    cv.rect(cx - 46, cy - 2, 92, 20, DARKGREY)
    for i, rx in enumerate((-36, -16, 4, 24)):
        cv.line(cx + rx, cy + 24, cx + rx - 6, cy + 40, SKY)
    cv.poly([(cx + 8, cy + 44), (cx - 4, cy + 66), (cx + 6, cy + 66),
             (cx - 2, cy + 86), (cx + 18, cy + 58), (cx + 8, cy + 58)],
            YELLOW)
    # parade balloon, grounded: ellipse + basket, rope slack
    cv.disc(ox + 30, oy + h - 22, 16, PINK)
    cv.rect(ox + 14, oy + h - 38, 32, 12, PINK)
    cv.rect(ox + 24, oy + h - 8, 12, 8, BROWN)


def pic_flame(cv, ox, oy, w, h):
    # Refinery tower + flame + oil barrel.
    cv.poly([(ox + 18, oy + h - 10), (ox + 30, oy + 16), (ox + 42, oy + h - 10)],
            DARKGREY)
    cv.line(ox + 18, oy + h - 30, ox + 42, oy + h - 30, DARKGREY)
    cv.line(ox + 22, oy + h - 52, ox + 38, oy + h - 52, DARKGREY)
    cv.rect(ox + 56, oy + h - 44, 34, 34, GREY)
    cv.rect(ox + 56, oy + h - 44, 34, 6, INK)
    cx = ox + 72
    cv.poly([(cx - 14, oy + h - 48), (cx, oy + h - 84), (cx + 14, oy + h - 48)],
            ORANGE)
    cv.poly([(cx - 7, oy + h - 48), (cx, oy + h - 68), (cx + 7, oy + h - 48)],
            YELLOW)
    cv.disc(ox + 104, oy + h - 22, 12, INK)
    cv.rect(ox + 92, oy + h - 34, 24, 4, AMBER)


def pic_jet(cv, ox, oy, w, h):
    # Fighter jet diving, blast star behind.
    cv.poly([(ox + 16, oy + 34), (ox + 78, oy + 18), (ox + 108, oy + 30),
             (ox + 78, oy + 40), (ox + 30, oy + 52)], NAVY)
    cv.poly([(ox + 46, oy + 34), (ox + 58, oy + 8), (ox + 68, oy + 34)],
            NAVY)
    cv.poly([(ox + 20, oy + 40), (ox + 8, oy + 62), (ox + 26, oy + 44)],
            NAVY)
    cv.rect(ox + 84, oy + 22, 14, 10, SKY)
    for i in range(5):
        a = i * 6.283 / 5
        x1 = ox + 12 + int(10 * math.cos(a))
        y1 = oy + 78 + int(10 * math.sin(a))
        x2 = ox + 12 + int(22 * math.cos(a))
        y2 = oy + 78 + int(22 * math.sin(a))
        cv.line(x1, y1, x2, y2, ORANGE)
    cv.disc(ox + 12, oy + 78, 8, YELLOW)
    for x in (ox + 88, ox + 100):
        cv.line(x, oy + 52, x - 8, oy + 58, GREY)


def pic_missile(cv, ox, oy, w, h):
    # Tactical missile on launcher, launch flame.
    cv.rect(ox + 52, oy + 12, 16, 62, RED)
    cv.poly([(ox + 52, oy + 12), (ox + 68, oy + 12), (ox + 60, oy - 2)],
            RED)
    cv.poly([(ox + 52, oy + 74), (ox + 40, oy + 92), (ox + 52, oy + 86)],
            DARKGREY)
    cv.poly([(ox + 68, oy + 74), (ox + 80, oy + 92), (ox + 68, oy + 86)],
            DARKGREY)
    cv.poly([(ox + 54, oy + 92), (ox + 60, oy + 108), (ox + 66, oy + 92)],
            ORANGE)
    cv.rect(ox + 20, oy + h - 16, 80, 10, INK)
    cv.disc(ox + 30, oy + h - 6, 6, INK)
    cv.disc(ox + 90, oy + h - 6, 6, INK)
    cv.disc(ox + 104, oy + 18, 5, AMBER)
    cv.disc(ox + 110, oy + 34, 4, AMBER)


def pic_chart(cv, ox, oy, w, h):
    # Market chart plunging: axes, falling red line, arrow.
    cv.vline(ox + 14, oy + 10, h - 26, INK)
    cv.hline(ox + 14, oy + h - 16, w - 26, INK)
    pts = [(ox + 18, oy + 18), (ox + 40, oy + 26), (ox + 58, oy + 44),
           (ox + 76, oy + 40), (ox + 94, oy + 66), (ox + 112, oy + 84)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], RED)
        cv.line(a[0], a[1] + 1, b[0], b[1] + 1, RED)
        cv.disc(a[0], a[1], 3, RED)
    cv.disc(pts[-1][0], pts[-1][1], 3, RED)
    cv.poly([(pts[-1][0] - 8, pts[-1][1] - 4), (pts[-1][0] + 8, pts[-1][1] - 4),
             (pts[-1][0], pts[-1][1] + 10)], RED)
    cv.text(ox + 16, oy + 4, '-4%', 1, RED)


def pic_satellite(cv, ox, oy, w, h):
    # Starmind satellite: bus, solar wings, dish, orbit arc, stars.
    for sx, sy in ((ox + 12, oy + 10), (ox + 100, oy + 22), (ox + 24, oy + 84),
                   (ox + 108, oy + 78)):
        cv.disc(sx, sy, 2, GOLD)
    cv.circle(ox + 60, oy + 54, 46, SKY)
    cv.rect(ox + 50, oy + 42, 20, 24, NAVY)
    cv.rect(ox + 18, oy + 46, 28, 16, BLUE)
    cv.rect(ox + 74, oy + 46, 28, 16, BLUE)
    cv.line(ox + 22, oy + 50, ox + 22, oy + 58, WHITE)
    cv.line(ox + 78, oy + 50, ox + 78, oy + 58, WHITE)
    cv.circle(ox + 60, oy + 34, 8, GOLD)
    cv.line(ox + 60, oy + 42, ox + 60, oy + 46, GOLD)
    cv.line(ox + 84, oy + 76, ox + 104, oy + 96, TEAL)
    cv.disc(ox + 104, oy + 96, 4, TEAL)


def pic_tanker(cv, ox, oy, w, h):
    # Fuel tanker truck, flames above, smoke.
    cv.disc(ox + 30, oy + 14, 10, GREY)
    cv.disc(ox + 44, oy + 8, 8, GREY)
    cv.disc(ox + 58, oy + 14, 9, GREY)
    cv.rect(ox + 16, oy + 62, 62, 26, AMBER)
    cv.rect(ox + 78, oy + 66, 26, 22, RED)
    cv.rect(ox + 84, oy + 70, 12, 10, SKY)
    cv.disc(ox + 32, oy + 92, 9, INK)
    cv.disc(ox + 88, oy + 92, 9, INK)
    cv.disc(ox + 32, oy + 92, 4, GREY)
    cv.disc(ox + 88, oy + 92, 4, GREY)
    cx = ox + 46
    cv.poly([(cx - 16, oy + 62), (cx - 4, oy + 34), (cx + 4, oy + 48),
             (cx + 16, oy + 62)], ORANGE)
    cv.poly([(cx - 7, oy + 62), (cx, oy + 44), (cx + 7, oy + 62)], YELLOW)


def pic_plane(cv, ox, oy, w, h):
    # Airliner over Gulf waves, splash below.
    cv.poly([(ox + 14, oy + 40), (ox + 86, oy + 32), (ox + 108, oy + 38),
             (ox + 86, oy + 44), (ox + 28, oy + 48)], SKY)
    cv.poly([(ox + 54, oy + 38), (ox + 62, oy + 18), (ox + 70, oy + 38)],
            SKY)
    cv.poly([(ox + 18, oy + 42), (ox + 8, oy + 58), (ox + 26, oy + 46)],
            SKY)
    for i, wy in enumerate((oy + h - 18, oy + h - 8)):
        for x in range(ox + 4, ox + w - 4, 16):
            cv.line(x, wy, x + 8, wy - 4 if i == 0 else wy, BLUE)
    cv.disc(ox + 60, oy + h - 26, 5, WHITE)
    cv.disc(ox + 72, oy + h - 30, 4, WHITE)
    cv.disc(ox + 48, oy + h - 24, 4, WHITE)


def pic_gate(cv, ox, oy, w, h):
    # Open gate, three freed figures walking out, check mark.
    cv.rect(ox + 12, oy + 10, 6, h - 30, INK)
    cv.rect(ox + 58, oy + 10, 6, h - 30, INK)
    cv.rect(ox + 12, oy + 10, 52, 6, INK)
    cv.line(ox + 18, oy + 16, ox + 40, oy + 60, INK)
    cv.line(ox + 18, oy + 16, ox + 40, oy + 60, INK)
    for i, fx in enumerate((ox + 72, ox + 88, ox + 104)):
        cv.disc(fx, oy + 40, 7, TEAL if i != 1 else GREEN)
        cv.rect(fx - 5, oy + 48, 10, 26, TEAL if i != 1 else GREEN)
        cv.rect(fx - 5, oy + 74, 4, 20, INK)
        cv.rect(fx + 1, oy + 74, 4, 20, INK)
    cv.line(ox + 8, oy + h - 8, ox + 16, oy + h - 2, GREEN)
    cv.line(ox + 16, oy + h - 2, ox + 30, oy + h - 16, GREEN)

# ---------------------------------------------------------------- stories
# (tag, tag colour, headline, sub-line, pictogram)
# Facts double-checked 26 Nov 2026 against Reuters, AP, AFP, WSJ,
# Al Jazeera, Financial Express, Times Now and Qatar Tribune.
LEAD = ("TRADE WAR, ROUND TWO",
        "US UNVEILS SWEEPING NEW TARIFFS",
        "14 PARTNERS HIT - CHINA FACES UP TO 40%")

STORIES = [
    ("USA", RED, "THANKSGIVING STORM CHAOS",
     "MACY'S PARADE POSTPONED", pic_storm),
    ("ENERGY", ORANGE, "HOUTHIS STRIKE SAUDI REFINERY",
     "BRENT JUMPS TO $94.61", pic_flame),
    ("WAR", DARKGREY, "UKRAINE HITS RUSSIAN AIR BASE",
     "FIVE PLANES DAMAGED", pic_jet),
    ("ASIA", PURPLE, "KIM: MORE TACTICAL NUKES",
     "N. KOREA ORDERS WIDER USE", pic_missile),
    ("MARKETS", RED, "WALL ST AI ROUT DEEPENS",
     "NASDAQ FELL 4% IN A DAY", pic_chart),
    ("SPACE", NAVY, "SPACEX GETS 1M SATELLITES",
     "ORBITAL DATA CENTRES: FCC", pic_satellite),
    ("EGYPT", BROWN, "31 KILLED IN CAIRO TANKER FIRE",
     "TANKER FIRE ON RING ROAD", pic_tanker),
    ("USA", BLUE, "SIX DEAD IN GULF PLANE CRASH",
     "OFF MISSISSIPPI COAST", pic_plane),
    ("LATAM", TEAL, "COLOMBIA FREES HOSTAGES",
     "SUPERMARKET SIEGE ENDS", pic_gate),
]


def draw_cell(cv, x, y, w, h, tag, tagc, headline, sub, pic):
    cv.rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, h, LIGHT)  # border via outline below
    cv.rect(x, y, w, 2, INK)
    cv.rect(x, y + h - 2, w, 2, INK)
    cv.rect(x, y, 2, h, INK)
    cv.rect(x + w - 2, y, 2, h, INK)
    cv.rect(x + 2, y + 2, w - 4, 26, tagc)
    cv.text(x + 10, y + 9, tag, 2, WHITE)
    pic(cv, x + (w - 124) // 2, y + 34, 124, 96)
    lines = wrap_text(headline, w - 20, 2)
    yy = y + 136
    for ln in lines[:2]:
        cv.text(x + 10, yy, ln, 2, INK)
        yy += 16
    while text_width(sub, 2) > w - 20:
        sub = sub[:-1]
    cv.text(x + 10, y + h - 24, sub, 2, DARKGREY)


def draw():
    cv = Canvas(W, H, PAPER)
    # ---- masthead
    cv.rect(0, 0, W, 96, NAVY)
    cv.rect(0, 96, W, 4, GOLD)
    # small globe mark left of title
    gx, gy = 56, 48
    cv.circle(gx, gy, 30, GOLD)
    cv.circle(gx, gy, 30, GOLD)
    cv.vline(gx, gy - 30, 61, GOLD)
    cv.hline(gx - 30, gy, 61, GOLD)
    cv.circle(gx, gy, 14, GOLD)
    cv.text_center(W // 2 + 20, 16, "THE WORLD", 6, WHITE)
    cv.text_center(W // 2 + 20, 62, "THURSDAY 26 NOVEMBER 2026", 2, GOLD)
    cv.text(W - 24 - text_width("TEN STORIES", 2), 62, "TEN STORIES", 2, WHITE)

    # ---- lead story
    lx, ly, lw, lh = 8, 108, 1008, 188
    cv.rect(lx, ly, lw, lh, WHITE)
    cv.rect(lx, ly, lw, 3, RED)
    cv.rect(lx, ly + lh - 3, lw, 3, INK)
    cv.rect(lx, ly, 3, lh, INK)
    cv.rect(lx + lw - 3, ly, 3, lh, INK)
    cv.rect(lx + 16, ly + 14, 132, 26, RED)
    cv.text(lx + 24, ly + 21, "LEAD STORY", 2, WHITE)
    cv.text(lx + 20, ly + 56, LEAD[1], 4, INK)
    cv.text(lx + 20, ly + 96, "TRADE WAR, ROUND TWO", 3, RED)
    cv.text(lx + 20, ly + 140, LEAD[2], 2, DARKGREY)
    pic_ship(cv, lx + 640, ly + 40, 340, 132)

    # ---- 3x3 grid
    cell_w, cell_h, gap = 320, 208, 8
    for i, (tag, tagc, head, sub, pic) in enumerate(STORIES):
        r, c = divmod(i, 3)
        x = 8 + c * (cell_w + gap)
        y = 304 + r * (cell_h + gap)
        draw_cell(cv, x, y, cell_w, cell_h, tag, tagc, head, sub, pic)

    # ---- footer
    cv.rect(0, 952, W, 4, GOLD)
    cv.text_center(W // 2, 968,
                   "26 NOVEMBER 2026 - THE DAY IN TEN STORIES", 2, INK)
    cv.text_center(W // 2, 994,
                   "SOURCES: REUTERS - AP - AFP - WSJ - AL JAZEERA",
                   1, DARKGREY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    data = png_bytes(draw())
    with open(path, "wb") as f:
        f.write(data)
    os.chmod(path, 0o644)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()

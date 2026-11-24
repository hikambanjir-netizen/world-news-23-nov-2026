#!/usr/bin/env python3
"""The World Today - 23 November 2026.

A one-page front-page summary of Monday 23 November 2026 world news,
drawn from scratch with the Python standard library only: a hand-built
5x7 bitmap font, a small canvas, and a from-scratch PNG encoder (zlib).
No network, no randomness, no clock reads: two runs write identical bytes.

Writes $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
Image: 1024x1024 PNG, well under the 1 MiB cap.
"""

import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (246, 241, 227)
INK = (22, 19, 14)
RED = (163, 30, 34)
BLUE = (30, 58, 95)
GREY = (107, 101, 88)
LIGHT = (232, 226, 208)


# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, '#' = ink. Uppercase only; input is upper-cased.
FONT = {
    "A": (" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "B": ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    "C": (" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"),
    "D": ("#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "),
    "E": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    "F": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    "G": (" ####", "#    ", "#    ", "# ###", "#   #", "#   #", " ### "),
    "H": ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "I": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"),
    "J": ("  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "),
    "K": ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    "L": ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    "M": ("#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"),
    "N": ("#   #", "##  #", "##  #", "# # #", "#  ##", "#  ##", "#   #"),
    "O": (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "P": ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    "Q": (" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"),
    "R": ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    "S": (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    "T": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "U": ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "V": ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "W": ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    "X": ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    "Y": ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "Z": ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    "0": (" ### ", "#  ##", "# # #", "##  #", "#   #", "#   #", " ### "),
    "1": ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "2": (" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"),
    "3": ("#### ", "    #", "    #", " ### ", "    #", "    #", "#### "),
    "4": ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    "5": ("#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "),
    "6": (" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "),
    "7": ("#####", "    #", "   # ", "   # ", "  #  ", "  #  ", "  #  "),
    "8": (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    "9": (" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "),
    " ": ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
    ".": ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    ",": ("     ", "     ", "     ", "     ", " ##  ", " ##  ", " #   "),
    ":": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "),
    ";": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", " #   "),
    "'": ("  #  ", "  #  ", "  #  ", "     ", "     ", "     ", "     "),
    "-": ("     ", "     ", "     ", "#####", "     ", "     ", "     "),
    "!": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    "?": (" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "),
    "(": ("   # ", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   # "),
    ")": (" #   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", " #   "),
    "/": ("    #", "    #", "   # ", "  #  ", " #   ", "#    ", "#    "),
    "&": (" ### ", "#   #", "#   #", " #   ", "# # #", "#  # ", " ## #"),
    "%": ("#  ##", "# # #", "   # ", "  #  ", " #   ", "# # #", "##  #"),
    "+": ("     ", "  #  ", "  #  ", "#####", "  #  ", "  #  ", "     "),
    "=": ("     ", "     ", "#####", "     ", "#####", "     ", "     "),
    '"': (" # # ", " # # ", " # # ", "     ", "     ", "     ", "     "),
    "*": ("     ", " # # ", "  #  ", "#####", "  #  ", " # # ", "     "),
}


def glyph(ch):
    if ch == "\u2014" or ch == "\u2013":
        return FONT["-"]
    if ch == "\u2019" or ch == "\u2018":
        return FONT["'"]
    if ch == "\u00b7":
        return ("     ", "     ", " ### ", " ### ", "     ", "     ", "     ")
    return FONT.get(ch.upper(), FONT[" "])


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray([bg[0]] * (w * h * 3))
        self.px[1::3] = bytearray([bg[1]] * (w * h))
        self.px[2::3] = bytearray([bg[2]] * (w * h))

    def fill(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                o = base + (xx - x0) * 3
                self.px[o], self.px[o + 1], self.px[o + 2] = c

    def hline(self, x, y, w, c, t=1):
        self.fill(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.fill(x, y, t, h, c)

    def box(self, x, y, w, h, c, t=1):
        self.hline(x, y, w, c, t)
        self.hline(x, y + h - t, w, c, t)
        self.vline(x, y, h, c, t)
        self.vline(x + w - t, y, h, c, t)

    def text(self, x, y, s, scale, c):
        cx = x
        for ch in s:
            g = glyph(ch)
            for row in range(7):
                line = g[row]
                for col in range(5):
                    if line[col] == "#":
                        self.fill(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def centre(self, y, s, scale, c):
        self.text((self.w - self.text_w(s, scale)) // 2, y, s, scale, c)

    def centre_in(self, x, w, y, s, scale, c):
        self.text(x + (w - self.text_w(s, scale)) // 2, y, s, scale, c)

    def wrap(self, s, scale, max_w):
        """Greedy word wrap; returns list of lines fitting max_w."""
        words, lines, cur = s.split(" "), [], ""
        for wd in words:
            trial = wd if not cur else cur + " " + wd
            if self.text_w(trial, scale) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, scale, c, max_w, leading=None):
        lh = leading if leading is not None else 10 * scale
        for i, line in enumerate(self.wrap(s, scale, max_w)):
            self.text(x, y + i * lh, line, scale, c)
        return y + len(self.wrap(s, scale, max_w)) * lh


# ---------------------------------------------------------------- png
def _chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def encode_png(cv):
    raw = bytearray()
    for yy in range(cv.h):
        raw.append(0)
        raw += cv.px[yy * cv.w * 3:(yy + 1) * cv.w * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    return png


# ---------------------------------------------------------------- page
def draw_masthead(cv):
    cv.hline(36, 34, W - 72, INK, 2)
    cv.centre(48, "ONE PAGE - THE WORLD'S NEWS", 2, GREY)
    cv.centre(72, "THE WORLD TODAY", 8, INK)
    cv.hline(36, 136, W - 72, INK, 3)
    cv.centre(148, "MONDAY 23 NOVEMBER 2026", 3, INK)
    cv.hline(36, 176, W - 72, INK, 1)


def draw_lead(cv):
    y = 196
    cv.centre(y, "CLIMATE - ANTALYA, TURKIYE", 2, RED)
    cv.centre(y + 24, "COP31 COLLAPSES", 8, INK)
    deck = ("Two weeks of talks end with no deal. The final text drops every "
            "mention of fossil fuels, and the EU and island states refuse to "
            "sign it - the longest climate summit ever, and the first to "
            "collapse since Copenhagen in 2009.")
    cv.para(88, y + 92, deck, 2, INK, W - 176, leading=18)
    # fact strip: three boxed facts
    fy = y + 180
    boxes = [("190+ NATIONS", "NO DEAL REACHED"),
             ("LONGEST COP", "EVER HELD"),
             ("FIRST COLLAPSE", "SINCE 2009")]
    bw = (W - 72 - 2 * 16) // 3
    for i, (a, b) in enumerate(boxes):
        bx = 36 + i * (bw + 16)
        cv.box(bx, fy, bw, 56, BLUE, 2)
        cv.centre_in(bx, bw, fy + 10, a, 2, BLUE)
        cv.centre_in(bx, bw, fy + 32, b, 2, INK)
    cv.hline(36, fy + 72, W - 72, INK, 2)
    return fy + 72


def draw_story(cv, x, y, w, kicker, headline, body, accent=RED):
    cv.text(x, y, kicker, 2, accent)
    y += 22
    y = cv.para(x, y, headline, 3, INK, w, leading=28)
    y += 4
    y = cv.para(x, y, body, 2, INK, w, leading=18)
    return y


def draw_middle(cv, top):
    y = top + 18
    col_w = 452
    lx, rx = 36, 536
    ly = draw_story(cv, lx, y, col_w,
                    "THE GULF WAR - RED SEA",
                    "HOUTHIS CLAIM STRIKES ON SAUDI REFINERY",
                    "The Houthis say they hit the Rabigh oil refinery and a "
                    "radar site near Riyadh. Saudi defences intercepted a "
                    "missile and drones; damage is unconfirmed.")
    ly = draw_story(cv, lx, ly + 16, col_w,
                    "UKRAINE - KYIV REGION",
                    "DRONE HITS FLAT BLOCK: 14 MISSING",
                    "A Russian drone strike collapses part of a five-storey "
                    "block in Dymer. Two dead, four hurt, and rescuers search "
                    "the rubble for 14 people.", accent=BLUE)
    ry = draw_story(cv, rx, y, col_w,
                    "INDONESIA - WEST JAVA",
                    "FACTORY FIRE: AT LEAST 3 DEAD, DOZENS MISSING",
                    "Fire tears through a candy factory. Rescuers have found "
                    "bodies in the ruins, and dozens of workers are still "
                    "unaccounted for.")
    ry = draw_story(cv, rx, ry + 16, col_w,
                    "SOUTH KOREA - SEOUL",
                    "MINISTER QUITS OVER AI EXAM CHEATING",
                    "The education minister resigns after an AI-driven "
                    "cheating scandal in the national exams.", accent=BLUE)
    cv.vline(512, y, max(ly, ry) - y, GREY, 1)
    return max(ly, ry)


def draw_sport(cv, top):
    y = top + 12
    cv.fill(36, y, W - 72, 40, BLUE)
    cv.text(52, y + 11, "SPORT", 2, PAPER)
    cv.text(150, y + 11,
            "ALCARAZ WINS FIRST ATP FINALS TITLE - BEATS ZVEREV", 2, PAPER)
    y += 52
    cv.text(36, y, "FIFA TO CONFIRM UK AS 2035 WOMEN'S WORLD CUP HOST", 2, INK)
    cv.text(36, y + 18, "INDIA POST RECORD 720/9 IN WELLINGTON TEST", 2, INK)
    cv.hline(36, y + 44, W - 72, INK, 2)
    return y + 44


def draw_ticker(cv, top):
    y = top + 12
    cv.text(36, y, "ALSO:", 2, RED)
    cv.para(110, y,
            "SEA DRONES HIT RUSSIAN WARSHIP AT BENGHAZI NAVAL BASE - "
            "NEPAL PM HOLDS TALKS IN DELHI - US SEEKS ANSWERS FROM "
            "NVIDIA OVER CHIP SALES TO CHINA",
            2, INK, W - 146, leading=18)
    y += 46
    cv.hline(36, y, W - 72, INK, 3)
    cv.centre(y + 12, "SOURCES: REUTERS - CNN - AP - ISW  -  23 NOVEMBER 2026",
              2, GREY)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    y = draw_lead(cv)
    y = draw_middle(cv, y)
    y = draw_sport(cv, y)
    draw_ticker(cv, y)
    png = encode_png(cv)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png)
    print("wrote %s (%d bytes)" % (path, len(png)))


if __name__ == "__main__":
    main()

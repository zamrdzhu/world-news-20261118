#!/usr/bin/env python3
"""Draw THE WORLD TODAY — a 1024x1024 newspaper front page summing up
Wednesday 18 November 2026, from stories.json. Pillow only, no network,
no clock: the same input always produces the same PNG bytes."""
import json

from PIL import Image, ImageDraw, ImageFont

SIZE = 1024
MARGIN = 34
CONTENT = SIZE - 2 * MARGIN          # 956

PAPER = (252, 251, 245)
INK = (18, 18, 18)
ACCENT = (158, 24, 24)
MUTED = (96, 92, 84)
RULE_LIGHT = (203, 199, 189)

NOTO = "/usr/share/fonts/truetype/noto/NotoSerif-Regular.ttf"
NOTO_B = "/usr/share/fonts/truetype/noto/NotoSerif-Bold.ttf"
NOTO_I = "/usr/share/fonts/truetype/noto/NotoSerif-Italic.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def load(path, size):
    return ImageFont.truetype(path, size)


def fit_lines(draw, text, face, width, limit=None):
    """Greedy wrap; if limit is set, cut the tail with an ellipsis."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = (current + " " + word).strip()
        if draw.textlength(trial, font=face) <= width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    if limit is not None and len(lines) > limit:
        lines = lines[:limit]
        tail = lines[-1]
        while tail and draw.textlength(tail + "…", font=face) > width:
            tail = tail[:-1].rstrip()
        lines[-1] = tail + "…"
    return lines


def put_lines(draw, lines, x, y, face, fill, step):
    for line in lines:
        draw.text((x, y), line, font=face, fill=fill)
        y += step
    return y


def centred(draw, text, y, face, fill):
    w = draw.textlength(text, font=face)
    draw.text(((SIZE - w) / 2, y), text, font=face, fill=fill)


def ring(draw, cx, cy, r, colour):
    """A small line-drawn globe: circle, meridian and two parallels."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=colour, width=2)
    draw.ellipse([cx - r * 0.42, cy - r, cx + r * 0.42, cy + r],
                 outline=colour, width=1)
    draw.line([cx - r, cy, cx + r, cy], fill=colour, width=1)
    draw.arc([cx - r, cy - r * 0.6, cx + r, cy + r * 0.6],
             start=195, end=345, fill=colour, width=1)


def main():
    with open("stories.json", encoding="utf-8") as fh:
        data = json.load(fh)

    page = Image.new("RGB", (SIZE, SIZE), PAPER)
    d = ImageDraw.Draw(page)

    # ---- Nameplate ------------------------------------------------------
    d.line([MARGIN, 28, SIZE - MARGIN, 28], fill=INK, width=4)
    d.line([MARGIN, 35, SIZE - MARGIN, 35], fill=INK, width=1)
    name_face = load(NOTO_B, 56)
    ring(d, MARGIN + 17, 72, 14, INK)
    ring(d, SIZE - MARGIN - 17, 72, 14, INK)
    centred(d, data["paper"], 42, name_face, INK)

    date_face = load(SANS_B, 27)
    centred(d, data["date"], 102, date_face, ACCENT)
    tag_face = load(NOTO_I, 20)
    centred(d, data["tagline"], 132, tag_face, INK)
    d.line([MARGIN, 158, SIZE - MARGIN, 158], fill=INK, width=3)

    # ---- Lead story -----------------------------------------------------
    lead = data["lead"]
    kick_face = load(SANS_B, 20)
    d.text((MARGIN, 170), lead["kicker"], font=kick_face, fill=ACCENT)
    head_face = load(NOTO_B, 43)
    head = fit_lines(d, lead["headline"], head_face, CONTENT, limit=2)
    y = put_lines(d, head, MARGIN, 196, head_face, INK, 48)
    deck_face = load(SANS, 21)
    deck = fit_lines(d, lead["deck"], deck_face, CONTENT, limit=2)
    y = put_lines(d, deck, MARGIN, y + 8, deck_face, INK, 26)
    d.line([MARGIN, y + 12, SIZE - MARGIN, y + 12], fill=INK, width=2)

    # ---- Story grid: three columns, four rows ---------------------------
    grid_top = y + 24
    row_h = 130
    gap = 18
    col_w = (CONTENT - 2 * gap) // 3
    col_x = [MARGIN, MARGIN + col_w + gap, MARGIN + 2 * (col_w + gap)]
    label_face = load(SANS_B, 20)
    grid_head_face = load(NOTO_B, 22)
    body_face = load(SANS, 20)
    for i, story in enumerate(data["stories"][:12]):
        row, col = divmod(i, 3)
        x = col_x[col]
        y = grid_top + row * row_h
        d.text((x, y), story["section"], font=label_face, fill=ACCENT)
        hl = fit_lines(d, story["headline"], grid_head_face, col_w, limit=2)
        y2 = put_lines(d, hl, x, y + 24, grid_head_face, INK, 25)
        body = fit_lines(d, story["body"], body_face, col_w, limit=2)
        put_lines(d, body, x, y2 + 4, body_face, INK, 22)
        if col < 2:
            d.line([x + col_w + gap // 2, y + 2, x + col_w + gap // 2,
                    y + row_h - 12], fill=RULE_LIGHT, width=1)
        if row < 3:
            d.line([x, y + row_h - 4, x + col_w, y + row_h - 4],
                   fill=RULE_LIGHT, width=1)
    grid_bottom = grid_top + 4 * row_h

    # ---- In brief --------------------------------------------------------
    d.line([MARGIN, grid_bottom + 6, SIZE - MARGIN, grid_bottom + 6],
           fill=INK, width=2)
    brief = data["stories"][12:15]
    brief_y = grid_bottom + 16
    brief_face = load(SANS, 20)
    for i, story in enumerate(brief):
        x = col_x[i]
        tag = story["section"] + " — "
        tag_w = d.textlength(tag, font=label_face)
        d.text((x, brief_y), tag, font=label_face, fill=ACCENT)
        lines = fit_lines(d, story["headline"], brief_face,
                          col_w - tag_w, limit=2)
        if lines:
            d.text((x + tag_w, brief_y), lines[0], font=brief_face, fill=INK)
            if len(lines) > 1:
                d.text((x, brief_y + 24), lines[1], font=brief_face, fill=INK)
    brief_bottom = brief_y + 48

    # ---- Footer ----------------------------------------------------------
    d.line([MARGIN, brief_bottom + 8, SIZE - MARGIN, brief_bottom + 8],
           fill=INK, width=1)
    foot_face = load(SANS, 20)
    centred(d, data["footer"], brief_bottom + 16, foot_face, MUTED)

    page.save("entry.png", optimize=True)
    print("saved entry.png", page.size)


if __name__ == "__main__":
    main()

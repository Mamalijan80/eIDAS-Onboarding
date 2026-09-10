# -*- coding: utf-8 -*-
"""Design tokens: the agents' spec, with the learning agent's must_change revisions applied."""
from reportlab.lib.units import mm

PAGE_W, PAGE_H = 210*mm, 297*mm
M_TOP, M_BOT, M_LEFT, M_RIGHT = 17*mm, 15*mm, 18*mm, 48*mm

LABEL_X0, LABEL_X1 = 18*mm, 40*mm          # labels right-aligned to 40mm
TEXT_X0, TEXT_X1   = 44*mm, 162*mm         # 118mm norm measure (~78 chars)
COL_W              = 57*mm                 # cross-reference columns
COL_X = (44*mm, 105*mm)
FLAG_X0, FLAG_X1   = 166*mm, 192*mm        # marginal flag column
EDGE_X0, EDGE_X1   = 199*mm, 210*mm        # priority edge zone
Y_TOP, Y_BOT       = 280*mm, 15*mm
GRID               = 13.2                  # baseline grid, pt

# --- fonts: spec roles mapped onto the real families available ---
# Helvetica role -> Work Sans | Times role -> IBM Plex Serif | Courier role -> IBM Plex Mono
F_UI, F_UIB, F_UII = "UI", "UI-Bold", "UI-It"
F_SERIF, F_SERIFI  = "Body", "Body-It"
F_MONO, F_MONOB    = "Mono", "Mono-Bold"
F_MARK             = "Marks"

INK      = "#14181F"
INK_SOFT = "#3A4049"
GREY     = "#6E6E6E"    # was #9AA1AB - must_change 9: 2.6:1 -> 5.0:1
HAIRLINE = "#C8CCD2"
BLUE     = "#1F4E9C"

# modality: colour + silhouette, only inside the header band
MODALITY = {
 "SHALL":                 dict(c="#1F4E9C", shape="rect",     fill=1),
 "SHALL NOT":             dict(c="#8C1D18", shape="rect",     fill=1, keyline=1, slab=1, spine=2.5),
 "MAY":                   dict(c="#00707A", shape="rect",     fill=0, dash=1),
 "DEFINITION":            dict(c="#6E6E6E", shape="half",     fill=1),
 "COMMISSION MANDATE":    dict(c="#8A5300", shape="chev_r",   fill=1),   # must_change 10: 4.2:1 -> 6.3:1
 "REFERENCING PROVISION": dict(c="#5B3E96", shape="chev_l",   fill=0),
 "LEGAL EFFECT":          dict(c="#14181F", shape="round",    fill=1),
}
# priority: achromatic + position, only in the page-edge zone
PRIORITY = {
 "L1": dict(y0=220*mm, y1=280*mm, c="#14181F", fill=1.0,  glyph="filled"),
 "L2": dict(y0=127.5*mm, y1=167.5*mm, c="#9AA1AB", fill=0.5, glyph="half"),
 "L3": dict(y0=15*mm, y1=35*mm, c="#14181F", fill=0.0, glyph="open"),
}
# must_change 3: red now means prohibition ONLY. Deadline is marked typographically, not by hue.
DEADLINE_C = INK

T = {  # (font, size, leading, colour)
 "runhead":   (F_UI,    7,    9,    GREY),
 "folio":     (F_UIB,   9,    11,   INK),
 "blockid":   (F_MONOB, 8,    10,   INK),
 "label":     (F_UIB,   6.8,  GRID, GREY),
 "topic":     (F_UIB,   11.5, 14,   INK),
 "addressee": (F_UII,   9,    GRID, INK_SOFT),
 "content":   (F_UI,    9.3,  GRID, INK),
 "purpose":   (F_SERIFI,9.8,  GRID, INK),
 "deadline":  (F_MONOB, 8.6,  GRID, DEADLINE_C),
 "xtitle":    (F_UIB,   7.6,  9.6,  BLUE),
 "xgloss":    (F_UI,    7.4,  9.6,  INK_SOFT),
 "xquote":    (F_SERIF, 8.3,  10.4, INK),   # must_change 8: 7.4 -> 8.3, real serif x-height
 "xrel":      (F_UIB,   7.4,  9.6,  INK_SOFT),
 "audit":     (F_UIB,   9.6,  GRID, INK),
 "keypoint":  (F_UIB,   10.5, 13.8, INK),
 "partno":    (F_UIB,   64,   64,   BLUE),
 "parttitle": (F_UIB,   20,   24,   INK),
 "objective": (F_UI,    10.5, 15,   INK),
}
PROOF_MARKS = False   # must_change 7: editorial flags are proof-only

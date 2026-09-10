# -*- coding: utf-8 -*-
"""Design tokens - dense revision. Blocks flow continuously; page budget 200 for the full manual."""
from reportlab.lib.units import mm

PAGE_W, PAGE_H = 210*mm, 297*mm
M_TOP, M_BOT = 14*mm, 13*mm

LABEL_X0, LABEL_X1 = 15*mm, 33*mm      # labels right-aligned to 33mm
TEXT_X0,  TEXT_X1  = 36*mm, 188*mm     # 152mm measure (was 118mm)
COL_W              = 74*mm             # two reference columns
COL_X              = (36*mm, 114*mm)
EDGE_X0, EDGE_X1   = 197*mm, 203*mm    # priority zone at the trimmed edge
Y_TOP, Y_BOT       = PAGE_H-M_TOP-6*mm, M_BOT+4*mm
GRID               = 11.0

F_UI, F_UIB, F_UII = "UI", "UI-Bold", "UI-It"
F_SERIF, F_SERIFI  = "Body", "Body-It"
F_MONO, F_MONOB    = "Mono", "Mono-Bold"
F_MARK             = "Marks"

INK      = "#14181F"
INK_SOFT = "#3A4049"
GREY     = "#6E6E6E"
HAIRLINE = "#C8CCD2"
BLUE     = "#1F4E9C"

MODALITY = {
 "SHALL":                 dict(c="#1F4E9C", shape="rect",   fill=1),
 "SHALL NOT":             dict(c="#8C1D18", shape="rect",   fill=1, keyline=1, spine=1.8),
 "MAY":                   dict(c="#00707A", shape="rect",   fill=0, dash=1),
 "DEFINITION":            dict(c="#6E6E6E", shape="half",   fill=1),
 "COMMISSION MANDATE":    dict(c="#8A5300", shape="chev_r", fill=1),
 "REFERENCING PROVISION": dict(c="#5B3E96", shape="chev_l", fill=0),
 "LEGAL EFFECT":          dict(c="#14181F", shape="round",  fill=1),
}
# priority: achromatic, positional - three non-overlapping bands at the fore-edge
PRIORITY = {
 "L1": dict(y0=200*mm, y1=270*mm, glyph="filled"),
 "L2": dict(y0=115*mm, y1=185*mm, glyph="half"),
 "L3": dict(y0= 30*mm, y1=100*mm, glyph="open"),
}
DEADLINE_C = INK

T = {
 "runhead":   (F_UI,    6.6,  8.5,  GREY),
 "folio":     (F_UIB,   8,    10,   INK),
 "blockid":   (F_MONOB, 7,    9,    INK),
 "label":     (F_UIB,   6.0,  GRID, GREY),
 "topic":     (F_UIB,   9.8,  11.6, INK),
 "addressee": (F_UII,   8.0,  GRID, INK_SOFT),
 "content":   (F_UI,    8.4,  GRID, INK),
 "purpose":   (F_SERIFI,8.8,  GRID, INK),
 "deadline":  (F_MONOB, 7.6,  GRID, DEADLINE_C),
 "xtitle":    (F_UIB,   6.9,  8.6,  BLUE),
 "xgloss":    (F_UI,    6.8,  8.6,  INK_SOFT),
 "xquote":    (F_SERIF, 7.6,  9.4,  INK),
 "xrel":      (F_UIB,   6.8,  8.6,  INK_SOFT),
 "audit":     (F_UIB,   8.6,  GRID, INK),
 "keypoint":  (F_UIB,   9.0,  11.4, INK),
 "partno":    (F_UIB,   52,   52,   BLUE),
 "parttitle": (F_UIB,   17,   21,   INK),
 "objective": (F_UI,    9.2,  13,   INK),
}
LABELS = {"TOPIC":"TOPIC","ADDRESSEE":"ADDRESSEE","CONTENT":"CONTENT","PURPOSE":"PURPOSE",
          "DEADLINE":"DEADLINE","CROSS-REFERENCES":"REFERENCES","AUDIT CHECK":"AUDIT CHECK",
          "KEY POINT":"KEY POINT"}
PROOF_MARKS = False

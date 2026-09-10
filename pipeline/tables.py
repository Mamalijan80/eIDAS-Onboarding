# -*- coding: utf-8 -*-
"""Flowing table renderer: column widths in mm, header repeated on every page, rows never split."""
from reportlab.lib.units import mm
import design as D, richtext as R

def _cell_lines(text, w, style):
    f,s,l,col = D.T[style]
    return R.wrap_runs([(str(text or ""), f, s, col)], w), l

def row_height(cells, widths, styles, pad=1.6*mm):
    h=0
    for txt,w,st in zip(cells,widths,styles):
        ln,l=_cell_lines(txt,w,st)
        h=max(h, len(ln)*l)
    return h+pad

def draw_row(c, cells, widths, styles, x0, y, pad=1.6*mm, rule=True):
    x=x0; low=y
    for txt,w,st in zip(cells,widths,styles):
        ln,l=_cell_lines(txt,w,st)
        yy=R.draw_lines(c, ln, x, y, l)
        low=min(low,yy); x+=w
    if rule:
        c.setStrokeColor(D.HAIRLINE); c.setLineWidth(0.35)
        c.line(x0, low+l*0.35, x0+sum(widths), low+l*0.35)
    return low-pad

def draw_header(c, heads, widths, x0, y):
    f,s,l,col = D.T["label"]
    c.setFont(f,s); c.setFillColor(col)
    x=x0
    for h,w in zip(heads,widths):
        c.drawString(x, y, str(h).upper()); x+=w
    c.setStrokeColor(D.INK); c.setLineWidth(0.6)
    c.line(x0, y-2.2*mm, x0+sum(widths), y-2.2*mm)
    return y-2.2*mm-l*0.55

def flow_table(doc, heads, rows, widths, styles, label=None):
    """Render a table, repeating the header after every page break."""
    x0=D.TEXT_X0
    if label:
        f,s,l,col=D.T["topic"]; doc.c.setFont(f,s); doc.c.setFillColor(col)
        doc.need(18*mm); doc.c.drawString(x0, doc.y, label); doc.y-=l+1.5*mm
    doc.need(24*mm)
    y=draw_header(doc.c, heads, widths, x0, doc.y)
    for cells in rows:
        h=row_height(cells, widths, styles)
        if y-h < D.Y_BOT:
            doc.y=y; doc.new_page()
            y=draw_header(doc.c, heads, widths, x0, doc.y)
        y=draw_row(doc.c, cells, widths, styles, x0, y)
    doc.y=y-2*mm
    return doc.y

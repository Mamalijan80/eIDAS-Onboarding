# -*- coding: utf-8 -*-
"""Run-based text wrapping so small caps and marks can be styled inline."""
import re
from reportlab.pdfbase.pdfmetrics import stringWidth

ACRONYMS = {"EU","EUDI","MS","QTSP","CAB","ARF","DVO","GDPR","DMA","DSA","NIS2","EAA","QEAA",
            "PUB-EAA","LOA","EUCC","ID","IT","PKI","API","URL","QES","CA","TL","EIDAS","OJ","L1","L2","L3"}

def smallcaps_runs(text, font, fontb, size, colour, cap_ratio=0.82):
    """must_change 6: simulated small caps per WORD, not per token."""
    runs=[]
    for tok in re.split(r'(\s+)', text):
        if not tok: continue
        if tok.isspace(): runs.append((tok, font, size, colour)); continue
        core=tok.strip('.,;:()[]"“”')
        if len(core)>1 and core.isupper() and core not in ACRONYMS and any(c.isalpha() for c in core):
            for w in re.split(r'([^A-Za-zÄÖÜ])', tok):
                if not w: continue
                if w.isalpha() and w.isupper() and len(w)>1:
                    runs.append((w[0], fontb, size, colour))
                    runs.append((w[1:], fontb, size*cap_ratio, colour))
                else:
                    runs.append((w, fontb, size, colour))
        else:
            runs.append((tok, font, size, colour))
    return runs

def wrap_runs(runs, width):
    """Greedy wrap a list of (text, font, size, colour) into lines."""
    lines=[]; cur=[]; w=0.0
    for text, font, size, colour in runs:
        for piece in re.split(r'(\s+)', text):
            if not piece: continue
            pw=stringWidth(piece, font, size)
            if piece.isspace():
                if cur: cur.append((piece,font,size,colour)); w+=pw
                continue
            if w+pw>width and cur:
                while cur and cur[-1][0].isspace(): cur.pop()
                lines.append(cur); cur=[]; w=0.0
            if pw>width:                      # unbreakable token longer than the measure
                acc=""
                for ch in piece:
                    if stringWidth(acc+ch, font, size)>width and acc:
                        lines.append([(acc,font,size,colour)]); acc=""
                    acc+=ch
                if acc: cur.append((acc,font,size,colour)); w=stringWidth(acc,font,size)
                continue
            cur.append((piece,font,size,colour)); w+=pw
    if cur:
        while cur and cur[-1][0].isspace(): cur.pop()
        lines.append(cur)
    return lines

def draw_lines(c, lines, x, y, leading):
    for ln in lines:
        cx=x
        for text,font,size,colour in ln:
            c.setFont(font,size); c.setFillColor(colour)
            c.drawString(cx,y,text); cx+=stringWidth(text,font,size)
        y-=leading
    return y

def measure(lines, leading):
    return len(lines)*leading

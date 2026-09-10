# -*- coding: utf-8 -*-
import json, glob, re, sys
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
import fonts, design as D, richtext as R
from xref import parse as parse_xref, split_title

fonts.register()
T=D.T

def txt(key): return T[key]

def field_label(c, y, label):
    f,s,l,col = txt("label")
    c.setFont(f,s); c.setFillColor(col)
    c.drawRightString(D.LABEL_X1, y, label.upper())

def para(c, y, key, text, x0=None, x1=None, smallcaps=False):
    if not text: return y
    f,s,l,col = txt(key)
    x0 = D.TEXT_X0 if x0 is None else x0
    x1 = D.TEXT_X1 if x1 is None else x1
    runs = R.smallcaps_runs(text, f, f if "Bold" in f else f.replace("UI","UI-Bold"), s, col) if smallcaps \
           else [(text, f, s, col)]
    lines = R.wrap_runs(runs, x1-x0)
    return R.draw_lines(c, lines, x0, y, l)

# ---------- chrome ----------
def badge(c, x, y, modality):
    m = D.MODALITY.get(modality)
    if not m: return
    h, w = 8*mm, 34*mm
    c.saveState()
    c.setStrokeColor(m["c"]); c.setFillColor(m["c"]); c.setLineWidth(0.9)
    sh=m["shape"]
    if sh=="rect":
        if m.get("dash"): c.setDash(2,1.6)
        c.rect(x,y,w,h, stroke=1, fill=m["fill"])
        if m.get("keyline"):
            c.setDash(); c.setStrokeColor("#000000"); c.setLineWidth(1.6); c.rect(x,y,w,h,stroke=1,fill=0)
    elif sh=="half":
        c.rect(x,y,w,h,stroke=1,fill=0); c.rect(x,y,2.5*mm,h,stroke=0,fill=1)
    elif sh in ("chev_r","chev_l"):
        n=3.2*mm; p=c.beginPath()
        if sh=="chev_r":
            p.moveTo(x,y); p.lineTo(x+w-n,y); p.lineTo(x+w,y+h/2); p.lineTo(x+w-n,y+h); p.lineTo(x,y+h)
        else:
            p.moveTo(x+w,y); p.lineTo(x+n,y); p.lineTo(x,y+h/2); p.lineTo(x+n,y+h); p.lineTo(x+w,y+h)
        p.close(); c.drawPath(p, stroke=1, fill=m["fill"])
    elif sh=="round":
        c.roundRect(x,y,w,h,2*mm,stroke=1,fill=1)
    lab=modality
    c.setFont("UI-Bold", 6.6)
    c.setFillColor("#FFFFFF" if m["fill"] and sh!="half" else m["c"])
    if sh=="half": c.setFillColor(m["c"])
    tw=stringWidth(lab,"UI-Bold",6.6)
    if tw>w-4*mm:
        c.setFont("UI-Bold",5.6); tw=stringWidth(lab,"UI-Bold",5.6)
    c.drawString(x+(w-tw)/2, y+h/2-2.3, lab)
    c.restoreState()

def priority_edge(c, level):
    p=D.PRIORITY.get(level)
    if not p: return
    c.saveState(); c.setStrokeColor(p["c"]); c.setFillColor(p["c"]); c.setLineWidth(0.7)
    x,w = D.EDGE_X0, D.EDGE_X1-D.EDGE_X0
    if p["fill"]>=1.0:   c.rect(x,p["y0"],w,p["y1"]-p["y0"],stroke=0,fill=1)
    elif p["fill"]>0:    c.setFillColor("#9AA1AB"); c.rect(x,p["y0"],w,p["y1"]-p["y0"],stroke=0,fill=1)
    else:                c.rect(x,p["y0"],w,p["y1"]-p["y0"],stroke=1,fill=0)
    c.restoreState()

def priority_glyph(c, x, y, level):
    p=D.PRIORITY.get(level)
    if not p: return
    s=3*mm
    c.saveState(); c.setStrokeColor(D.INK); c.setFillColor(D.INK); c.setLineWidth(0.7)
    if p["glyph"]=="filled": c.rect(x,y,s,s,stroke=0,fill=1)
    elif p["glyph"]=="half": c.rect(x,y,s,s,stroke=1,fill=0); c.rect(x,y,s/2,s,stroke=0,fill=1)
    else: c.rect(x,y,s,s,stroke=1,fill=0)
    c.setFont("UI-Bold",7); c.setFillColor(D.INK)
    c.drawString(x+s+1.5*mm, y+0.4*mm, level)
    c.restoreState()

def running_head(c, page, left, right):
    f,s,l,col=txt("runhead"); c.setFont(f,s); c.setFillColor(col)
    c.drawString(D.M_LEFT, D.PAGE_H-D.M_TOP+3*mm, left)
    c.drawRightString(D.EDGE_X1-4*mm, D.PAGE_H-D.M_TOP+3*mm, right)
    c.setStrokeColor(D.HAIRLINE); c.setLineWidth(0.4)
    c.line(D.M_LEFT, D.PAGE_H-D.M_TOP+1.5*mm, D.EDGE_X1-4*mm, D.PAGE_H-D.M_TOP+1.5*mm)
    f,s,l,col=txt("folio"); c.setFont(f,s); c.setFillColor(col)
    c.drawRightString(D.EDGE_X1-4*mm, D.M_BOT-6*mm, str(page))

# ---------- the Normblock ----------
def _rec_lines(r):
    """Pre-measure one cross-reference record -> list of (kind, lines, leading)."""
    out=[]
    f,s_,l,col=txt("xtitle")
    title, gloss = split_title(r["body"])
    head = (r["cite"] or "—")
    runs=[(head,f,s_,col)]
    if title: runs += [("  ","UI",s_,col), (title,"UI-Bold",s_,D.INK)]
    out.append(("title", R.wrap_runs(runs, D.COL_W), l))
    if gloss:
        f,s_,l,col=txt("xgloss")
        out.append(("gloss", R.wrap_runs([(gloss,f,s_,col)], D.COL_W), l))
    if r["quote"]:
        f,s_,l,col=txt("xquote")
        out.append(("quote", R.wrap_runs([("\u201c"+r["quote"]+"\u201d",f,s_,col)], D.COL_W-3*mm), l))
        out.append(("mark", None, l))
    elif r["mark"]=="\u25cf":
        out.append(("dot", None, txt("xgloss")[2]))
    if r["relevance"]:
        f,s_,l,col=txt("xrel")
        out.append(("rel", R.wrap_runs([("Relevance here: ",f,s_,col),
                                        (r["relevance"],"UI",7.4,D.INK_SOFT)], D.COL_W), l))
    return out

def _rec_height(parts):
    h=0.0
    for kind,lines,l in parts:
        h += (len(lines)*l if lines else l) + (1.2 if kind=="gloss" else 0)
    return h + 2.2*mm

def _draw_rec(c, r, parts, x, cy):
    for kind,lines,l in parts:
        if kind=="title":  cy=R.draw_lines(c,lines,x,cy,l)
        elif kind=="gloss": cy=R.draw_lines(c,lines,x,cy-1.2,l)
        elif kind=="quote":
            qh=len(lines)*l
            c.saveState(); c.setStrokeColor(D.BLUE); c.setLineWidth(1.2)
            c.line(x+0.6*mm, cy-1.5, x+0.6*mm, cy-qh-1.0); c.restoreState()
            cy=R.draw_lines(c,lines,x+3*mm,cy-2.0,l)
        elif kind=="mark":
            mk=r["mark"] or "\u2713"
            c.setFont("Marks",7.6); c.setFillColor(D.BLUE if mk=="\u2713" else D.GREY)
            c.drawString(x+3*mm, cy-0.5, mk)
            c.setFont("UI",6.6); c.setFillColor(D.GREY)
            c.drawString(x+3*mm+8, cy-0.5, (r["qcite"] or "").strip()); cy-=l
        elif kind=="dot":
            c.setFont("Marks",7.0); c.setFillColor(D.GREY); c.drawString(x,cy-0.5,"\u25cf")
            c.setFont("UI",6.6); c.drawString(x+8,cy-0.5,"summary, not verified against the original"); cy-=l
        elif kind=="rel":  cy=R.draw_lines(c,lines,x,cy-1.0,l)
    return cy-2.2*mm

def draw_xref(c, y, recs, y_floor):
    """Fill two 57mm columns down to y_floor; return (lowest_y, records_not_yet_drawn)."""
    avail=y-y_floor
    packs=[(r,_rec_lines(r)) for r in recs]
    heights=[_rec_height(p) for _,p in packs]
    col=[[],[]]; used=[0.0,0.0]; left=[]
    for (r,p),h in zip(packs,heights):
        placed=False
        for ci in (0,1):
            if used[ci]+h<=avail:
                col[ci].append((r,p)); used[ci]+=h; placed=True; break
        if not placed: left.append(r)
    lowest=y
    for ci in (0,1):
        cy=y; x=D.COL_X[ci]
        for r,p in col[ci]: cy=_draw_rec(c,r,p,x,cy)
        lowest=min(lowest,cy)
    return lowest, left

def _block_chrome(c, b, page, part_label, cont=False):
    art=b.get("article",""); mod=(b.get("modality_en") or "").upper(); lvl=b.get("level","")
    running_head(c, page, part_label, f"Article {art}" + (" (continued)" if cont else ""))
    priority_edge(c, lvl)
    y=D.Y_TOP
    m=D.MODALITY.get(mod,{})
    if not cont:
        badge(c, D.TEXT_X0, y-8*mm, mod)
        f,s_,l,col=txt("blockid"); c.setFont(f,s_); c.setFillColor(col)
        c.drawString(D.LABEL_X0, y-5.6*mm, b["id"].replace("|"," · "))
        priority_glyph(c, D.TEXT_X1-16*mm, y-8*mm+2.4*mm, lvl)
        if m.get("slab"):
            c.setFillColor(m["c"]); c.rect(D.TEXT_X0, y-9.6*mm, D.TEXT_X1-D.TEXT_X0, 3, stroke=0, fill=1)
    else:
        f,s_,l,col=txt("blockid"); c.setFont(f,s_); c.setFillColor(D.GREY)
        c.drawString(D.LABEL_X0, y-5.6*mm, b["id"].replace("|"," · ")+"  (cross-references, continued)")
    c.setStrokeColor(m.get("c", D.HAIRLINE) if m.get("spine") else D.HAIRLINE)
    c.setLineWidth(m.get("spine",0.5)); c.line(D.LABEL_X0-2*mm, D.Y_BOT, D.LABEL_X0-2*mm, y)
    return y-12*mm

def draw_block(c, b, page, part_label):
    """Renders one Normblock; overflows cross-references onto continuation pages. Returns pages used."""
    F=b["fields"]
    y=_block_chrome(c,b,page,part_label)
    if F.get("TOPIC"):     field_label(c,y,"Topic");     y=para(c,y,"topic",F["TOPIC"]); y-=2.0*mm
    if F.get("ADDRESSEE"): field_label(c,y,"Addressee"); y=para(c,y,"addressee",F["ADDRESSEE"]); y-=1.6*mm
    if F.get("CONTENT"):   field_label(c,y,"Content");   y=para(c,y,"content",F["CONTENT"],smallcaps=True); y-=1.6*mm
    if F.get("PURPOSE"):   field_label(c,y,"Purpose");   y=para(c,y,"purpose",F["PURPOSE"]); y-=1.6*mm
    if F.get("DEADLINE"):
        field_label(c,y,"Deadline")
        c.setStrokeColor(D.INK); c.setLineWidth(0.8); c.line(D.TEXT_X0, y+9.0, D.TEXT_X0+16*mm, y+9.0)
        y=para(c,y,"deadline",F["DEADLINE"]); y-=1.6*mm
    tail_h=34*mm            # reserved for AUDIT CHECK + KEY POINT (must_change 5)
    left=[]
    if F.get("CROSS-REFERENCES"):
        field_label(c,y,"Cross-references")
        left=parse_xref(F["CROSS-REFERENCES"])
        y,left=draw_xref(c,y,left, D.Y_BOT+tail_h)
        y-=1.0*mm
    y=min(y, D.Y_BOT+tail_h)
    c.setStrokeColor(D.HAIRLINE); c.setLineWidth(0.4); c.line(D.TEXT_X0, y+4*mm, D.TEXT_X1, y+4*mm)
    if F.get("AUDIT CHECK"):
        field_label(c,y,"Audit check"); y=para(c,y,"audit",F["AUDIT CHECK"]); y-=2.0*mm
    if F.get("KEY POINT"):
        f,s_,l,col=txt("keypoint")
        lines=R.wrap_runs([(F["KEY POINT"],f,s_,col)], D.TEXT_X1-D.TEXT_X0-6*mm)
        h=len(lines)*l+5*mm
        c.setFillColor("#F2F4F7"); c.setStrokeColor(D.HAIRLINE); c.setLineWidth(0.5)
        c.rect(D.TEXT_X0, y-h+l, D.TEXT_X1-D.TEXT_X0, h, stroke=1, fill=1)
        field_label(c,y,"Key point"); R.draw_lines(c, lines, D.TEXT_X0+3*mm, y, l)
    c.showPage(); used=1
    while left:                      # continuation pages - never drop a reference
        y=_block_chrome(c,b,page+used,part_label,cont=True)
        field_label(c,y,"Cross-references")
        y,left2=draw_xref(c,y,left, D.Y_BOT)
        if len(left2)==len(left): break     # no progress guard
        left=left2; c.showPage(); used+=1
    return used

# ---------- front matter ----------
def title_page(c):
    c.setFillColor(D.BLUE); c.rect(0, D.PAGE_H-92*mm, D.PAGE_W, 92*mm, stroke=0, fill=1)
    c.setFillColor("#FFFFFF"); c.setFont("UI-Bold", 34)
    c.drawString(D.M_LEFT, D.PAGE_H-46*mm, "eIDAS")
    c.setFont("UI", 15)
    c.drawString(D.M_LEFT, D.PAGE_H-58*mm, "Electronic Identification and Trust Services")
    c.setFont("UI", 9.5); c.setFillColor("#C8D6EE")
    c.drawString(D.M_LEFT, D.PAGE_H-72*mm, "STUDY AND AUDIT MANUAL  ·  ENGLISH EDITION  ·  PILOT (Articles 5a–5f)")
    y=D.PAGE_H-112*mm
    f,s,l,col=txt("objective"); c.setFont(f,s); c.setFillColor(D.INK)
    for ln in ["Regulation (EU) No 910/2014, consolidated version of 18 October 2024",
               "eIDAS and eIDAS 2.0 — Chapter II, Articles 5a to 5f"]:
        c.drawString(D.M_LEFT, y, ln); y-=6.5*mm
    y-=6*mm
    c.setStrokeColor(D.HAIRLINE); c.setLineWidth(0.5); c.line(D.M_LEFT,y,D.TEXT_X1,y); y-=8*mm
    c.setFont("UI-Bold",8.4); c.setFillColor(D.GREY)
    c.drawString(D.M_LEFT,y,"SOURCE AND VERIFICATION"); y-=6*mm
    c.setFont("UI",8.6); c.setFillColor(D.INK_SOFT)
    for ln in ["Translated from the German study manual (231 pp.) against the official English text of the",
               "consolidated Regulation. Defined terms follow the 57 definitions of Article 3 verbatim.",
               "All 27 passages marked ✓ were checked character-for-character against the official English",
               "wording and are reproduced exactly; they are not translations made for this edition.",
               "",
               "This document has no legal effect. Only the text published in the Official Journal of the",
               "European Union is authentic."]:
        c.drawString(D.M_LEFT,y,ln); y-=5.2*mm
    c.showPage()

def legend_page(c, page):
    running_head(c, page, "eIDAS · English edition", "How to read this manual")
    y=D.Y_TOP-6*mm
    c.setFont("UI-Bold",18); c.setFillColor(D.INK); c.drawString(D.M_LEFT,y,"How to read a norm block"); y-=12*mm
    c.setFont("UI",9.2); c.setFillColor(D.INK_SOFT)
    for ln in ["Every provision is set as one block with the same fields in the same order, so the eye learns",
               "where to look. Modality is colour and shape; priority is position at the page edge. They",
               "never share a channel, so neither can be mistaken for the other."]:
        c.drawString(D.M_LEFT,y,ln); y-=5.4*mm
    y-=6*mm
    c.setFont("UI-Bold",8.4); c.setFillColor(D.GREY); c.drawString(D.M_LEFT,y,"MODALITY — WHAT KIND OF NORM"); y-=10*mm
    desc={"SHALL":"Unconditional duty.","SHALL NOT":"Prohibition. Marked on three channels — the heaviest ink on the page.",
          "MAY":"Discretion or a right. Creates no duty unless exercised.",
          "DEFINITION":"Defines a term. Imposes no duty — the most common source of error.",
          "COMMISSION MANDATE":"Empowerment to adopt an implementing or delegated act.",
          "REFERENCING PROVISION":"Applies other articles by reference.",
          "LEGAL EFFECT":"Non-discrimination rule or legal presumption; addressed to courts."}
    for k in ["SHALL","SHALL NOT","MAY","DEFINITION","COMMISSION MANDATE","REFERENCING PROVISION","LEGAL EFFECT"]:
        badge(c, D.M_LEFT, y-2*mm, k)
        c.setFont("UI",8.2); c.setFillColor(D.INK_SOFT)
        c.drawString(D.M_LEFT+38*mm, y+0.6*mm, desc[k]); y-=11*mm
    y-=2*mm
    c.setFont("UI-Bold",8.4); c.setFillColor(D.GREY); c.drawString(D.M_LEFT,y,"PRIORITY — HOW HARD IT IS TESTED"); y-=8*mm
    for k,t in [("L1","Core material. Actually asked in conformity assessments."),
                ("L2","Important for understanding the system."),
                ("L3","Procedural and peripheral provisions.")]:
        priority_glyph(c, D.M_LEFT, y-1*mm, k)
        c.setFont("UI",8.2); c.setFillColor(D.INK_SOFT); c.drawString(D.M_LEFT+38*mm, y, t); y-=7.5*mm
    c.setFont("UI",7.6); c.setFillColor(D.GREY)
    c.drawString(D.M_LEFT, y-1*mm, "The bar at the trimmed page edge sits at a different height for each level, so the closed book shows them.")
    y-=12*mm
    c.setFont("UI-Bold",8.4); c.setFillColor(D.GREY); c.drawString(D.M_LEFT,y,"MARKS ON A CROSS-REFERENCE"); y-=8*mm
    for mk,t in [("✓","The quoted wording was checked character-for-character against the official English text."),
                 ("●","A summary in this manual's own words; no wording was quoted."),
                 ("","No mark: the reference is named and explained, but nothing is quoted or asserted as wording.")]:
        if mk:
            c.setFont("Marks",9); c.setFillColor(D.BLUE if mk=="✓" else D.GREY); c.drawString(D.M_LEFT,y,mk)
        c.setFont("UI",8.2); c.setFillColor(D.INK_SOFT); c.drawString(D.M_LEFT+38*mm,y,t); y-=7*mm
    c.showPage()

def part_opener(c, page, letter, title, subtitle, objectives):
    running_head(c, page, "eIDAS · English edition", f"Part {letter}")
    f,s,l,col=txt("partno"); c.setFont(f,s); c.setFillColor(col)
    c.drawString(D.M_LEFT, D.Y_TOP-24*mm, letter)
    f,s,l,col=txt("parttitle"); c.setFont(f,s); c.setFillColor(col)
    c.drawString(D.M_LEFT, D.Y_TOP-40*mm, title)
    c.setFont("UI",10); c.setFillColor(D.GREY)
    c.drawString(D.M_LEFT, D.Y_TOP-48*mm, subtitle)
    y=D.Y_TOP-66*mm
    c.setFont("UI-Bold",8.4); c.setFillColor(D.GREY)
    c.drawString(D.M_LEFT,y,"AFTER THIS PART YOU SHOULD BE ABLE TO"); y-=9*mm
    f,s,l,col=txt("objective")
    for o in objectives:
        c.setFillColor(D.BLUE); c.setFont("UI-Bold",s); c.drawString(D.M_LEFT,y,"—")
        lines=R.wrap_runs([(o,f,s,D.INK)], D.TEXT_X1-D.M_LEFT-7*mm)
        y=R.draw_lines(c, lines, D.M_LEFT+7*mm, y, l)-2.5*mm
    y-=6*mm
    c.setStrokeColor(D.HAIRLINE); c.setLineWidth(0.5); c.line(D.M_LEFT,y,D.TEXT_X1,y); y-=8*mm
    c.setFont("UI-Bold",8.4); c.setFillColor(D.GREY); c.drawString(D.M_LEFT,y,"SPACED REPETITION"); y-=8*mm
    c.setFont("UI",8.4); c.setFillColor(D.INK_SOFT)
    for d,w in [("Day 0","Read the part; then recall the key points without the manual"),
                ("Day 1","Recall yesterday's key points — 15 min"),
                ("Day 3","Audit checks of the part, answers covered — 20 min"),
                ("Day 7","Only the items marked hard, plus the deadlines — 20 min"),
                ("Day 16","Mixed across all parts so far, deliberately out of order — 30 min"),
                ("Day 35","Refresh; look up what is still missing — 30 min")]:
        c.setFont("Mono-Bold",8.2); c.setFillColor(D.INK); c.drawString(D.M_LEFT,y,d)
        c.setFont("UI",8.4); c.setFillColor(D.INK_SOFT); c.drawString(D.M_LEFT+18*mm,y,w); y-=6*mm
    c.showPage()

OBJECTIVES = [
 "name the three routes by which a Member State may provide a European Digital Identity Wallet, "
 "and say who bears supervisory responsibility in each",
 "state which paragraphs of Article 5a are covered by certification under Article 5c — and which are not",
 "date the 24-month deadline in Article 5a(1) from the correct trigger, and name both implementing acts that start it",
 "distinguish what a relying party may request from what it must have registered beforehand",
 "explain why 'low' assurance creates no obligation to accept, while 'substantial' and 'high' do",
 "identify, for any provision in this Part, whether it binds a Member State, a wallet provider, "
 "a relying party or the Commission",
]

def main(out="eIDAS_Study_Manual_EN_pilot.pdf"):
    blocks=[b for f in sorted(glob.glob("pilot/out/*_en.json")) for b in json.load(open(f))]
    c=canvas.Canvas(out, pagesize=(D.PAGE_W, D.PAGE_H))
    c.setTitle("eIDAS — Study and Audit Manual, English Edition (Pilot)")
    c.setAuthor("eIDAS Study Manual"); c.setSubject("Regulation (EU) No 910/2014, consolidated 18 October 2024")
    title_page(c)
    page=2; legend_page(c,page); page+=1
    part_opener(c,page,"A","Electronic Identification",
                "Chapter II · Articles 5a to 5f · Wallet, relying parties, certification, acceptance",
                OBJECTIVES); page+=1
    overflow=0
    c.bookmarkPage("partA"); c.addOutlineEntry("Part A — Electronic Identification","partA",0)
    cur=None
    for b in blocks:
        art=b.get("article","")
        key=f"art{art}"
        if art!=cur:
            c.bookmarkPage(key); c.addOutlineEntry(f"Article {art}",key,1); cur=art
        page+=draw_block(c,b,page,"Part A · Electronic Identification")
    c.save()
    return out, page-1, len(blocks), 0

if __name__=="__main__":
    f,pages,n,ov=main()
    print(f"built {f}: {pages} pages, {n} blocks, {ov} cross-references beyond the 3-box cap")

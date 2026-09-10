# -*- coding: utf-8 -*-
"""Continuous-flow typesetter for the English eIDAS study manual."""
import json, glob, re, sys
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
import fonts, design as D, richtext as R
from xref import parse as parse_xref, split_title

fonts.register()
T = D.T

class Doc:
    def __init__(self, path):
        self.c = canvas.Canvas(path, pagesize=(D.PAGE_W, D.PAGE_H))
        self.page = 0; self.y = 0; self.head_l = ""; self.head_r = ""
        self.new_page()
    def new_page(self, head_l=None, head_r=None):
        if self.page: self.c.showPage()
        self.page += 1
        if head_l is not None: self.head_l = head_l
        if head_r is not None: self.head_r = head_r
        self.y = D.Y_TOP
        self._chrome()
    def _chrome(self):
        c = self.c
        f,s,l,col = T["runhead"]; c.setFont(f,s); c.setFillColor(col)
        c.drawString(D.LABEL_X0, D.PAGE_H-D.M_TOP, self.head_l)
        c.drawRightString(D.EDGE_X1-2*mm, D.PAGE_H-D.M_TOP, self.head_r)
        c.setStrokeColor(D.HAIRLINE); c.setLineWidth(0.4)
        c.line(D.LABEL_X0, D.PAGE_H-D.M_TOP-2.4*mm, D.EDGE_X1-2*mm, D.PAGE_H-D.M_TOP-2.4*mm)
        f,s,l,col = T["folio"]; c.setFont(f,s); c.setFillColor(col)
        c.drawRightString(D.EDGE_X1-2*mm, D.M_BOT-3*mm, str(self.page))
    def room(self): return self.y - D.Y_BOT
    def need(self, h):
        if h > self.room(): self.new_page()

def label(doc, y, key):
    f,s,l,col = T["label"]
    doc.c.setFont(f,s); doc.c.setFillColor(col)
    doc.c.drawRightString(D.LABEL_X1, y, D.LABELS.get(key,key))

def lines_for(key, text, width=None, smallcaps=False):
    f,s,l,col = T[key]
    w = (D.TEXT_X1-D.TEXT_X0) if width is None else width
    runs = R.smallcaps_runs(text, f, "UI-Bold", s, col) if smallcaps else [(text,f,s,col)]
    return R.wrap_runs(runs, w), l

# ---------- badges & priority ----------
def badge(c, x, y, modality, w=30*mm, h=6.2*mm):
    m = D.MODALITY.get(modality)
    if not m: return 0
    c.saveState(); c.setStrokeColor(m["c"]); c.setFillColor(m["c"]); c.setLineWidth(0.8)
    sh = m["shape"]
    if sh == "rect":
        if m.get("dash"): c.setDash(2,1.5)
        c.rect(x,y,w,h,stroke=1,fill=m["fill"])
        if m.get("keyline"):
            c.setDash(); c.setStrokeColor("#000000"); c.setLineWidth(1.3); c.rect(x,y,w,h,stroke=1,fill=0)
    elif sh == "half":
        c.rect(x,y,w,h,stroke=1,fill=0); c.rect(x,y,2*mm,h,stroke=0,fill=1)
    elif sh in ("chev_r","chev_l"):
        n=2.6*mm; p=c.beginPath()
        if sh=="chev_r": p.moveTo(x,y); p.lineTo(x+w-n,y); p.lineTo(x+w,y+h/2); p.lineTo(x+w-n,y+h); p.lineTo(x,y+h)
        else:            p.moveTo(x+w,y); p.lineTo(x+n,y); p.lineTo(x,y+h/2); p.lineTo(x+n,y+h); p.lineTo(x+w,y+h)
        p.close(); c.drawPath(p,stroke=1,fill=m["fill"])
    elif sh == "round":
        c.roundRect(x,y,w,h,1.6*mm,stroke=1,fill=1)
    size=5.6
    if stringWidth(modality,"UI-Bold",size) > w-4*mm: size=4.9
    c.setFont("UI-Bold",size)
    c.setFillColor("#FFFFFF" if (m["fill"] and sh!="half") else m["c"])
    c.drawString(x+(w-stringWidth(modality,"UI-Bold",size))/2, y+h/2-size*0.35, modality)
    c.restoreState(); return w

def priority_edge(c, level, y0, y1):
    """Bar in the fore-edge zone spanning this block's own extent."""
    p = D.PRIORITY.get(level)
    if not p or y1-y0 < 2*mm: return
    c.saveState(); x,w = D.EDGE_X0, D.EDGE_X1-D.EDGE_X0
    if p["glyph"]=="filled": c.setFillColor(D.INK); c.rect(x,y0,w,y1-y0,stroke=0,fill=1)
    elif p["glyph"]=="half": c.setFillColor("#9AA1AB"); c.rect(x,y0,w/2,y1-y0,stroke=0,fill=1)
    else:
        c.setStrokeColor(D.INK); c.setLineWidth(0.5); c.rect(x,y0,w,y1-y0,stroke=1,fill=0)
    c.restoreState()

def priority_glyph(c, x, y, level):
    p = D.PRIORITY.get(level)
    if not p: return
    s=2.6*mm
    c.saveState(); c.setStrokeColor(D.INK); c.setFillColor(D.INK); c.setLineWidth(0.6)
    if p["glyph"]=="filled": c.rect(x,y,s,s,stroke=0,fill=1)
    elif p["glyph"]=="half": c.rect(x,y,s,s,stroke=1,fill=0); c.rect(x,y,s/2,s,stroke=0,fill=1)
    else: c.rect(x,y,s,s,stroke=1,fill=0)
    c.setFont("UI-Bold",6.2); c.drawString(x+s+1.2*mm, y+0.3*mm, level)
    c.restoreState()

# ---------- cross-references ----------
def rec_parts(r):
    out=[]
    title, gloss = split_title(r["body"])
    f,s,l,col = T["xtitle"]
    runs=[(r["cite"] or "—", f, s, col)]
    if title: runs += [("  ",f,s,col), (title,"UI-Bold",s,D.INK)]
    out.append(("title", R.wrap_runs(runs, D.COL_W), l))
    if gloss:
        ln,l = lines_for("xgloss", gloss, D.COL_W); out.append(("gloss", ln, l))
    if r["quote"]:
        ln,l = lines_for("xquote", "“"+r["quote"]+"”", D.COL_W-2.5*mm)
        out.append(("quote", ln, l)); out.append(("mark", None, l))
    elif r["mark"]=="●":
        out.append(("dot", None, T["xgloss"][2]))
    if r["relevance"]:
        f,s,l,col = T["xrel"]
        ln = R.wrap_runs([("Relevance: ",f,s,col), (r["relevance"],"UI",s,D.INK_SOFT)], D.COL_W)
        out.append(("rel", ln, l))
    return out

def rec_h(parts): return sum((len(ln)*l if ln else l) for _,ln,l in parts) + 1.8*mm

def draw_rec(c, r, parts, x, cy):
    for kind, ln, l in parts:
        if kind=="title":   cy=R.draw_lines(c,ln,x,cy,l)
        elif kind=="gloss": cy=R.draw_lines(c,ln,x,cy,l)
        elif kind=="quote":
            qh=len(ln)*l
            c.saveState(); c.setStrokeColor(D.BLUE); c.setLineWidth(1.0)
            c.line(x+0.5*mm, cy-1.2, x+0.5*mm, cy-qh-0.6); c.restoreState()
            cy=R.draw_lines(c,ln,x+2.5*mm,cy-1.4,l)
        elif kind=="mark":
            mk=r["mark"] or "✓"
            c.setFont("Marks",6.8); c.setFillColor(D.BLUE if mk=="✓" else D.GREY)
            c.drawString(x+2.5*mm, cy-0.4, mk)
            c.setFont("UI",6.0); c.setFillColor(D.GREY)
            c.drawString(x+2.5*mm+7, cy-0.4, (r["qcite"] or "").strip()); cy-=l
        elif kind=="dot":
            c.setFont("Marks",6.4); c.setFillColor(D.GREY); c.drawString(x,cy-0.4,"●")
            c.setFont("UI",6.0); c.drawString(x+7,cy-0.4,"summary, not verified"); cy-=l
        elif kind=="rel": cy=R.draw_lines(c,ln,x,cy,l)
    return cy-1.8*mm

def flow_refs(doc, recs, first_y):
    """Two balanced columns. Nothing is drawn that does not fit; the remainder goes to the next page."""
    packs=[(r,rec_parts(r)) for r in recs]
    i=0; y_start=first_y; guard=0
    while i < len(packs):
        guard+=1
        if guard > 400: raise RuntimeError("flow_refs did not converge")
        avail = y_start - D.Y_BOT
        rest = packs[i:]
        total = sum(rec_h(p) for _,p in rest)
        if total <= avail*2:                       # everything left fits: balance the columns
            target=total/2.0; cut=0; acc=0.0
            for k,(r,p) in enumerate(rest):
                if acc>=target and k>0: break
                acc+=rec_h(p); cut=k+1
            chunks=[rest[:cut], rest[cut:]]
        else:                                      # fill column 0, then column 1, strictly by fit
            chunks=[[],[]]; used=[0.0,0.0]; k=0
            for ci in (0,1):
                while k < len(rest):
                    h=rec_h(rest[k][1])
                    if used[ci]+h > avail: break
                    chunks[ci].append(rest[k]); used[ci]+=h; k+=1
        drawn=len(chunks[0])+len(chunks[1])
        if drawn==0:
            # one record taller than a full column: give it the full measure on a fresh page
            r,p = rest[0]
            if y_start < D.Y_TOP - 1*mm:
                doc.new_page(); label(doc, doc.y, "CROSS-REFERENCES"); y_start=doc.y
            wide = rec_parts_wide(r)
            doc.y = draw_rec(doc.c, r, wide, D.COL_X[0], y_start)
            i+=1; y_start=doc.y
            if i < len(packs):
                doc.new_page(); label(doc, doc.y, "CROSS-REFERENCES"); y_start=doc.y
            continue
        if not chunks[1]:                      # single column would waste half the measure
            wide=[(r,rec_parts_wide(r)) for r,_ in chunks[0]]
            if sum(rec_h(p) for _,p in wide) <= avail:
                cy=[y_start,y_start]
                for r,p in wide: cy[0]=draw_rec(doc.c,r,p,D.COL_X[0],cy[0])
                i+=drawn
                if i < len(packs):
                    doc.new_page(); label(doc, doc.y, "CROSS-REFERENCES"); y_start=doc.y
                else: doc.y=cy[0]
                continue
        cy=[y_start,y_start]
        for ci in (0,1):
            x=D.COL_X[ci]
            for r,p in chunks[ci]: cy[ci]=draw_rec(doc.c,r,p,x,cy[ci])
        i+=drawn
        if i < len(packs):
            doc.new_page(); label(doc, doc.y, "CROSS-REFERENCES"); y_start=doc.y
        else:
            doc.y=min(cy)
    return doc.y

def rec_parts_wide(r):
    """Same record laid out across the full measure - used only when it exceeds one column."""
    W=D.TEXT_X1-D.TEXT_X0
    out=[]; title,gloss=split_title(r["body"])
    f,s,l,col=T["xtitle"]
    runs=[(r["cite"] or "—",f,s,col)]
    if title: runs+=[("  ",f,s,col),(title,"UI-Bold",s,D.INK)]
    out.append(("title", R.wrap_runs(runs,W), l))
    if gloss:
        ln,l=lines_for("xgloss",gloss,W); out.append(("gloss",ln,l))
    if r["quote"]:
        ln,l=lines_for("xquote","\u201c"+r["quote"]+"\u201d",W-2.5*mm)
        out.append(("quote",ln,l)); out.append(("mark",None,l))
    elif r["mark"]=="\u25cf":
        out.append(("dot",None,T["xgloss"][2]))
    if r["relevance"]:
        f,s,l,col=T["xrel"]
        out.append(("rel", R.wrap_runs([("Relevance: ",f,s,col),(r["relevance"],"UI",s,D.INK_SOFT)],W), l))
    return out

# ---------- one norm block ----------
def draw_block(doc, b, part_label):
    c=doc.c; F=b["fields"]
    mod=(b.get("modality_en") or "").upper(); lvl=b.get("level","")
    art=b.get("article",""); locus=b.get("locus_en") or b.get("locus","")
    lx=re.sub(r'^Paragraphs?\s+','',str(locus)).strip()
    lx=re.sub(r'\s*\(.*?\)\s*$','',lx).strip()
    ident=f"Art. {art}({lx})" if lx else f"Art. {art}"
    # head + the first two fields must not be orphaned
    head_h = 9.4*mm
    tl,_ = lines_for("topic", F.get("TOPIC",""))
    probe = head_h + len(tl)*T["topic"][2] + 6*mm
    doc.need(probe)
    if doc.head_r != f"Article {art}":
        doc.head_l = part_label; doc.head_r = f"Article {art}"
        doc._chrome() if doc.y==D.Y_TOP else None
    y=doc.y
    block_top=y
    badge(c, D.TEXT_X0, y-5.6*mm, mod)
    f,s,l,col=T["blockid"]; c.setFont(f,s); c.setFillColor(col)
    c.drawRightString(D.LABEL_X1, y-4.0*mm, ident)
    priority_glyph(c, D.TEXT_X0+33*mm, y-5.3*mm, lvl)
    m=D.MODALITY.get(mod,{})
    if m.get("spine"):
        c.setStrokeColor(m["c"]); c.setLineWidth(m["spine"])
        c.line(D.LABEL_X0-1.5*mm, D.Y_BOT, D.LABEL_X0-1.5*mm, y)
    y -= head_h
    for key, sc in (("TOPIC",False),("ADDRESSEE",False),("CONTENT",True),("PURPOSE",False),("DEADLINE",False)):
        if not F.get(key): continue
        ln,l = lines_for("topic" if key=="TOPIC" else key.lower().replace(" ","") if key!="ADDRESSEE" else "addressee",
                         F[key], smallcaps=sc) if False else lines_for(
                         {"TOPIC":"topic","ADDRESSEE":"addressee","CONTENT":"content",
                          "PURPOSE":"purpose","DEADLINE":"deadline"}[key], F[key], smallcaps=sc)
        if len(ln)*l > doc.y - D.Y_BOT and key!="TOPIC":
            doc.y=y; doc.new_page(); y=doc.y
        label(doc, y, key)
        y=R.draw_lines(c, ln, D.TEXT_X0, y, l) - 1.2*mm
        doc.y=y
    if F.get("CROSS-REFERENCES"):
        label(doc, y, "CROSS-REFERENCES")
        y=flow_refs(doc, parse_xref(F["CROSS-REFERENCES"]), y)
    tail=[]
    if F.get("AUDIT CHECK"):
        ln,l=lines_for("audit", F["AUDIT CHECK"]); tail.append(("AUDIT CHECK",ln,l))
    if F.get("KEY POINT"):
        ln,l=lines_for("keypoint", F["KEY POINT"], D.TEXT_X1-D.TEXT_X0-5*mm); tail.append(("KEY POINT",ln,l))
    th=sum(len(ln)*l for _,ln,l in tail)+7*mm
    if th > doc.y-D.Y_BOT: doc.new_page()
    y=doc.y-1.5*mm
    for key,ln,l in tail:
        label(doc,y,key)
        if key=="KEY POINT":
            h=len(ln)*l+3.4*mm
            c.setFillColor("#F2F4F7"); c.setStrokeColor(D.HAIRLINE); c.setLineWidth(0.4)
            c.rect(D.TEXT_X0, y-h+l, D.TEXT_X1-D.TEXT_X0, h, stroke=1, fill=1)
            R.draw_lines(c,ln,D.TEXT_X0+2.5*mm,y,l); y-=len(ln)*l+2.2*mm
        else:
            y=R.draw_lines(c,ln,D.TEXT_X0,y,l)-1.2*mm
    doc.y=y-3*mm
    priority_edge(c, lvl, max(doc.y, D.Y_BOT), block_top)
    c.setStrokeColor(D.HAIRLINE); c.setLineWidth(0.5)
    c.line(D.LABEL_X0, doc.y+1.4*mm, D.EDGE_X1-2*mm, doc.y+1.4*mm)
    doc.y-=2.5*mm

# ---------- front matter ----------
def title_page(doc):
    c=doc.c
    c.setFillColor(D.BLUE); c.rect(0, D.PAGE_H-78*mm, D.PAGE_W, 78*mm, stroke=0, fill=1)
    c.setFillColor("#FFFFFF"); c.setFont("UI-Bold",30)
    c.drawString(D.LABEL_X0, D.PAGE_H-40*mm, "eIDAS")
    c.setFont("UI",13); c.drawString(D.LABEL_X0, D.PAGE_H-50*mm, "Electronic Identification and Trust Services")
    c.setFont("UI",8.6); c.setFillColor("#C8D6EE")
    c.drawString(D.LABEL_X0, D.PAGE_H-62*mm, "STUDY AND AUDIT MANUAL · ENGLISH EDITION")
    y=D.PAGE_H-96*mm
    c.setFont("UI",9.2); c.setFillColor(D.INK)
    for ln in ["Regulation (EU) No 910/2014, consolidated version of 18 October 2024",
               "eIDAS and eIDAS 2.0"]:
        c.drawString(D.LABEL_X0,y,ln); y-=5.6*mm
    y-=5*mm; c.setStrokeColor(D.HAIRLINE); c.setLineWidth(0.5)
    c.line(D.LABEL_X0,y,D.TEXT_X1,y); y-=7*mm
    c.setFont("UI",8.2); c.setFillColor(D.INK_SOFT)
    for ln in ["Passages marked ✓ are reproduced verbatim from the official English text and were",
               "checked character-for-character; they are not translations made for this edition.",
               "Defined terms follow the 57 definitions of Article 3.",
               "",
               "This document has no legal effect. Only the text published in the Official Journal",
               "of the European Union is authentic."]:
        c.drawString(D.LABEL_X0,y,ln); y-=4.8*mm
    doc.y=D.Y_BOT

def legend_page(doc):
    doc.new_page("eIDAS · English edition", "How to read this manual")
    c=doc.c; y=doc.y-3*mm
    c.setFont("UI-Bold",15); c.setFillColor(D.INK); c.drawString(D.LABEL_X0,y,"How to read a norm block"); y-=9*mm
    c.setFont("UI",8.4); c.setFillColor(D.INK_SOFT)
    for ln in ["Every provision is one block with the same fields in the same order. Modality is colour and shape;",
               "priority is position at the page edge. The two codes never share a channel.",
               "'Wallet' is used throughout for the European Digital Identity Wallet, the term defined in Article 3(42);",
               "quoted wording always keeps the official full term."]:
        c.drawString(D.LABEL_X0,y,ln); y-=4.8*mm
    y-=4*mm
    c.setFont("UI-Bold",7.4); c.setFillColor(D.GREY); c.drawString(D.LABEL_X0,y,"MODALITY"); y-=7.5*mm
    desc={"SHALL":"Unconditional duty.","SHALL NOT":"Prohibition.","MAY":"Discretion or a right; no duty unless exercised.",
          "DEFINITION":"Defines a term; imposes no duty. The most common source of error.",
          "COMMISSION MANDATE":"Empowerment to adopt an implementing or delegated act.",
          "REFERENCING PROVISION":"Applies other articles by reference.",
          "LEGAL EFFECT":"Non-discrimination rule or legal presumption; addressed to courts."}
    for k in ["SHALL","SHALL NOT","MAY","DEFINITION","COMMISSION MANDATE","REFERENCING PROVISION","LEGAL EFFECT"]:
        badge(c, D.LABEL_X0, y-1.6*mm, k)
        c.setFont("UI",7.8); c.setFillColor(D.INK_SOFT); c.drawString(D.LABEL_X0+34*mm, y, desc[k]); y-=8.4*mm
    y-=2*mm
    c.setFont("UI-Bold",7.4); c.setFillColor(D.GREY); c.drawString(D.LABEL_X0,y,"PRIORITY"); y-=6.5*mm
    for k,t in [("L1","Core material; asked in conformity assessments."),
                ("L2","Important for understanding the system."),
                ("L3","Procedural and peripheral provisions.")]:
        priority_glyph(c, D.LABEL_X0, y-0.8*mm, k)
        c.setFont("UI",7.8); c.setFillColor(D.INK_SOFT); c.drawString(D.LABEL_X0+34*mm,y,t); y-=6.2*mm
    y-=3*mm
    c.setFont("UI-Bold",7.4); c.setFillColor(D.GREY); c.drawString(D.LABEL_X0,y,"MARKS ON A REFERENCE"); y-=6.5*mm
    for mk,t in [("✓","Wording checked character-for-character against the official English text."),
                 ("●","A summary in this manual's own words; nothing is quoted."),
                 ("","No mark: the reference is explained, but no wording is quoted or asserted.")]:
        if mk:
            c.setFont("Marks",8); c.setFillColor(D.BLUE if mk=="✓" else D.GREY); c.drawString(D.LABEL_X0,y,mk)
        c.setFont("UI",7.8); c.setFillColor(D.INK_SOFT); c.drawString(D.LABEL_X0+34*mm,y,t); y-=6.2*mm
    doc.y=y

def part_banner(doc, letter, title, subtitle):
    """Compact banner, not a full page - the objectives and repetition schedule were dropped."""
    doc.need(34*mm)
    c=doc.c; y=doc.y
    c.setFillColor(D.BLUE); c.rect(D.LABEL_X0, y-24*mm, D.EDGE_X1-2*mm-D.LABEL_X0, 24*mm, stroke=0, fill=1)
    c.setFillColor("#FFFFFF"); c.setFont("UI-Bold",30)
    c.drawString(D.LABEL_X0+4*mm, y-15*mm, letter)
    c.setFont("UI-Bold",15); c.drawString(D.LABEL_X0+20*mm, y-12*mm, title)
    c.setFont("UI",8); c.setFillColor("#C8D6EE")
    c.drawString(D.LABEL_X0+20*mm, y-18.5*mm, subtitle)
    doc.y = y-24*mm-5*mm

def main(out="eIDAS_Study_Manual_EN_pilot.pdf"):
    blocks=[b for f in sorted(glob.glob("pilot/out/*_en.json")) for b in json.load(open(f))]
    doc=Doc(out)
    doc.c.setTitle("eIDAS — Study and Audit Manual, English Edition")
    title_page(doc); legend_page(doc)
    doc.new_page("Part A · Electronic Identification","")
    part_banner(doc,"A","Electronic Identification","Chapter II · Articles 5a to 5f")
    cur=None
    for b in blocks:
        if b["article"]!=cur:
            cur=b["article"]
            doc.c.bookmarkPage(f"art{cur}"); doc.c.addOutlineEntry(f"Article {cur}", f"art{cur}", 0)
        draw_block(doc, b, "Part A · Electronic Identification")
    doc.c.showPage(); doc.c.save()
    return out, doc.page, len(blocks)

if __name__=="__main__":
    f,p,n=main(); print(f"built {f}: {p} pages, {n} blocks  =>  {p/n:.2f} pages/block  =>  220 blocks ~ {round(p/n*220)} pp")

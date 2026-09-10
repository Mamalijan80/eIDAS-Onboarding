# -*- coding: utf-8 -*-
"""Renderers for the reference parts C to I."""
from reportlab.lib.units import mm
import design as D, richtext as R
from tables import flow_table

def _s(n, *styles): return list(styles)

SPEC = {
 "C": dict(title="All Articles at a Glance", sub="Chapters I to VI and Annexes I to VII",
   heads=["Art.","Ch.","Subject","Main addressee","Deadline","Key point","Prio"],
   keys=["article","chapter","topic","addressee","deadline","key_point","priority"],
   widths=[11*mm,10*mm,32*mm,25*mm,24*mm,42*mm,8*mm],
   styles=["blockid","xgloss","xgloss","xgloss","xgloss","xgloss","xgloss"]),
 "D": dict(title="Roles in the eIDAS System", sub="Who acts, who is supervised, who benefits",
   heads=["Role","Task","Typical articles","Delimitation"],
   keys=["role","task","articles","delimitation"],
   widths=[24*mm,52*mm,34*mm,42*mm],
   styles=["xtitle","xgloss","xgloss","xgloss"]),
 "E": dict(title="Deadline Calendar", sub="One-off dates and recurring obligations",
   heads=["Date / rhythm","Article","What must be done","Addressee","Note"],
   keys=["date","article","action","addressee","note"],
   widths=[22*mm,20*mm,48*mm,26*mm,36*mm],
   styles=["deadline","blockid","xgloss","xgloss","xgloss"]),
 "F": dict(title="Signature and Seal Side by Side", sub="What matches — and where the mirror ends",
   heads=["Subject","Signature","Seal","Common content","Difference"],
   keys=["subject","signature","seal","common","difference"],
   widths=[22*mm,15*mm,15*mm,52*mm,48*mm],
   styles=["xtitle","blockid","blockid","xgloss","xgloss"]),
 "H": dict(title="Corrections Against the Previous Edition", sub="What was checked against the Regulation and put right",
   heads=["Type","Reference","Subject","Previous wording","Finding against the Regulation"],
   keys=["kind","reference","subject","previous","finding"],
   widths=[20*mm,22*mm,26*mm,42*mm,42*mm],
   styles=["xtitle","blockid","xgloss","xgloss","xgloss"]),
}

import re as _re
def _tidy(key, col, v):
    v=str(v or "")
    if col in ("article","reference","signature","seal") or (key=="C" and col=="article"):
        v=_re.sub(r'\bArticles?\s+','',v)     # the column header already says it
        v=_re.sub(r'\bAnnex\s+','Ann. ',v)
    if col=="chapter": v=_re.sub(r'^Ch\.\s*','',v)
    return v

def part_table(doc, key, rows, banner):
    sp=SPEC[key]
    banner(doc, key, sp["title"], sp["sub"])
    data=[[_tidy(key,k,r.get(k,"")) for k in sp["keys"]] for r in rows]
    return flow_table(doc, sp["heads"], data, sp["widths"], sp["styles"])

def part_cards(doc, rows, banner):
    """Part G: question above, answer below a fold rule - answers stay coverable."""
    banner(doc, "G", "Retrieval Cards", "Cover the answer, respond, then compare")
    c=doc.c
    for r in rows:
        qf,qs,ql,qc = D.T["audit"]; af,as_,al,ac = D.T["content"]
        qn = R.wrap_runs([(f'{r.get("number","")}  ', "Mono-Bold", qs, D.BLUE),
                          (r.get("question",""), qf, qs, qc)], D.TEXT_X1-D.TEXT_X0-16*mm)
        an = R.wrap_runs([(r.get("answer",""), af, as_, ac)], D.TEXT_X1-D.TEXT_X0-16*mm)
        h = len(qn)*ql + len(an)*al + 9*mm
        doc.need(h)
        y=doc.y
        y=R.draw_lines(c, qn, D.TEXT_X0, y, ql)
        d=(r.get("difficulty") or "").strip()
        if d:
            c.setFont("UI-Bold",6.0); c.setFillColor(D.GREY)
            c.drawRightString(D.TEXT_X1, doc.y, d.upper())
        y-=1.6*mm
        c.setStrokeColor(D.HAIRLINE); c.setLineWidth(0.4); c.setDash(1.6,1.6)
        c.line(D.TEXT_X0, y+2.4*mm, D.TEXT_X1, y+2.4*mm); c.setDash()
        y=R.draw_lines(c, an, D.TEXT_X0, y, al)
        doc.y=y-4.5*mm
    return doc.y

def part_index(doc, entries, banner):
    """Part I: reference digest as continuous two-column text. Entries may break across
    columns and pages; a heading is never left stranded at the foot of a column."""
    banner(doc, "I", "Reference Digest", "What each provision says, ordered for lookup")
    COLW = (D.TEXT_X1 - D.TEXT_X0 - 6*mm) / 2
    COLX = (D.TEXT_X0, D.TEXT_X0 + COLW + 6*mm)
    tf, ts, tl, tc = D.T["xtitle"]
    gf, gs, gl, gc = D.T["xgloss"]

    stream = []            # (wrapped_line | None, leading, is_heading)
    for e in entries:
        for ln in R.wrap_runs([(e.get("ref", ""), tf, ts, tc)], COLW):
            stream.append((ln, tl, True))
        for ln in R.wrap_runs([(e.get("text", ""), gf, gs, gc)], COLW):
            stream.append((ln, gl, False))
        stream.append((None, 2.0*mm, False))       # gap between entries

    def widow_height(k):
        """Height of the heading block at k plus two lines of its body."""
        h = 0.0
        while k < len(stream) and stream[k][2]:
            h += stream[k][1]; k += 1
        for _ in range(2):
            if k < len(stream): h += stream[k][1]; k += 1
        return h

    i = 0
    top = doc.y
    while i < len(stream):
        for ci in (0, 1):
            x, y = COLX[ci], top
            while i < len(stream):
                line, lead, is_head = stream[i]
                if y - lead < D.Y_BOT: break
                if is_head and y - widow_height(i) < D.Y_BOT: break
                if line is not None:
                    R.draw_lines(doc.c, [line], x, y, lead)
                y -= lead
                i += 1
        if i < len(stream):
            doc.new_page(); top = doc.y
        else:
            doc.y = D.Y_BOT
    return doc.y

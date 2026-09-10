import re, json
from collections import Counter

pages=json.load(open("SKRIPT_pages.json"))
FOOT=re.compile(r'^(?:\d{1,3}|Art\.\s*\d+[a-z]?\s+\d{1,3}|Artikel\s*\d+[a-z]?\s+\d{1,3})$')
ARTHEAD=re.compile(r'^Artikel\s+(\d+[a-z]?)\s+(.+)$')
TEILHEAD=re.compile(r'^(TEIL\s+[A-I]|Teil\s+[A-I]\b)')

stream=[]; titles={}
for pno,pg in enumerate(pages,1):
    lines=pg.split("\n")
    for j,ln in enumerate(lines):
        if FOOT.match(ln.strip()):            # running footer / page number
            continue
        m=ARTHEAD.match(ln.strip())
        if m and not re.search(r'\bAbs(atz|\.)\b|\bBuchst', ln):
            titles.setdefault(m.group(1), m.group(2).strip())
            continue                           # structural heading, not block body
        stream.append((pno, ln))

HDR=re.compile(r'^Art\.\s*(\d+[a-z]?)\s*\|\s*(.+?)\s*$')
MOD=r'(MUSS(?:\s*/\s*[\wÄÖÜ]+)?|DARF NICHT|KANN(?:\s*/\s*DARF)?|SOLL|Definition|Grundsatz|Verfahren|Verweisnorm|Auftrag Kommission|Rechtswirkung(?:\s*/\s*Vermutung)?)'
TAIL=re.compile(r'^(.*?)(?:\s+'+MOD+r')?(?:\s+(L[123]))?$')
FLD=re.compile(r'^(THEMA|ADRESSAT|INHALT|ZWECK|FRIST|VERWEISE|PRUEFUNG|MERKSATZ)\b\s*(.*)$')

idx=[i for i,(p,l) in enumerate(stream) if HDR.match(l)]
blocks=[]
for k,i in enumerate(idx):
    end=idx[k+1] if k+1<len(idx) else len(stream)
    pno,hline=stream[i]
    art,rest=HDR.match(hline).groups()
    t=TAIL.match(rest)
    locus=(t.group(1) or "").strip(); modality=(t.group(2) or "").strip(); lvl=(t.group(3) or "").strip()
    fields={}; cur=None; buf=[]
    for p,l in stream[i+1:end]:
        if TEILHEAD.match(l): break
        f=FLD.match(l)
        if f:
            if cur: fields[cur]=" ".join(buf).strip()
            cur,buf=f.group(1),[f.group(2)]
        elif cur: buf.append(l)
    if cur: fields[cur]=" ".join(buf).strip()
    if "THEMA" not in fields: continue
    blocks.append({"id":f"{art}|{locus}","article":art,"article_title":titles.get(art,""),
                   "locus":locus,"modality":modality,"level":lvl,"page":pno,"fields":fields})

json.dump(blocks, open("blocks.json","w"), ensure_ascii=False, indent=1)
json.dump(titles, open("article_titles.json","w"), ensure_ascii=False, indent=1)
print("Normbloecke:",len(blocks),"| article titles:",len(titles))
# debris check
deb=[b["id"] for b in blocks if re.search(r'\s(?:Art\.|Artikel)\s*\d+[a-z]?\s*\d{1,3}\s*$|\s\d{1,3}\s*$', b["fields"].get("MERKSATZ",""))]
print("MERKSATZ with trailing debris:", len(deb))
wel=[b["id"] for b in blocks if re.search(r'\bArtikel\s+\d+[a-z]?\s+[A-ZÄÖÜ][a-zäöü]', b["fields"].get("MERKSATZ",""))]
print("MERKSATZ with welded heading:", len(wel))
print("modality:",Counter(b["modality"] for b in blocks).most_common())

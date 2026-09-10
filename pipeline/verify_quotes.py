import json,glob,re,unicodedata
arts=json.load(open("articles_aligned.json"))
def norm(s):
    s=unicodedata.normalize("NFKC",s)
    s=s.replace('’',"'").replace('‘',"'").replace('“','"').replace('”','"')
    s=s.replace('„','"').replace('—','-').replace('–','-').replace('­','')
    s=re.sub(r'\s+',' ',s)
    return s.lower().strip(' .,;:')
CORPUS={a:norm(v["en"]) for a,v in arts.items()}
ALL=norm(" ".join(v["en"] for v in arts.values()))
QUOTE=re.compile(r'[‘“„"]([^’”"]{25,})[’”"]\s*✓\s*(?:Art\.|Article)\s*(\d+[a-z]?)')
rows=[]
for f in sorted(glob.glob("pilot/out/*_en.json")):
    for b in json.load(open(f)):
        for fld,val in b["fields"].items():
            for m in QUOTE.finditer(val):
                q,art=norm(m.group(1)), m.group(2)
                hit_art = art in CORPUS and q in CORPUS[art]
                hit_any = q in ALL
                rows.append((b["id"],fld,art,hit_art,hit_any,m.group(1)[:70]))
ok=sum(1 for r in rows if r[3]); anyh=sum(1 for r in rows if r[4])
print(f"checkmarked quotes found: {len(rows)}")
print(f"  verbatim in cited article : {ok}")
print(f"  verbatim somewhere in reg : {anyh}")
print(f"  NOT verbatim anywhere     : {len(rows)-anyh}")
print("\n--- failures ---")
for i,fl,a,ha,hy,txt in rows:
    if not hy: print(f"  [{i}] {fl} -> cites Art.{a}: {txt!r}")
print("\n--- verbatim but in a different article than cited ---")
for i,fl,a,ha,hy,txt in rows:
    if hy and not ha: print(f"  [{i}] {fl} cites Art.{a}: {txt!r}")

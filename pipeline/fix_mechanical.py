import json,glob,re,os,shutil
OUT="pilot/out"
os.makedirs("pilot/out_backup",exist_ok=True)
for f in glob.glob(OUT+"/*_en.json"):
    shutil.copy(f, "pilot/out_backup/"+os.path.basename(f))

stats={}
def bump(k,n=1): stats[k]=stats.get(k,0)+n

# --- exact official replacements for the two failing quotes
QFIX=[
 ("three months of the suspension or revocation, the notifying Member State shall notify the other Member States and the Commission of the withdrawal of the electronic identification scheme",
  "three months of the suspension or revocation, the notifying Member State shall notify other Member States and the Commission of the withdrawal of the electronic identification scheme"),
 ("gatekeepers shall enable them, in particular, effective interoperability with — and access for the purposes of interoperability to — the same operating system, hardware or software features",
  "gatekeepers shall in particular allow them effective interoperability with, and, for the purposes of interoperability, access to, the same operating system, hardware or software features"),
]
# --- canonical gloss titles (3 substantive divergences)
GLOSS=[("Mandatory technical properties","Mandatory technical characteristics"),
       ("Implementing act on the core requirements","Implementing act on the core wallet requirements"),
       ("Obligation of certain private parties to accept","Acceptance obligation of certain private entities")]
# --- trailing extraction debris (running footer welded to field end)
DEBRIS=re.compile(r'\s*(?:Article|Art\.)\s*\d+[a-z]?\s+\d{1,3}\s*$|\s+\d{1,3}\s*$')
WELD=re.compile(r'\s*(?:Article|Artikel)\s+\d+[a-z]?\s+(?:[A-Z][A-Za-z\-]*\s+){1,12}?(?=(?:Art\.|Article)\s*\d+[a-z]?\s+\d{1,3}\s*$|$)')

for f in sorted(glob.glob(OUT+"/*_en.json")):
    data=json.load(open(f)); ch=False
    for b in data:
        for k,v in list(b["fields"].items()):
            o=v
            for a,c in QFIX:
                if a in v: v=v.replace(a,c); bump("quote_official")
            for a,c in GLOSS:
                if a in v: v=v.replace(a,c); bump("gloss_canonical")
            if k=="KEY POINT":
                v2=WELD.sub("",v)
                if v2!=v: bump("weld_stripped"); v=v2
                v2=DEBRIS.sub("",v).rstrip()
                if v2!=v: bump("debris_stripped"); v=v2
            # German quotation marks around English text -> English curly
            if '„' in v:
                v=re.sub(r'„([^“]*)“', lambda m:'“'+m.group(1)+'”', v); bump("quotes_normalised")
            if v!=o: b["fields"][k]=v; ch=True
        # locus_en case
        le=b.get("locus_en","")
        if le:
            n=re.sub(r'^paragraph\b','Paragraph',le); n=re.sub(r'^Paragraphs\b','Paragraphs',n)
            if n!=le: b["locus_en"]=n; bump("locus_case"); ch=True
    if ch: json.dump(data, open(f,"w"), ensure_ascii=False, indent=1)
print("MECHANICAL FIXES APPLIED:")
for k,v in sorted(stats.items()): print(f"  {k:22s} {v}")

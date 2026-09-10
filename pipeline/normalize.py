import re, json

START = re.compile(
  r'^(?:'
  r'[▼►][BCM]\d*'
  r'|Artikel\s+\d+[a-z]?\b|Article\s+\d+[a-z]?\b'
  r'|KAPITEL\s+[IVXL]+\b|CHAPTER\s+[IVXL]+\b'
  r'|ABSCHNITT\s+\d+\b|SECTION\s+\d+\b'
  r'|ANHANG\b|ANNEX\b'
  r'|\(\d+[a-z]?\)\s'
  r'|\([a-z]{1,2}\)\s'
  r'|\d{1,2}\.\s'
  r'|[—–]\s'
  r')')

def norm(tag):
    lines=[l.strip() for pg in open(f"{tag}_layout.txt").read().split("\n\n<<<PAGE>>>\n\n")
           for l in pg.split("\n") if l.strip()]
    out=[]
    for ln in lines:
        ln = re.sub(r'\s+', ' ', ln).strip()
        if out and not START.match(ln):
            prev=out[-1]
            if prev.endswith('­'):
                out[-1]=prev.rstrip('­')+ln
            elif prev.endswith('-') and re.match(r'^[a-zäöüß]', ln):
                out[-1]=prev+ln          # real hyphen: keep the compound intact
            else:
                out[-1]=prev+' '+ln
            continue
        out.append(ln)
    txt="\n".join(out)
    # residual soft hyphens (mid-line): drop
    txt=txt.replace('­','')
    # quote spacing: ’ directly followed by a letter -> insert space
    txt=re.sub(r'’(?=[A-Za-zÄÖÜäöü])', '’ ', txt)
    txt=re.sub(r'\s+([,;.:])', r'\1', txt)
    txt=re.sub(r' {2,}',' ',txt)
    open(f"{tag}_clean.txt","w").write(txt)
    return txt

for tag in ["DE","EN"]:
    t=norm(tag); print(tag,"lines",t.count("\n")+1,"chars",len(t))

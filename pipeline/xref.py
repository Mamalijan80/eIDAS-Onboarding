import json,glob,re
from collections import defaultdict, Counter

INSTR=r'(?:GDPR|eIDAS|DMA|DSA|NIS2|EUCC|ARF|EUDI)'
CITE=(r'(?:'+INSTR+r'\s+)?(?:Article|Annex)\s+\d*[a-zA-Z]*(?:\([^)]*\))?'
      r'(?:\s*(?:and|to)\s*\([^)]*\))?(?:\s+'+INSTR+r')?'
      r'|'+INSTR)
SPLIT=re.compile(r'(?:'+CITE+r')\s*·')
HEAD=re.compile(r'^((?:'+CITE+r'))\s*·\s*(.*)$', re.S)
QUOTE=re.compile(r'([“„][^”“]{20,}[”“])\s*(✓|●)?', re.S)
QCITE=re.compile(r'^\s*((?:Art\.|Article|Annex)\s+[^\s]+(?:\s+(?:GDPR|eIDAS|DMA|DSA|NIS2))?)', re.S)
DOT=re.compile(r'\s*●\s*([^.]{0,80}\.)?')
REL=re.compile(r'\bRelevance here:\s*', re.S)

def _chunks(field):
    """Record boundaries from non-overlapping, leftmost-longest citation+middot matches."""
    field=field or ""
    starts=[m.start() for m in SPLIT.finditer(field)]
    if not starts: return [field] if field.strip() else []
    out=[]
    if starts[0]>0 and field[:starts[0]].strip(): out.append(field[:starts[0]])
    for i,st in enumerate(starts):
        en=starts[i+1] if i+1<len(starts) else len(field)
        out.append(field[st:en])
    return out

def _tidy_cite(c):
    c=re.sub(r'\s+',' ',c).strip()
    m=re.match(r'^('+INSTR+r')\s+((?:Article|Annex)\b.*?)(?:\s+('+INSTR+r'))?$', c)
    if m:
        lead, core, trail = m.group(1), m.group(2), m.group(3)
        return f"{core} {trail or lead}"
    return c

def parse(field):
    recs=[]
    for chunk in _chunks(field):
        chunk=chunk.strip()
        if not chunk: continue
        m=HEAD.match(chunk)
        if not m:
            if recs: recs[-1]["body"]=(recs[-1]["body"]+" "+chunk).strip()
            else: recs.append({"cite":"","body":chunk,"quote":None,"mark":None,"qcite":None,"relevance":None})
            continue
        cite, rest = _tidy_cite(m.group(1)), m.group(2).strip()
        quote=mark=qcite=None
        q=QUOTE.search(rest)
        if q:
            quote=q.group(1).strip('“”„'); mark=q.group(2)
            after=rest[q.end():]
            mq=QCITE.match(after)
            if mq: qcite=mq.group(1).strip(); after=after[mq.end():]
            rest=(rest[:q.start()].strip()+" "+after.strip()).strip()
        if not mark and '●' in rest:
            mark='●'; rest=DOT.sub(' ', rest).strip()
        rel=None
        if REL.search(rest):
            a,b=REL.split(rest,1); rest=a.strip(); rel=b.strip()
        recs.append({"cite":cite,"body":re.sub(r'\s{2,}',' ',rest).strip(),"quote":quote,
                     "mark":mark,"qcite":qcite,"relevance":rel})
    return recs

STARTERS={"The","This","That","These","Those","It","A","An","There","Both","Each","Every",
 "Where","When","If","Without","Together","Numerous","Establishes","Covers","Staggers","Applies",
 "Continues","Not","Only","Such","Its","Their","Under","Sets","Defines","Requires","Adds","Gives",
 "Allows","Obliges","Governs","Lists","Introduces","Extends","Provides","Specifies","Makes","Two","Three"}

def split_title(body, maxw=11):
    """Separate the reference's title (a noun phrase, no verb) from the gloss that follows."""
    ws=body.split()
    for i,w in enumerate(ws):
        if i>=2 and w.strip(",;:") in STARTERS:
            return " ".join(ws[:i]), " ".join(ws[i:])
        if i>=maxw: break
    return "", body

if __name__=="__main__":
    B=[b for f in sorted(glob.glob("pilot/out/*_en.json")) for b in json.load(open(f))]
    allrecs=[]; percite=defaultdict(list); unparsed=0
    for b in B:
        r=parse(b["fields"].get("CROSS-REFERENCES",""))
        allrecs+=r
        for x in r:
            percite[x["cite"]].append(x["body"])
            if not x["cite"]: unparsed+=1
    print("blocks:",len(B),"| sub-records:",len(allrecs),"| distinct citations:",len(percite))
    print("per block:",sorted(Counter(len(parse(b['fields'].get('CROSS-REFERENCES',''))) for b in B).items()))
    print("quotes:",sum(1 for x in allrecs if x['quote']),"| ✓:",sum(1 for x in allrecs if x['mark']=='✓'),
          "| ●:",sum(1 for x in allrecs if x['mark']=='●'),"| relevance:",sum(1 for x in allrecs if x['relevance']))
    print("unparsed:",unparsed)

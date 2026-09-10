import re, json, bisect

def key(a):
    m=re.match(r'(\d+)([a-z]?)',a); return (int(m.group(1)), m.group(2) or '')

XREF=re.compile(r'^(?:Artikel|Article)\s+\d+[a-z]?\s*(\(|Absatz|Absätze|Buchstabe|Buchstaben|paragraph|point)')

def lis(cands):
    """longest strictly-increasing subsequence by article key"""
    n=len(cands)
    if not n: return []
    tails=[]; tails_idx=[]; prev=[-1]*n
    for i,(_,num) in enumerate(cands):
        k=key(num)
        j=bisect.bisect_left(tails,k)
        if j==len(tails): tails.append(k); tails_idx.append(i)
        else: tails[j]=k; tails_idx[j]=i
        prev[i]=tails_idx[j-1] if j>0 else -1
    out=[]; i=tails_idx[-1]
    while i!=-1: out.append(cands[i]); i=prev[i]
    return out[::-1]

def seg(tag, artword):
    lines=open(f"{tag}_clean.txt").read().split("\n")
    pat=re.compile(r'^'+artword+r'\s+(\d+[a-z]?)\b')
    cand=[(i,m.group(1)) for i,l in enumerate(lines) if (m:=pat.match(l)) and not XREF.match(l)]
    kept=lis(cand)
    arts={}
    for k,(i,num) in enumerate(kept):
        end=kept[k+1][0] if k+1<len(kept) else len(lines)
        arts[num]="\n".join(lines[i:end]).strip()
    return arts, len(cand), len(kept)

de,cd,kd=seg("DE","Artikel"); en,ce,ke=seg("EN","Article")
print(f"DE candidates {cd} -> kept {kd} | EN candidates {ce} -> kept {ke}")
common=sorted(set(de)&set(en), key=key)
print("aligned:",len(common))
print("DE-only:",sorted(set(de)-set(en),key=key),"| EN-only:",sorted(set(en)-set(de),key=key))
json.dump({k:{"de":de[k],"en":en[k]} for k in common}, open("articles_aligned.json","w"), ensure_ascii=False, indent=1)
print("art3 chars DE/EN:", len(de.get("3","")), "/", len(en.get("3","")))

gd=dict((m.group(1),m.group(2).strip()) for m in re.finditer(r'(?m)^(\d+[a-z]?)\.\s*„([^“]+)“', de["3"]))
ge=dict((m.group(1),m.group(2).strip()) for m in re.finditer(r'(?m)^\((\d+[a-z]?)\)\s*‘([^’]+)’', en["3"]))
ks=sorted(set(gd)&set(ge), key=key)
gloss=[{"no":k,"de":gd[k],"en":ge[k]} for k in ks]
json.dump(gloss, open("glossary_art3.json","w"), ensure_ascii=False, indent=1)
print(f"\nglossary pairs: {len(gloss)}  (DE defs {len(gd)}, EN defs {len(ge)})")

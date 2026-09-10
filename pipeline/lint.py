import json,glob,re
from collections import Counter
B=[b for f in sorted(glob.glob("pilot/out/*_en.json")) for b in json.load(open(f))]
D=json.load(open("pilot_blocks.json"))
print(f"blocks EN {len(B)} | DE {len(D)}")
def rep(name,bad,total=None,show=3):
    ok = "PASS" if not bad else "FAIL"
    print(f"[{ok}] {name:44s} {len(bad)}" + (f"/{total}" if total else ""))
    for x in bad[:show]: print("        -", str(x)[:135])

# 1 audit check ends with ?
rep("AUDIT CHECK ends in '?'", [b['id'] for b in B if 'AUDIT CHECK' in b['fields'] and not b['fields']['AUDIT CHECK'].strip().endswith('?')], len(B))
# 2 key point length
kp=[(b['id'],len(b['fields'].get('KEY POINT',''))) for b in B]
rep("KEY POINT <= 90 chars", [f"{i} ({n})" for i,n in kp if n>90], len(B))
# 3 residual debris
rep("no trailing page-number debris", [b['id'] for b in B for k,v in b['fields'].items() if re.search(r'(?:Article|Art\.)\s*\d+[a-z]?\s+\d{1,3}\s*$', v)])
rep("no welded next-article heading", [b['id'] for b in B if re.search(r'\bArticle\s+\d+[a-z]?\s+[A-Z][a-z]+\s+[a-z]', b['fields'].get('KEY POINT',''))])
# 4 german quote marks
rep("no German quotation marks", [b['id'] for b in B for v in b['fields'].values() if '„' in v])
# 5 modality vs indicative
IND=[b['id'] for b in B if b.get('modality_en')=='SHALL' and 'CONTENT' in b['fields']
     and not re.search(r'\bshall\b|\bSHALL\b', b['fields']['CONTENT'])]
rep("SHALL badge backed by 'shall' in CONTENT", IND, len(B))
# 6 house style
w=Counter(); 
for b in B:
    t=" ".join(b['fields'].values())
    w['full']+=len(re.findall(r'European Digital Identity Wallet', t))
    w['bare']+=len(re.findall(r'(?<!European Digital Identity )\bWallet\b', t))
    w['artdot']+=len(re.findall(r'\bArt\.\s*\d', t)); w['artfull']+=len(re.findall(r'\bArticle\s+\d', t))
    w['emdash']+=t.count('—'); w['endash']+=t.count('–'); w['hyphsp']+=len(re.findall(r'\s-\s', t))
print(f"[INFO] Wallet naming: full {w['full']} / bare {w['bare']}")
print(f"[INFO] 'Art.' {w['artdot']} vs 'Article' {w['artfull']}")
print(f"[INFO] dashes: em {w['emdash']} / en {w['endash']} / spaced-hyphen {w['hyphsp']}")
# 7 GDPR ambiguity
amb=[b['id'] for b in B if re.search(r'(?:^|\.)\s*Article\s+(5|25)\s*[·.]', b['fields'].get('CROSS-REFERENCES',''))]
rep("cross-ref headings disambiguated (Art 5/25)", amb)
# 8 field parity DE/EN
M={'THEMA':'TOPIC','ADRESSAT':'ADDRESSEE','INHALT':'CONTENT','ZWECK':'PURPOSE','FRIST':'DEADLINE',
   'VERWEISE':'CROSS-REFERENCES','PRUEFUNG':'AUDIT CHECK','MERKSATZ':'KEY POINT'}
par=[]
for de,en in zip(D,B):
    exp={M[k] for k in de['fields']}
    if exp!=set(en['fields']): par.append(f"{de['id']}: {exp^set(en['fields'])}")
rep("DE/EN field-set parity", par, len(B))
# 9 by default
rep("5a(5)(g) carries 'by default'", [b['id'] for b in B if b['id'].startswith('5a|Abs. 5 g') and 'by default' not in b['fields'].get('CONTENT','')])

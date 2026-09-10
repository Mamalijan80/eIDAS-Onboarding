import json,glob,re,os,shutil
OUT="pilot/out"
os.makedirs("pilot/out_backup2",exist_ok=True)
for f in glob.glob(OUT+"/*_en.json"): shutil.copy(f,"pilot/out_backup2/"+os.path.basename(f))
st={}
def bump(k,n=1): st[k]=st.get(k,0)+n

# D1: the DE/EN divergence - the English edition must follow the English wording
D1_BLOCK={
 "TOPIC":"Provision at assurance level high",
 "AUDIT CHECK":"Does the underlying electronic identification scheme actually meet assurance level high – and is the exemption from Articles 7, 9, 10, 12 and 12a under Article 5a(22) documented?",
 "KEY POINT":"EUDI Wallet = electronic identification means at assurance level high.",
}
D1_SUBS=[
 ("shall be provided under a NOTIFIED electronic identification scheme with assurance level HIGH",
  "shall be provided under an electronic identification scheme with assurance level HIGH"),
 ("Is the Wallet provided under a notified electronic identification (eID) scheme at assurance level high (paragraph 11)?",
  "Is the Wallet provided under an electronic identification (eID) scheme at assurance level high (paragraph 11)?"),
 ("Provision under a notified scheme.","Provision at assurance level high."),
 ("are to be provided under a notified electronic identification scheme with assurance level high",
  "are to be provided under an electronic identification scheme with assurance level high"),
 ("In law the Wallet is therefore a notified electronic identification means and not a special object",
  "In law the Wallet is therefore an electronic identification means at assurance level high and not a special object"),
 ("Provision under a notified scheme","Provision at assurance level high"),
]
# D2 ARF title, D4/D5/D6 retrieval cues
ARF="Architecture and Reference Framework of the European Digital Identity Wallet"
D2_SUBS=[("Architecture and Reference Framework of the EUDI Wallet",ARF),
         ("Architecture and Reference Framework of the EU Digital Identity Wallet",ARF)]
CUES={
 "5f|Abs. 1":"Paragraph 1 the State, 2 private parties except micro/small, 3 very large platforms.",
 "5a|Abs. 5 g + UAbs. 2":"Free QES for all natural persons BY DEFAULT – MS MAY limit it to non-professional use.",
 "5a|Abs. 21":"Accessible on an equal basis for persons with disabilities – Directive (EU) 2019/882.",
}
QRE=re.compile(r'[“][^”]*[”]')
def protect(v):
    q=[]
    def s(m): q.append(m.group(0)); return f"\x00{len(q)-1}\x00"
    return QRE.sub(s,v), q
def restore(v,q): return re.sub(r'\x00(\d+)\x00', lambda m:q[int(m.group(1))], v)

for f in sorted(glob.glob(OUT+"/*_en.json")):
    data=json.load(open(f)); ch=False
    for b in data:
        for k,v in list(b["fields"].items()):
            o=v
            for a,c in D1_SUBS+D2_SUBS:
                if a in v: v=v.replace(a,c); bump("d1_d2")
            if b["id"]=="5a|Abs. 11" and k in D1_BLOCK: v=D1_BLOCK[k]; bump("d1_block")
            if k=="KEY POINT" and b["id"] in CUES: v=CUES[b["id"]]; bump("cue_fixed")
            # D3: one term policy - full term in prose, EUDI Wallet only in KEY POINT
            if k!="KEY POINT":
                v,q=protect(v)
                n=len(re.findall(r'(?<!European Digital Identity )(?<!EUDI )(?<!EU Digital Identity )\b[Ww]allet\b', v))
                if n:
                    v=re.sub(r'(?<!European Digital Identity )(?<!EUDI )(?<!EU Digital Identity )\b[Ww]allet\b',
                             'European Digital Identity Wallet', v); bump("term_policy",n)
                v=restore(v,q)
                v=re.sub(r'(European Digital Identity Wallet)(?:s?\s+European Digital Identity Wallet)+', r'\1', v)
            if v!=o: b["fields"][k]=v; ch=True
    if ch: json.dump(data,open(f,"w"),ensure_ascii=False,indent=1)
print("FINAL FIXES:"); [print(f"  {k:14s} {v}") for k,v in sorted(st.items())]

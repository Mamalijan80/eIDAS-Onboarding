from pypdf import PdfReader
import re
SRC="/root/.claude/uploads/678a16ec-3ace-516d-958d-18e01f302da6/"
FILES={"DE":"7f4c41ba-CELEX_02014R091020241018_DE_TXT.pdf","EN":"8648ce55-CELEX_02014R091020241018_EN_TXT.pdf"}
for tag,fn in FILES.items():
    r=PdfReader(SRC+fn); out=[]
    for i,p in enumerate(r.pages):
        t=p.extract_text(extraction_mode="layout")
        lines=[]
        for ln in t.split("\n"):
            ln=re.sub(r'\s{2,}',' ',ln).strip()
            if not ln: continue
            if re.match(r'^02014R0910\s*[—–-]', ln): continue   # page header
            lines.append(ln)
        out.append("\n".join(lines))
    open(f"{tag}_layout.txt","w").write("\n\n<<<PAGE>>>\n\n".join(out))
    print(tag,"pages",len(out),"chars",sum(len(x) for x in out))

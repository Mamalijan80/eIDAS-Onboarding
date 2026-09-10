import json, re, math
blocks=json.load(open("pilot_blocks.json"))
arts=json.load(open("articles_aligned.json"))
gloss=json.load(open("glossary_art3.json"))

# reference pack: official DE/EN text for the pilot articles
refs={a:arts[a] for a in ["5a","5b","5c","5d","5e","5f"] if a in arts}
json.dump(refs, open("pilot/official_articles.json","w"), ensure_ascii=False, indent=1)
json.dump(gloss, open("pilot/glossary.json","w"), ensure_ascii=False, indent=1)
open("pilot/learning_architecture.txt","w").write(open("lernarchitektur.txt").read())

B=9
batches=[blocks[i:i+B] for i in range(0,len(blocks),B)]
for i,b in enumerate(batches,1):
    json.dump(b, open(f"pilot/batches/batch{i:02d}.json","w"), ensure_ascii=False, indent=1)
print("blocks",len(blocks),"-> batches",len(batches))
for i,b in enumerate(batches,1):
    ch=sum(len(json.dumps(x,ensure_ascii=False)) for x in b)
    print(f"  batch{i:02d}: {len(b)} blocks, {ch:6d} chars, arts {sorted(set(x['article'] for x in b))}")
print("\nofficial ref chars:", sum(len(v['de'])+len(v['en']) for v in refs.values()))

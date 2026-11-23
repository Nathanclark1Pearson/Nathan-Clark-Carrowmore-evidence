"""Score a labels file against YOUR gold sheet.  python eval.py labels_baseline.json [gold_sheet.csv]
Headline metric is not accuracy: it is FALSE EVIDENCE = labels that say performed/directed+skilled where you said otherwise."""
from config import DATA,OUT,APP
import json, csv, sys
lab=json.load(open(OUT/sys.argv[1])); gold={}
for r in csv.DictReader(open(sys.argv[2] if len(sys.argv)>2 else OUT/'gold_sheet.csv')):
    if r['your_labels'] is None: continue
    s={tuple(x.strip().split(':')) for x in r['your_labels'].split(';') if x.strip()}
    gold[r['template_id']]=s
if not any(gold.values()): sys.exit('gold sheet is empty - label it first')
fe=tp=fp=fn=0; bad=[]
for tid,g in gold.items():
    m={(l['req'],l['role'],l['level']) for l in lab[tid]['labels']}
    tp+=len(m&g); fp+=len(m-g); fn+=len(g-m)
    strong=lambda S:{(a,b) for a,b,c in S if b in('performed','directed') and c=='skilled'}
    for x in strong(m)-strong(g): fe+=1; bad.append((tid,x))
print(f'templates scored {len(gold)}  precision {tp/max(tp+fp,1):.2f}  recall {tp/max(tp+fn,1):.2f}')
print(f'FALSE EVIDENCE labels (would inflate a tier): {fe}'); [print(' ',b) for b in bad[:20]]

"""Collapse 10,627 entries to unique templates (permit refs, circuit numbers, digits normalised)."""
from config import DATA,OUT,APP
import json, re, collections as C
SRC=str(DATA)+'/'
def norm(t):
    t=re.sub(r'(?i)\b(ptw|permit)\s*(/|bk\.\d+ no\.|no\.)?\s*[\w./]*\d[\w./]*','PERMIT',t)
    t=re.sub(r'(?i)\bno\.?\s?\d\b','no.N',t)
    t=re.sub(r'\d+','N',t)
    return re.sub(r'\s+',' ',t).strip()
def build():
    e=json.load(open(SRC+'logbook_entries.json'))
    g=C.OrderedDict()
    for x in e:
        n=norm(x['text']); g.setdefault(n,{'count':0,'example':x['text']})['count']+=1
    out=[{'template_id':f'T{i:03d}','template':n,**v} for i,(n,v) in enumerate(sorted(g.items()))]
    json.dump(out,open(OUT/'templates.json','w'),indent=1); return out
if __name__=='__main__':
    t=build(); print(len(t))

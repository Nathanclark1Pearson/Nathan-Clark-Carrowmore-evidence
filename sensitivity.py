"""How fragile is the inference? Re-tier every keeper x requirement under different thresholds and see what flips.
If 'evidenced' is an artefact of my cut-offs, the honest-confidence claim fails."""
from config import DATA,OUT,APP
import json, os, collections as C
from templates import norm, SRC
from requirements import REQS
K=json.load(open(SRC+'keepers.json')); E=json.load(open(SRC+'logbook_entries.json'))
T={t['template']:t['template_id'] for t in json.load(open(OUT/'templates.json'))}; L=json.load(open(OUT/'labels_baseline.json'))
by=C.defaultdict(list)
for x in E:
    for l in L[T[norm(x['text'])]]['labels']:
        by[(x['keeper_code'],l['req'])].append((x['date'][:4],l['role'],l['level']))
def tier(req,ents,min_sk,min_yrs,stale_after,now=2026):
    roles={'performed','directed'}|({'taught'} if req=='SUPERVISION' else set())
    sk=[e for e in ents if e[1] in roles and e[2]=='skilled']; rt=[e for e in ents if e[1] in roles and e[2]=='routine']
    if len(sk)>=min_sk and len({e[0] for e in sk})>=min_yrs: t='evidenced'
    elif sk: t='some'
    elif len(rt)>=5: t='routine'
    else: t='none'
    last=max((e[0] for e in sk+rt),default=None)
    return (t, bool(last and now-int(last)>=stale_after))
cur={k['keeper_code'] for k in K if k['status']=='current'}
pairs=[(k,r['id']) for k in cur for r in REQS if r['gate']]
base={p:tier(p[1],by.get(p,[]),3,2,10) for p in pairs}
print('gated keeper x requirement pairs:',len(pairs))
print('baseline (3 skilled entries, 2 years, stale after 10y): evidenced =',sum(1 for v in base.values() if v[0]=='evidenced'),
      '| evidenced AND recent =',sum(1 for v in base.values() if v==('evidenced',False)))
res={}
for ms,my,st in [(2,1,10),(2,2,10),(5,2,10),(5,3,10),(3,2,5),(3,2,15)]:
    alt={p:tier(p[1],by.get(p,[]),ms,my,st) for p in pairs}
    ev0={p for p,v in base.items() if v==('evidenced',False)}; ev1={p for p,v in alt.items() if v==('evidenced',False)}
    res[(ms,my,st)]=(len(ev1),len(ev0-ev1),len(ev1-ev0))
    print(f'  min_skilled={ms} min_years={my} stale={st}: evidenced&recent={len(ev1):3}  lost vs baseline={len(ev0-ev1):2}  gained={len(ev1-ev0):2}')
# how many baseline 'evidenced & recent' sit right on the margin (exactly 3 skilled entries or exactly 2 years)?
marg=0; tot=0
for p,v in base.items():
    if v==('evidenced',False):
        tot+=1; sk=[e for e in by[p] if e[1] in('performed','directed') and e[2]=='skilled']
        if len(sk)<=4 or len({e[0] for e in sk})<=2: marg+=1
print(f'baseline evidenced&recent claims within one step of the cut-off (<=4 skilled entries or only 2 years): {marg} of {tot}')
dist=C.Counter(len([e for e in by[p] if e[1] in('performed','directed') and e[2]=='skilled']) for p,v in base.items() if v==('evidenced',False))
print('skilled-entry counts behind recent evidenced claims:',sorted(dist.items()))
# ---- machine-readable summary for the app ----
ev0={p for p,v in base.items() if v==('evidenced',False)}
strict={p for p in pairs if tier(p[1],by.get(p,[]),5,3,10)==('evidenced',False)}
json.dump(dict(pairs=len(pairs),evidenced_recent=len(ev0),survive_strict=len(ev0&strict),margin=marg),open(OUT/'sensitivity.json','w'))

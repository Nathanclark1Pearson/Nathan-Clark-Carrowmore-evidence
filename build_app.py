"""Builds app/index.html: embeds the (privacy-trimmed) profiles + headline facts into app/template.html.
Left out on purpose: date of birth, payroll ref, failed-course outcomes, leavers, appraisals, manager notes."""
import json, re, collections as C
from config import DATA,OUT,APP
from requirements import REQS
from templates import norm
from tiers import classify
K={k['keeper_code']:k for k in json.load(open(DATA/'keepers.json'))}
P=json.load(open(OUT/'profiles.json')); D=json.load(open(OUT/'distance.json')); SENS=json.load(open(OUT/'sensitivity.json'))
E=json.load(open(DATA/'logbook_entries.json'))
mod={t['module']:t['module_name'] for k in K.values() for t in k['training_records']}
dist=C.defaultdict(list)
for r in D: dist[r['keeper']].append(r)
out=[]
for kc,v in P.items():
    if v['status']!='current': continue
    recs=[]
    for r in v['records']:
        w=r['work']; a=r['authorisation']
        recs.append(dict(r=r['req'],tier=w['tier'],ns=w['n_skilled'],nr=w['n_routine'],nc=w['n_context'],
            yrs=[w['years'][0],w['years'][-1]] if w['years'] else [],last=w['last_year'],stale=w['stale'],cav=w['caveats'],
            ex=[dict(d=e['date'],s=e['station'],t=e['text'],c=e['caveat']) for e in w['examples']],
            cx=[dict(d=e['date'],t=e['text'],c=e['caveat']) for e in w['context']],
            au=dict(s=a['status'],sc=a.get('scheme'),exp=a.get('expires') if a['status'] in('held_current','held_expiring','held_expired') else None,
                    miss=a.get('modules_missing',[]) if a['status']=='partial' else [])))
    out.append(dict(id=kc,name=v['name'],grade=v['grade'],recs=recs,
        schemes=[dict(sc=d['scheme'],held=d['held'],total=d['total'],band=d['band'],exp=d['expires'],
                      miss=[dict(m=m,st=s) for m,s in d['missing'].items()],sup=d['recent_work_evidence_for_missing']) for d in dist[kc]]))
cur={k['id'] for k in out}
# --- headline facts, all computed here so the page can't drift from the pipeline ---
pat=re.compile(r'\b(HV|permit|PTW|earth|isolat|switch|keys)',re.I)
naive=C.Counter(x['keeper_code'] for x in E if pat.search(x['text']) and x['keeper_code'] in cur)
naive_set={k for k,n in naive.items() if n>=3}; naive_n=len(naive_set)
hv=[next((r for r in k['recs'] if r['r']=='HV_SWITCH'),None) for k in out]
aware_set={k['id'] for k in out if any(r['r']=='HV_SWITCH' and r['tier'] in('evidenced','some_evidence') for r in k['recs'])}
handson=len(aware_set)
hvcls=C.Counter()
for v in P.values():
    if v['status']!='current': continue
    r=next((r for r in v['records'] if r['req']=='HV_SWITCH'),None)
    if r: hvcls[classify(r)]+=1
bands=C.Counter(r['band'] for r in D)
miss=C.Counter(s for r in D if r['band'] in('one_module_away','two_modules_away') for s in r['missing'].values())
FACTS=dict(keepers=len(out),entries=len(E),templates=len(json.load(open(OUT/'templates.json'))),naive=naive_n,handson=handson,naive_fp=len(naive_set-aware_set),naive_missed=len(aware_set-naive_set),
           hv=dict(hvcls),bands=dict(bands),miss=dict(miss),sens=SENS)
json.dump(FACTS,open(OUT/'facts.json','w'),indent=1)
DATA_JS=dict(keepers=out,facts=FACTS,reqs=[dict(id=r['id'],label=r['label'],gate=r['gate'],sc=r['scheme'],desc=r['description'],mods=r['modules']) for r in REQS],mods=mod)
html=open(APP/'template.html').read().replace('__DATA__',json.dumps(DATA_JS,separators=(',',':')))
open(APP/'index.html','w').write(html); print('app/index.html',len(html)//1024,'KB; facts:',FACTS)

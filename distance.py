"""How far is each keeper from each certification scheme? Facts from the record first, inference second.
Per keeper x scheme: modules held / missing, what happened to each missing module (never attempted /
attended-not-completed / failed), expiry, and whether logbook work evidence supports the area.
Deliberately NOT a probability of passing."""
from config import DATA,OUT,APP
import json, collections as C
from requirements import REQS
SRC=str(DATA)+'/'; NOW=2026
K=json.load(open(SRC+'keepers.json')); P=json.load(open(OUT/'profiles.json'))
mod2req=C.defaultdict(list)
for r in REQS:
    for m in r['modules']: mod2req[m].append(r['id'])
def band(held,total,cert,missing_detail):
    if cert and cert['complete'] and cert['valid_2026']: return 'certified_current'
    if cert and cert['complete']: return 'lapsed_renew'
    left=total-held
    if held==0: return 'not_started'
    if left==1: return 'one_module_away'
    if left==2: return 'two_modules_away'
    return 'three_plus_away'
UNIVERSE=C.defaultdict(set)
for k in K:
    for c in k['certifications']: UNIVERSE[c['scheme']]|=set(c['modules_held'])|set(c['modules_missing'])
UNIVERSE={s:sorted(v) for s,v in UNIVERSE.items()}
print('modules per scheme (from records):',{s:len(v) for s,v in UNIVERSE.items()})
rows=[]
for k in K:
    if k['status']!='current': continue
    tr=C.defaultdict(list)
    for t in k['training_records']: tr[t['module']].append(t['outcome'])
    prof={r['req']:r for r in P[k['keeper_code']]['records']}
    schemes={}
    for t in k['training_records']: schemes.setdefault(t['scheme'],set())
    for c in k['certifications']: schemes.setdefault(c['scheme'],set())
    for s in schemes:
        c=next((c for c in k['certifications'] if c['scheme']==s),None)
        allmods=UNIVERSE[s]
        held=c['modules_held'] if c else []; miss=[m for m in allmods if m not in held]
        det={}
        for m in miss:
            o=tr.get(m,[])
            det[m]=('failed_before' if 'failed' in o else 'attended_not_completed' if 'attended' in o else 'never_attempted')
        sup=[]
        for m in miss:
            for rq in mod2req[m]:
                p=prof.get(rq)
                if p and p['work']['tier'] in('evidenced','some_evidence') and not p['work']['stale']: sup.append(rq)
        rows.append(dict(keeper=k['keeper_code'],name=k['name'],scheme=s,held=len(held),total=len(allmods),
            band=band(len(held),len(allmods),c,det),missing=det,expires=c['expires_year'] if c and c['complete'] else None,
            recent_work_evidence_for_missing=sorted(set(sup))))
json.dump(rows,open(OUT/'distance.json','w'),indent=1)
print(len(rows),'keeper x scheme rows (current keepers, schemes with any record)')
print(C.Counter(r['band'] for r in rows))
print('\nOf one/two-module-away rows, what the missing module looks like:')
cc=C.Counter()
for r in rows:
    if r['band'] in('one_module_away','two_modules_away'):
        for m,s in r['missing'].items(): cc[s]+=1
print(dict(cc))
one=[r for r in rows if r['band']=='one_module_away']
print('\none-module-away AND recent logbook evidence in that area:',sum(1 for r in one if r['recent_work_evidence_for_missing']),'of',len(one))
print('\nby scheme, keepers one module away:',dict(C.Counter(r['scheme'] for r in one)))
print('\nexamples:')
for r in [r for r in one if r['recent_work_evidence_for_missing']][:6]: print(' ',r['keeper'],r['scheme'],f"{r['held']}/{r['total']}",r['missing'],r['recent_work_evidence_for_missing'])
# schemes where a keeper has work evidence of gated areas but zero record
nr=0
for k in K:
    if k['status']!='current': continue
    have={c['scheme'] for c in k['certifications']}|{t['scheme'] for t in k['training_records']}
    for r in REQS:
        if r['gate'] and r['scheme'] not in have:
            p=next((x for x in P[k['keeper_code']]['records'] if x['req']==r['id']),None)
            if p and p['work']['tier'] in('evidenced','some_evidence') and not p['work']['stale']: nr+=1
print('\nrecent hands-on evidence in a gated area but NO scheme record at all (could be absent, or held under an internal authorisation):',nr)

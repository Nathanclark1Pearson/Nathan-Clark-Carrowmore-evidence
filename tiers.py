"""STAGES B, C, D.  Plain code, no LLM.
B  work evidence tier   <- labels (from rules_baseline.py OR extract_llm.py) x logbook entries
C  authorisation status <- keepers.json certifications (kept completely separate from B)
D  gap + route          <- missing modules in the scheme
Usage: python src/tiers.py [labels_file]   (default labels_baseline.json)"""
from config import DATA,OUT,APP
import json, sys, collections as C
from templates import norm, SRC
from requirements import REQS
NOW=2026; STALE_AFTER=10
STRONG={'performed','directed'}
def tier_for(req,ents):
    roles=STRONG|({'taught'} if req=='SUPERVISION' else set())
    ev=[e for e in ents if e['role'] in roles]
    skilled=[e for e in ev if e['level']=='skilled']; routine=[e for e in ev if e['level']=='routine']
    yrs=lambda L:{e['date'][:4] for e in L}
    if len(skilled)>=3 and len(yrs(skilled))>=2: t='evidenced'
    elif skilled: t='some_evidence'
    elif len(routine)>=5 and len(yrs(routine))>=2: t='routine_only'
    elif ents: t='context_only'   # present/keys/permit-holder/teaching-only: shown, never counted
    else: t='none'
    last=max((e['date'][:4] for e in skilled+routine),default=None)
    return t,skilled,routine,last
def auth_for(keeper,req):
    if not req['scheme']: return dict(status='not_applicable')
    c=next((c for c in keeper['certifications'] if c['scheme']==req['scheme']),None)
    if not c: return dict(status='no_record',scheme=req['scheme'])
    held=[m for m in req['modules'] if m in c['modules_held']]
    base=dict(scheme=req['scheme'],modules_held=c['modules_held'],modules_missing=c['modules_missing'],
              relevant_modules_held=held,expires=c['expires_year'])
    if c['complete'] and c['valid_2026']:
        return dict(status='held_expiring' if c['expires_year']==NOW else 'held_current',**base)
    if c['complete']: return dict(status='held_expired',**base)
    return dict(status='partial',**base)
def build(labels_path='labels_baseline.json'):
    T={}
    for t in json.load(open(OUT/'templates.json')): T[t['template']]=t['template_id']
    L=json.load(open(OUT/labels_path)); K=json.load(open(SRC+'keepers.json')); E=json.load(open(SRC+'logbook_entries.json'))
    by=C.defaultdict(lambda:C.defaultdict(list))
    for x in E:
        lab=L[T[norm(x['text'])]]
        for l in lab['labels']:
            by[x['keeper_code']][l['req']].append(dict(date=x['date'],entry_id=x['entry_id'],station=x['station'],
              station_class=x['station_class'],text=x['text'],role=l['role'],level=l['level'],caveat=l['caveat']))
    out={}
    for k in K:
        recs=[]
        for r in REQS:
            ents=sorted(by[k['keeper_code']].get(r['id'],[]),key=lambda e:e['date'])
            tier,sk,ro,last=tier_for(r['id'],ents); au=auth_for(k,r)
            if tier=='none' and au['status'] in ('no_record','not_applicable'): continue
            ev=sk+ro; caveats=sorted({e['caveat'] for e in sk if e['caveat']})
            recs.append(dict(req=r['id'],label=r['label'],gate=r['gate'],
              work=dict(tier=tier,n_skilled=len(sk),n_routine=len(ro),n_context=len(ents)-len(ev),
                        years=sorted({e['date'][:4] for e in ev}),last_year=last,
                        stale=bool(last and NOW-int(last)>=STALE_AFTER),
                        all_skilled_caveated=bool(sk) and all(e['caveat'] for e in sk),caveats=caveats,
                        examples=(sorted(sk,key=lambda e:e['date'])[-3:] or sorted(ro,key=lambda e:e['date'])[-2:]),
                        context=[e for e in ents if e['role'] not in STRONG][-3:]),
              authorisation=au,
              route=(f"Complete {', '.join(au['modules_missing'])} ({r['scheme']})" if au['status']=='partial' and au['modules_missing']
                     else 'Renew '+r['scheme'] if au['status'] in('held_expired','held_expiring')
                     else f"No {r['scheme']} record found - check Authority records before assuming absent" if au['status']=='no_record' and r['gate'] else None)))
        out[k['keeper_code']]=dict(keeper_code=k['keeper_code'],name=k['name'],status=k['status'],grade=k['current_grade'],
                                   n_entries=sum(len(v) for v in by[k['keeper_code']].values()),records=recs)
    return out
def classify(rec):
    w=rec['work']['tier']; a=rec['authorisation']['status']; has=w in('evidenced','some_evidence'); held=a in('held_current','held_expiring')
    if rec['gate']:
        if has and rec['work']['stale']: return 'dated_experience'   # last hands-on evidence >=10y ago
        if has and held: return 'ready_on_record'
        if has: return 'experience_no_current_ticket'
        if held: return 'ticket_no_logbook_evidence'
        return 'neither'
    return 'evidenced_no_ticket_needed' if has else 'neither'
if __name__=='__main__':
    p=sys.argv[1] if len(sys.argv)>1 else 'labels_baseline.json'
    P=build(p); json.dump(P,open(OUT/'profiles.json','w'),indent=1,default=str); print('wrote profiles.json for',len(P),'keepers')

"""STAGE A (LLM version). Labels each UNIQUE TEMPLATE (530), not each entry (10,627): ~14 API calls.
Output schema == labels_baseline.json, so tiers.py and eval.py take either.
   export ANTHROPIC_API_KEY=...   [MODEL=claude-sonnet-5-5]   python extract_llm.py
Responses are cached in llm_cache/ so reruns are free."""
from config import DATA,OUT,APP
import json, os, hashlib, pathlib, re
from requirements import REQS
MODEL=os.environ.get('MODEL','claude-sonnet-5-5'); BATCH=40
REQ_IDS={r['id'] for r in REQS}; ROLES={'performed','directed','attended','custody','taught'}; LEVELS={'skilled','routine'}
REQ_TXT='\n'.join(f"- {r['id']}: {r['label']} - {r['description']}" for r in REQS)
SYSTEM=f"""You read one-line lighthouse logbook entries and report what each entry shows about the WRITER'S OWN role in a piece of work.
You are NOT judging whether anyone is qualified or authorised. Never infer a certificate, ticket or authorisation.

Requirements (use only these ids):
{REQ_TXT}

For each entry return zero or more labels {{"req","role","level","caveat"}}.
role (what the writer did, in this entry):
 performed - did the hands-on work themselves
 directed  - planned, led, authorised, issued, specified or wrote the method for the work
 attended  - present or on standby while someone else did it (witnessed, stood by, top man, attendant)
 custody   - held keys, signed on to or read or returned a permit, locked up: handling paperwork or access, not doing the work
 taught    - trained, coached or showed someone else
level: skilled = diagnosis, rebuild, set-up to a standard, a real incident, or leading others; routine = checks, cleaning, topping up, reading a gauge, a drill, a log line.
caveat: short text if the entry is ambiguous (voltage not stated, drill not live, method unclear), else "".
Rules: an entry that is stores, returns, drainage, housekeeping or weather with no requirement gets []. Entries about another person's conduct, fitness or welfare get [] (do not label them). Prefer under-labelling to over-labelling. If unsure whether the writer did it or only witnessed it, use attended.
Return ONLY a JSON object mapping template_id to a list of labels."""
def call(client,batch):
    key=hashlib.sha1(json.dumps(batch).encode()).hexdigest(); p=(OUT/'llm_cache')/f'{key}.json'
    if p.exists(): return json.loads(p.read_text())
    msg=client.messages.create(model=MODEL,max_tokens=8000,system=SYSTEM,
        messages=[{'role':'user','content':json.dumps([{'template_id':t['template_id'],'entry':t['example']} for t in batch])}])
    p.parent.mkdir(exist_ok=True); p.write_text(msg.content[0].text); return json.loads(msg.content[0].text)
def validate(raw):
    """Closed vocabularies enforced in code; anything off-list is dropped, not repaired."""
    out=[]
    for l in raw or []:
        if l.get('req') in REQ_IDS and l.get('role') in ROLES and l.get('level') in LEVELS:
            out.append(dict(req=l['req'],role=l['role'],level=l['level'],caveat=str(l.get('caveat',''))[:80]))
    return out
def parse(text):
    return json.loads(re.sub(r'^```(?:json)?|```$','',text.strip(),flags=re.M).strip())
if __name__=='__main__':
    import anthropic; client=anthropic.Anthropic()
    T=json.load(open(OUT/'templates.json')); labels={}
    for i in range(0,len(T),BATCH):
        b=T[i:i+BATCH]; res=call(client,b)
        if isinstance(res,str): res=parse(res)
        for t in b: labels[t['template_id']]=dict(labels=validate(res.get(t['template_id'])),sensitive=False)
    json.dump(labels,open(OUT/'labels_llm.json','w'),indent=1); print('wrote labels_llm.json')

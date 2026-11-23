"""Builds overview/index.html: one self-contained page that holds the whole submission.
Numbers come from outputs/facts.json; prose comes from docs/*.md; links come from overview/config.json."""
import json, re, html
from config import ROOT, OUT
CFG=json.load(open(ROOT/'overview'/'config.json')); F=json.load(open(OUT/'facts.json'))
def inline(t):
    t=html.escape(t,quote=False)
    t=re.sub(r'`([^`]+)`',r'<code>\1</code>',t)
    t=re.sub(r'\*\*([^*]+)\*\*',r'<b>\1</b>',t)
    t=re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)',r'<i>\1</i>',t)
    t=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'<a href="\2">\1</a>',t)
    return t
def md(text,skip_h1=True,hlevel=3):
    out=[];lines=text.split('\n');i=0
    while i<len(lines):
        l=lines[i]
        if not l.strip(): i+=1; continue
        m=re.match(r'^(#+) (.*)',l)
        if m:
            lvl=len(m.group(1))
            if not(lvl==1 and skip_h1): out.append(f'<h{hlevel}>{inline(m.group(2))}</h{hlevel}>')
            i+=1; continue
        if l.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].startswith('|'):
                if not re.match(r'^\|[\s\-|]+\|$',lines[i]): rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i+=1
            t='<div class="tw"><table><thead><tr>'+''.join(f'<th>{inline(c)}</th>' for c in rows[0])+'</tr></thead><tbody>'
            for r in rows[1:]: t+='<tr>'+''.join(f'<td>{inline(c)}</td>' for c in r)+'</tr>'
            out.append(t+'</tbody></table></div>'); continue
        m=re.match(r'^(\d+)\. ',l)
        if m or l.startswith('- '):
            tag='ol' if m else 'ul'; items=[]
            while i<len(lines) and (re.match(r'^\d+\. ',lines[i]) if m else lines[i].startswith('- ')):
                items.append(re.sub(r'^(\d+\. |- )','',lines[i])); i+=1
            out.append(f'<{tag}>'+''.join(f'<li>{inline(x)}</li>' for x in items)+f'</{tag}>'); continue
        para=[l]; i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r'^(#|\||- |\d+\. )',lines[i]): para.append(lines[i]); i+=1
        out.append(f'<p>{inline(" ".join(para))}</p>')
    return '\n'.join(out)
doc=lambda n:(ROOT/'docs'/n).read_text()
repo=CFG['repo_url'].rstrip('/'); proto=CFG['prototype_url']
def rlink(path,label):
    return f'<a href="{repo}/blob/main/{path}">{label}</a>' if repo and path else f'<a href="{repo}">{label}</a>' if repo else f'<span class="soon">{label} (link added when shared)</span>'
hours=f"Time spent: about {CFG['hours']} hours." if CFG['hours'] else 'Time spent: <span class="soon">to be added</span>.'
call=doc('the-call.md').replace('Time spent: **[N hours: fill in]**.','')
page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Carrowmore: can a lighthouse keeper recognise what the logbooks say about them? The whole submission on one page.">
<title>Carrowmore: the submission on one page</title>
<style>
:root{{--p:#440099;--p2:#6b2fc4;--pl:#f1ebfa;--ink:#1d1a24;--mut:#615b6d;--line:#e3dfea;--bg:#faf9fc;--warn:#6b4300;--warnb:#fdf1dc}}
*{{box-sizing:border-box}}body{{margin:0;font:16px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;color:var(--ink);background:var(--bg)}}
header{{background:var(--p);color:#fff;padding:34px 24px 30px}}.w{{max-width:920px;margin:0 auto}}
header .k{{font-size:13px;letter-spacing:.06em;text-transform:uppercase;opacity:.8}}header h1{{margin:6px 0 8px;font-size:32px;line-height:1.2}}header p{{margin:0;max-width:640px;opacity:.92}}
main{{max-width:920px;margin:0 auto;padding:8px 24px 70px}}h2{{font-size:22px;margin:38px 0 6px;color:var(--p)}}h3{{font-size:17px;margin:20px 0 4px}}
.verdict{{background:#fff;border:1px solid var(--line);border-left:6px solid var(--p);border-radius:10px;padding:16px 20px;margin-top:-22px;box-shadow:0 2px 10px rgba(68,0,153,.08)}}
.verdict b.big{{font-size:20px;color:var(--p)}}.verdict p{{margin:6px 0 0}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:18px 0}}
.stat{{background:#fff;border:1px solid var(--line);border-radius:10px;padding:14px 16px}}.stat .n{{font-size:28px;font-weight:700;color:var(--p);line-height:1.1}}.stat .t{{font-size:14px;color:var(--mut);margin-top:6px}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:12px}}
.card{{background:#fff;border:1px solid var(--line);border-radius:10px;padding:14px 16px}}.card h3{{margin:0 0 4px}}.card p{{margin:0;font-size:15px;color:var(--mut)}}.card .go{{display:inline-block;margin-top:8px;font-weight:600}}
.try{{background:var(--pl);border-radius:10px;padding:14px 20px}}.try ol{{margin:6px 0 0;padding-left:20px}}
.note{{background:var(--warnb);border:1px solid #f0d9a8;color:var(--warn);border-radius:10px;padding:12px 16px;font-size:15px}}
details{{background:#fff;border:1px solid var(--line);border-radius:10px;margin:12px 0;padding:0 18px}}summary{{cursor:pointer;font-weight:600;font-size:18px;padding:14px 0;color:var(--p)}}details[open] summary{{border-bottom:1px solid var(--line);margin-bottom:6px}}
details h3{{color:var(--ink)}}details p,details li{{font-size:16px}}a{{color:var(--p2)}}code{{background:var(--pl);padding:1px 5px;border-radius:4px;font-size:.92em}}
.tw{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;font-size:14.5px;margin:10px 0}}th,td{{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}}th{{background:var(--pl)}}
.soon{{color:var(--mut);font-style:italic}}footer{{color:var(--mut);font-size:14px;margin-top:30px;border-top:1px solid var(--line);padding-top:14px}}
@media(max-width:600px){{header h1{{font-size:26px}}}}
</style></head><body>
<header><div class="w"><div class="k">Senior Product Manager, Zero to One · practical exercise</div>
<h1>Can a lighthouse keeper recognise what the logbooks say about them?</h1>
<p>Carrowmore: 340 keepers, forty years of logbooks and no competence record. This page holds the whole submission: the bet, the prototype built to test it, the call, and what has not been shown.</p></div></header>
<main>
<div class="verdict"><b class="big">The call: persevere, narrowly. Not validated.</b>
<p>The cheapest test did not kill the bet, and it showed what to measure next. I would not build the employer shortlist yet. The bet dies if 10% or more of the claims marked "evidenced" turn out to be wrong when an independent reader checks them.</p></div>

<h2>What the work found</h2>
<div class="stats">
<div class="stat"><div class="n">{F["naive"]} → {F["handson"]}</div><div class="t">A keyword search for HV work flags {F["naive"]} of {F["keepers"]} keepers. Reading <i>role</i> finds {F["handson"]} with hands-on entries. {F["naive_fp"]} of the {F["naive"]} only held keys, signed permits, witnessed or stood by.</div></div>
<div class="stat"><div class="n">{F["sens"]["survive_strict"]} of {F["sens"]["evidenced_recent"]}</div><div class="t">Recent "evidenced" claims in ticket-gated areas that survive much stricter cut-offs. {F["sens"]["margin"]} sit near the margin.</div></div>
<div class="stat"><div class="n">{F["hv"].get("ready_on_record",0)} of {F["keepers"]}</div><div class="t">Keepers ready on record for HV switching: recent hands-on evidence and a current ticket. {F["hv"].get("experience_no_current_ticket",0)} more have the experience but no current ticket.</div></div>
<div class="stat"><div class="n">{F["bands"].get("one_module_away",0)}</div><div class="t">Keeper-scheme pairs one module from complete. {F["miss"].get("attended_not_completed",0)} missing modules were attended but never finished. Tickets, not experience, are the constraint.</div></div>
</div>

<h2>Where to look</h2>
<div class="cards">
<div class="card"><h3>1. The prototype</h3><p>Open this first. A keeper view (with Yes / Partly / No feedback on every claim), an employer view, and an evidence tab that tallies the answers.</p><a class="go" href="{proto}">Open the prototype (Pearson sign-in) →</a><br><a class="go" href="../app/index.html" style="font-weight:500">or open the copy in this repository →</a></div>
<div class="card"><h3>2. The framing</h3><p>One page: whose problem, what I believe but can't prove, and the belief that would sink it.</p><a class="go" href="#framing">Read below ↓</a></div>
<div class="card"><h3>3. The call</h3><p>What I tested, what it did not show, what would change my mind, and what surprised me.</p><a class="go" href="#call">Read below ↓</a></div>
<div class="card"><h3>4. The evidence test</h3><p>How to run a feedback session on the prototype, and how to read the result.</p><span class="go">{rlink("docs/evidence-test.md","Evidence test guide")}</span></div>
<div class="card"><h3>5. The repository</h3><p>Pipeline, outputs, validation tools and this page. Rebuilds in one command from the clean data.</p><span class="go">{rlink("","Open the repository")}</span></div>
</div>

<h2>Five minutes in the prototype</h2>
<div class="try"><ol>
<li><b>Keeper view</b>: pick anyone and open an amber "around it, not doing it" card. Click <i>Show the entries</i> to see what the logbook does and doesn't say.</li>
<li><b>Employer view</b>: switch between the role profiles. Candidates are grouped with reasons, not scored. Open one to see the "check at interview" notes.</li>
<li><b>Evidence</b>: answer a few Yes / Partly / No questions and watch the tally and wrong rate update.</li></ol></div>

<h2>What it has not shown</h2>
<div class="note">No keeper has reacted yet. The labels were written by Claude and are not independently checked. The clean data has had the hard problems removed, so these numbers are an upper bound for the raw pack. The role profiles are my drafts, not the real postings.</div>

<h2 id="framing">The framing</h2>
<details open><summary>Whose problem, and the bet</summary>{md(doc("framing.md"))}</details>

<h2 id="call">The call</h2>
<details open><summary>What I tested, what it did not show, what would change my mind</summary>{md(call)}</details>

<footer>{hours} All data is synthetic: Carrowmore does not exist. Appraisals, station-manager notes, dates of birth and payroll references were deliberately not used.</footer>
</main></body></html>'''
(ROOT/'overview'/'index.html').write_text(page); print('overview/index.html',len(page)//1024,'KB')

#!/usr/bin/env python3
"""Rebuilds everything from data/clean/{keepers.json, logbook_entries.json}. Works on Windows, Mac and Linux.
No API key and no extra packages needed.   Usage:  python run_all.py"""
import subprocess, sys, pathlib, os
ROOT=pathlib.Path(__file__).resolve().parent; SRC=ROOT/'src'
DATA=pathlib.Path(os.environ.get('CARROWMORE_DATA',ROOT/'data'/'clean'))
need=[DATA/'keepers.json',DATA/'logbook_entries.json']
missing=[p.name for p in need if not p.exists()]
if missing:
    sys.exit(f"""
Missing: {', '.join(missing)}
Copy keepers.json and logbook_entries.json from the Carrowmore pack's clean/ folder into:
    {DATA}
then run  python run_all.py  again.
(You do not need them just to view the prototype: open app/index.html in a browser.)""")
steps=['templates.py','requirements.py','rules_baseline.py','tiers.py','distance.py','sensitivity.py','make_gold_sheet.py','build_app.py','build_overview.py']
for s in steps:
    print(f'-> {s}',flush=True)
    r=subprocess.run([sys.executable,s],cwd=SRC,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    if r.returncode: sys.exit(f'{s} failed:\n{r.stdout[-1500:]}')
    if s in('rules_baseline.py','distance.py','sensitivity.py'): (ROOT/'outputs'/(s[:-3]+'.log')).write_text(r.stdout)
print('\nDone. Open app/index.html (prototype) or overview/index.html (overview page).')

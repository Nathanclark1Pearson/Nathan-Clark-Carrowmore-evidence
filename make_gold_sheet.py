"""Blind validation sheet: ~60 templates for YOU to label before looking at anyone's labels.
Fill `your_labels` as  REQ:role:level ; REQ:role:level   (blank = nothing relevant)."""
from config import DATA,OUT,APP
import json, csv, random, re
random.seed(7); T=json.load(open(OUT/'templates.json')); B=json.load(open(OUT/'labels_baseline.json'))
GATED=re.compile(r'permit|keys|earth|switch|isolat|stand by|stood by|witness|confined|tank entry|rescue|abseil|rope|marshall|survival|lift',re.I)
hard=[t for t in T if GATED.search(t['template'])]; rest=[t for t in T if t not in hard]
pick=random.sample(hard,min(30,len(hard)))+random.sample(rest,30)
random.shuffle(pick)
with open(OUT/'gold_sheet.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['template_id','example_entry','times_seen','your_labels'])
    for t in pick: w.writerow([t['template_id'],t['example'],t['count'],''])
print(len(pick),'rows -> gold_sheet.csv')

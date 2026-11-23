"""STAGE A (offline baseline): label each unique template with
   requirement x role x level (+caveat).  Hand-written by reading all 530 templates.
   roles : performed | directed | attended | custody | taught
           (only performed/directed ever count as evidence of doing; the rest is shown as context)
   level : skilled | routine
   Same output schema as extract_llm.py so the two can be diffed."""
from config import DATA,OUT,APP
import json, re
P,D,A,C,T='performed','directed','attended','custody','taught'
S,R='skilled','routine'
def L(req,role,lvl,cav=''): return (req,role,lvl,cav)
RULES=[
# ---- HV ----
(r'^Carried out switching to release',[L('HV_SWITCH',P,S)]),
(r'^Switched the ring to the alternative feed',[L('HV_SWITCH',P,S)]),
(r'^Earthed off both ends of the sub-sea feed',[L('HV_SWITCH',P,S)]),
(r'^Restored the HV after the contractor cleared',[L('HV_SWITCH',P,S)]),
(r'^Took the NkV board off, worked the sequence myself',[L('HV_SWITCH',P,S)]),
(r'^Isolated no\.N transformer, earths applied both ends, PERMIT issued',[L('HV_SWITCH',P,S),L('HV_PERMIT',D,S)]),
(r'^Racked out no\.N breaker, locked off',[L('HV_SWITCH',P,S,'voltage not stated')]),
(r'^Authorised the switching programme',[L('HV_PERMIT',D,S)]),
(r'^Acted as issuing authority',[L('HV_PERMIT',D,S)]),
(r'^Issued PERMIT to the contractor',[L('HV_PERMIT',D,S)]),
(r'^Refused to sign PERMIT back',[L('HV_PERMIT',D,S)]),
(r'^Witnessed earths applied',[L('HV_SWITCH',A,S,'present while someone else did it')]),
(r'^Stood by while .* switched the no\.N transformer out',[L('HV_SWITCH',A,S,'present while someone else did it')]),
(r'^Held the keys for the HV work',[L('HV_SWITCH',C,R,'held keys only')]),
(r'^HV room locked and keys signed back in',[L('HV_SWITCH',C,R,'held keys only')]),
(r'^Signed on to PERMIT',[L('HV_SWITCH',C,R,'worked under a permit')]),
(r'^Read the permit conditions',[L('HV_SWITCH',C,R,'permit recipient')]),
(r'^Permit returned and cancelled',[L('HV_SWITCH',C,R,'permit returned')]),
# ---- LV / electrical ----
(r'^Traced an intermittent|^Traced and lifted an earth fault|^Sat through the night to catch the earth fault|^Worked the fault down by halving|^Fault only showed when|^Contractor could not find it|^Traced the nuisance low-volt',[L('ELEC_FAULT',P,S)]),
(r'^Checked continuity on the run|^Alarm bell sounding, traced to a loose wire|^Intermittent fault on the gallery lights',[L('ELEC_FAULT',P,R)]),
(r'^Megger test|^Rewired the changeover|^Reconfigured distribution|^Rebuilt the changeover logic|^Discrimination not right|^Re-terminated|^Protection relay settings',[L('LV_DIST',P,S)]),
(r'^Balanced loads|^Changed over main board|^Renewed fuse links|^Reset tripped breaker|^Tightened glands in the cable trunk|^Checked board readings|^Cleaned terminals|^Cleaned the contacts in the changeover|^Checked the feeder run|^Lamp circuit off at the board',[L('LV_DIST',P,R)]),
(r'^Renewed N cells|^Charger float voltage|^Load-tested the standby bank|^Full capacity discharge|^Traced the nuisance low-volt',[L('BATT_DC',P,S)]),
(r'^SGs taken across|^Topped up cells|^Battery checked on the beacon|^Battery room vented|^Charger on boost',[L('BATT_DC',P,R)]),
# ---- plant ----
(r'^Decoke|^Bottom-end knock|^Injectors off|^Set the timing on no\.N|^Governor hunting|^AVR on|^Synchronised|^Set up the auto-start|^Overhauled the raw water|^Bled the fuel system',[L('GEN_PRIME',P,S)]),
(r'^Changed oil and filters|^Ran no\.N set|^Started no\.N set|^Weekly changeover|^Auto start tested|^Topped coolant|^Reset the overspeed|^Engine run up|^Fuel transferred',[L('GEN_PRIME',P,R)]),
(r'^Fuel transfer by hose in a swell',[L('GEN_PRIME',P,S)]),
(r'^Rebuilt the no\.N pump|^Pump losing prime|^Mechanical seal gone|^Reseal on the no\.N ram|^Flushed the whole system|^System running hot|^Made up a new hose|^Set up a duty/standby',[L('PUMP_HYD',P,S)]),
(r'^Repacked the gland|^Checked for weeps|^Primed the no\.N pump|^Cleared a blockage in the suction|^Filter changed on the power pack|^Topped the hydraulic|^Ran the sump pump|^Cleared the yard drain',[L('PUMP_HYD',P,R)]),
(r'^Brake band relined|^Gearbox stripped|^Repaired the derrick luffing|^Renewed the winch wire',[L('PLANNED_MAINT',P,S)]),
(r'^Ran the overhaul party|^Wrote up the running hours',[L('PLANNED_MAINT',D,S)]),
(r'^Quarterly inspection|^Greased the winch|^Winch brake adjusted|^Greased the derrick|^Greased the exposed',[L('PLANNED_MAINT',P,R)]),
# ---- height / rope / rescue ----
(r'^Set up the fall arrest|^Worked the mast head|^Rigged staging round the lantern',[L('WORK_HEIGHT',P,S)]),
(r'^Harness and lanyard|^Up the ladder to the gallery|^Checked the anchor points|^Ropes inspected|^Cleaned the lantern glass from the staging',[L('WORK_HEIGHT',P,R)]),
(r'^Abseil inspection|^Roped access|^Rigged a rebelay',[L('ROPE_ACCESS',P,S)]),
(r'^Descended to the mid-course',[L('ROPE_ACCESS',P,R,'method not stated')]),
(r'^Practised a pick-off rescue',[L('TOWER_RESCUE',P,S,'drill, not a live rescue')]),
(r'^Recovered .* from the cable duct',[L('TOWER_RESCUE',P,S),L('CONFINED',P,S)]),
# ---- confined space ----
(r'^Confined space entry|^Confined space work|^Entered the water tank|^Second confined space|^Tank entry',[L('CONFINED',P,S)]),
(r'^Gas tested the fuel tank|^Ventilated the cellar',[L('CONFINED',P,R)]),
(r'^Acted as top man|^Rescue kit rigged',[L('CONFINED',A,S,'standby/attendant role')]),
# ---- OSSC ----
(r'^Treated .* for a crush|^Hypothermia case|^Immobilised a back injury|^Managed a suspected heart',[L('FIRST_AID',P,S)]),
(r'^Dressed a cut hand',[L('FIRST_AID',P,R)]),
(r'^Casualty bag|^First aid box',[L('FIRST_AID',P,R)]),
(r'^Engine room fire|^Overhauled the foam installation',[L('FIRE',P,S)]),
(r'^Ran the fire drill as a real scenario',[L('FIRE',D,S)]),
(r'^Fire drill held|^Ran through the fire drill|^Fire alarm tested|^Extinguishers checked|^Hose reels|^Evacuation route',[L('FIRE',P,R)]),
(r'^Ran the annual survival drill',[L('SEA_SURVIVAL',P,S,'drill')]),
(r'^Survival drill with|^Immersion suits|^Lifejackets|^Liferaft service',[L('SEA_SURVIVAL',P,R)]),
(r'^Briefed the new supernumerary on survival kit',[L('SEA_SURVIVAL',T,R)]),
(r'^Marshalled the relief aircraft|^Talked the pilot in|^Ran the deck for N lifts',[L('HELI_OPS',P,S)]),
(r'^Briefed the new men on pad discipline|^Ran the muster and got N off the rock by helicopter',[L('HELI_OPS',D,S)]),
(r'^Helipad swept|^Pad lighting tested',[L('HELI_OPS',P,R)]),
(r'^Stood by for the aircraft',[L('HELI_OPS',A,R)]),
# ---- marine ----
(r'^Coxed for the relief|^Landed the relief|^Landing in the dark|^Ran the boat off the rock|^Took the boat through the sound|^Recovered a broken-down punt|^Got four men and stores ashore|^Judged the sea wrong',[L('BOAT',P,S)]),
(r'^Boat away to the landing|^Took the punt round|^Landing attempted, abandoned|^Landing party rigged|^Boat hauled up',[L('BOAT',P,R)]),
(r'^Reported the landing as unsafe',[L('BOAT',D,S)]),
(r'^Stood by at the landing',[L('BOAT',A,R)]),
(r'^Laid a new ground chain|^Mooring dragged in the gale',[L('MOORING',P,S)]),
(r'^Renewed a shackle on the boat mooring|^Mooring chain inspected|^Moorings checked|^Buoy recovered',[L('MOORING',P,R)]),
(r'^Took the boat through the sound in poor vis',[L('NAVIGATION',P,S)]),
(r'^Checked the AIS position against the chart',[L('NAVIGATION',P,R)]),
(r'^Acted as on-scene reporting point|^Worked out a search pattern',[L('SEARCH_COORD',D,S)]),
(r'^Handled N stations at once during the search',[L('SEARCH_COORD',P,S),L('RADIO_OPS',P,S)]),
(r'^Held the search log|^Kept a full timeline of the incident',[L('SEARCH_COORD',P,S)]),
(r'^Kept a lookout for the missing boat|^Logged the search traffic',[L('SEARCH_COORD',P,R)]),
# ---- radio / met ----
(r'^Heard the mayday first|^Copied a distress|^Worked a poor-range casualty|^Handled a live DSC|^Held the distress watch|^Coordinated the relay|^Ran comms for the lift',[L('RADIO_OPS',P,S)]),
(r'^Passed the weather by VHF|^Radio check|^Scheduled call|^Routine MF sched|^Distress watch kept|^MF watch kept|^DSC watch|^DSC test call|^Cleared a false DSC|^Logged a mayday|^Logged the silence|^Nothing heard on the distress|^Worked (MFV|MV|tender|local|the relief)|^Reported a flare',[L('RADIO_OPS',P,R)]),
(r'^Kept hourly obs through the storm|^Instrument screen|^Queried our own obs',[L('MET_OBS',P,S)]),
(r'^Ob taken|^Wind .*Passed|^Sea state|^Bar N',[L('MET_OBS',P,R)]),
(r'^Trained .* on the observing code',[L('MET_OBS',T,S),L('SUPERVISION',T,S)]),
(r'^Reprogrammed the DSC|^Tuned the aerial|^MF transmitter down|^Set up the standby transmitter|^Found the receiver desensitised|^Antenna feeder|^Rebuilt the aerial mast|^Earth mat for the MF|^AIS transmitting a wrong|^Aton reporting intermittently|^Configured the synthetic aton|^Set up the telemetry link|^Traced repeated false alerts|^Racon not triggering|^Set up the new beacon|^Fog detector cutting in late',[L('RADIO_EQUIP',P,S)]),
(r'^Aerial inspected|^MF set checked|^Changed the battery in the portable|^MMSI checked|^AIS reset|^AIS unit reporting|^Aton message confirmed|^Racon (checked|coding|reset)',[L('RADIO_EQUIP',P,R)]),
# ---- ATON ----
(r'^Lamp changer stepping twice|^Set up the new lamp focus|^Aligned the no\.N panel|^Stripped and cleaned the mercury|^Rebuilt the clockwork|^Drive motor brushes',[L('OPTICAL',P,S)]),
(r'^Lamp changed|^Lamp not lit|^Changer tested|^Mercury bath checked|^Rotation checked|^Lens panels|^Lantern glass cleaned|^Wick trimmed|^Cleaned the lantern',[L('OPTICAL',P,R)]),
(r'^Showed .* the lamp changer',[L('OPTICAL',T,R),L('SUPERVISION',T,R)]),
(r'^Character found N sec out|^Coding wheel|^Set the timing gear on the signal|^Set the new flasher unit',[L('SIGNAL_CHAR',P,S)]),
(r'^Character (checked|confirmed)|^Occulting timing|^Timed the flashes',[L('SIGNAL_CHAR',P,R)]),
(r'^Diaphone piston|^Compressor not making pressure|^Emitter horn',[L('AUDIBLE',P,S)]),
(r'^Diaphone tested|^Compressor run up|^Greased the compressor|^Fog signal in operation|^Signal secured',[L('AUDIBLE',P,R)]),
# ---- fabric ----
(r'^Cut out and rebuilt N courses|^Made up a mix to match|^Stripped failed cement render|^Repaired the storm damage to the landing wall',[L('MASONRY',P,S)]),
(r'^Pointing made good|^Mixed mortar|^Raked out the joints|^Rendered the patch',[L('MASONRY',P,R)]),
(r'^Needle-gunned|^Specified and applied a two-pack|^Surface prep argued|^Renewed the sacrificial anodes|^Traced bimetallic corrosion',[L('COATINGS',P,S)]),
(r'^Ran the whole tower repaint|^Wrote the method for the tower repaint',[L('COATINGS',D,S),L('SUPERVISION',D,S)]),
(r'^Painted the|^Red lead|^Wire brushed and primed|^Tower whitewashed|^Anodes checked',[L('COATINGS',P,R)]),
(r'^Renewed the glazing bars|^Replaced N lantern panes|^Made a template for the curved pane',[L('GLAZING',P,S)]),
(r'^Cracked pane|^Renewed the putty|^Astragals checked',[L('GLAZING',P,R)]),
(r'^Full condition survey|^Surveyed the|^Produced the dilapidation',[L('CONDITION_SURVEY',P,S)]),
(r'^Noted damage to the boundary|^Noted rust|^Quarterly inspection',[L('CONDITION_SURVEY',P,R)]),
# ---- lifting ----
(r'^Slewed heavy plant|^Load chart worked out|^Set up the haul for a heavy lift|^Made up a new strop|^Renewed the winch wire|^Condemned N strops|^Ran comms for the lift|^Got four men and stores ashore',[L('LIFTING',P,S)]),
(r'^Ran the lifting operation for the lantern panel|^Load tested the winch and the landing gear',[L('LIFTING',D,S)]),
(r'^Hauled up stores with the winch|^Coal and gas taken up|^Derrick used for the relief|^Crane hook and block|^Checked the shackles and strops|^Wire inspected|^Greased the winch|^Greased the derrick',[L('LIFTING',P,R)]),
# ---- people / planning ----
(r'^Took charge of the station|^Ran the overhaul party|^Wrote the safe system|^Reorganised the watch bill|^Assessed N keepers',[L('SUPERVISION',D,S)]),
(r'^Work allocated|^Detailed |^Watch bill made out',[L('SUPERVISION',D,R)]),
(r'^Coached |^Took the supernumerary through the whole plant',[L('SUPERVISION',T,S)]),
(r'^Took .* round the plant',[L('SUPERVISION',T,R)]),
(r'^Rewrote the station evacuation|^Reviewed the station abandon|^Evacuated the station|^Ran the muster',[L('EMERGENCY_PLAN',D,S)]),
(r'^Stood by for evacuation',[L('EMERGENCY_PLAN',A,R)]),
]
# Entries about OTHER people's conduct/fitness. Do not count, do not display.
SENSITIVE=[r'^Had to stand a man down for coming back unfit']
def label_templates(templates):
    out={}
    for t in templates:
        labs=[]; txt=t['template']
        for pat,ls in RULES:
            if re.search(pat,txt,re.I):
                for r,ro,lv,cav in ls:
                    if (r,ro) not in [(x['req'],x['role']) for x in labs]:
                        labs.append(dict(req=r,role=ro,level=lv,caveat=cav))
        sens=any(re.search(p,txt,re.I) for p in SENSITIVE)
        out[t['template_id']]=dict(labels=[] if sens else labs,sensitive=sens)
    return out
if __name__=='__main__':
    T=json.load(open(OUT/'templates.json')); lab=label_templates(T)
    json.dump(lab,open(OUT/'labels_baseline.json','w'),indent=1)
    n=sum(1 for v in lab.values() if v['labels']); e=sum(t['count'] for t in T if lab[t['template_id']]['labels'])
    print(f'{n}/{len(T)} templates labelled; {e}/{sum(t["count"] for t in T)} entries')
    un=[t for t in T if not lab[t['template_id']]['labels']]
    print('UNLABELLED (count desc):')
    for t in sorted(un,key=lambda x:-x['count']): print(t['count'],t['template'][:95], '[SENSITIVE]' if lab[t['template_id']]['sensitive'] else '')

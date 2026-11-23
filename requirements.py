"""Draft requirement list. Each requirement = something an employer asks for.
scheme/modules link it to the certification record. gate=True means an employer/insurer
is likely to need a ticket, not just experience.  DRAFT: I have not seen the Array posting or
certification_schemes.json -> cut/rename this against the real posting before you rely on it."""
from config import DATA,OUT,APP
import json
R=[
# id, label, scheme, modules, gate, description
("HV_SWITCH","HV isolation, switching and earthing (hands-on)","HVAP",["HVAP-01","HVAP-02"],True,"Personally carries out HV switching, isolation, earthing, proving dead, restoration."),
("HV_PERMIT","HV permit issue / switching authority","HVAP",["HVAP-03","HVAP-04"],True,"Issues permits or authorises switching programmes (Authorised Person duties)."),
("ELEC_FAULT","Electrical fault-finding","MECS",["MECS-3"],False,"Diagnoses intermittent / earth / cable faults with instruments."),
("LV_DIST","LV distribution, protection and testing","MECS",["MECS-1","MECS-5"],False,"Rewires, re-terminates, tests insulation, sets protection."),
("BATT_DC","Batteries and DC systems","MECS",["MECS-4"],False,"Cell replacement, load testing, charger setting."),
("GEN_PRIME","Generator and prime mover maintenance","MPMC",["MPMC-A","MECS-2"],False,"Diesel overhaul, governor/AVR, synchronising, auto-start."),
("PUMP_HYD","Pumped and hydraulic systems","MPMC",["MPMC-B","MPMC-C"],False,"Pump rebuilds, rams, seals, relief valves."),
("PLANNED_MAINT","Mechanical repair and planned maintenance","MPMC",["MPMC-D"],False,"Plant repairs, maintenance schedules, running an overhaul."),
("WORK_HEIGHT","Working at height","WAHS",["WAHS-1","WAHS-2"],True,"Fall arrest, mast/tower work, staging."),
("ROPE_ACCESS","Rope access","WAHS",["WAHS-3"],True,"Abseil/rope work, rebelays."),
("TOWER_RESCUE","Tower rescue and casualty recovery","WAHS",["WAHS-4"],True,"Rescue from height/duct (practice or real)."),
("CONFINED","Confined space entry and standby","OSSC",["OSSC-CS"],True,"Tank/duct entry, gas testing, top-man, rescue kit."),
("FIRST_AID","First aid and casualty care","OSSC",["OSSC-FA"],True,"Treats injuries and illness, hands over casualties."),
("FIRE","Fire prevention and response","OSSC",["OSSC-FF"],True,"Real fires, drills, fire plant."),
("SEA_SURVIVAL","Sea survival","OSSC",["OSSC-SS"],True,"Survival drills, suits, rafts."),
("HELI_OPS","Helicopter landing area operations","OSSC",["OSSC-HL"],True,"Marshalling, pad ops, helicopter evacuation."),
("BOAT","Small boat handling","SMOC",["SMOC-BH"],True,"Coxing, landings in swell, tow and recovery."),
("MOORING","Mooring and anchor work","SMOC",["SMOC-MO"],False,"Laying and recovering moorings."),
("NAVIGATION","Coastal navigation and pilotage","SMOC",["SMOC-NV"],False,"Passage in poor visibility."),
("SEARCH_COORD","Search and on-scene coordination","SMOC",["SMOC-SR"],False,"Search patterns, on-scene reporting, search logs."),
("RADIO_OPS","Radio operation and distress handling","RCOM",["RCOM-GEN","RCOM-DSC"],False,"VHF/MF/DSC distress, relays, multi-station handling."),
("MET_OBS","Meteorological observing","RCOM",["RCOM-MET"],False,"Observations, instrument siting and checks."),
("RADIO_EQUIP","Radio and electronic equipment maintenance","RCOM",["RCOM-AT","ANSM-E"],False,"Aerials, transmitters, AIS, racon, telemetry faults."),
("OPTICAL","Optical apparatus and light sources","ANSM",["ANSM-O"],False,"Lamp changer, lens, mercury bath, clockwork."),
("SIGNAL_CHAR","Signal character and timing","ANSM",["ANSM-C"],False,"Flasher/timing gear to published character."),
("AUDIBLE","Audible signals and compressed air","ANSM",["ANSM-A"],False,"Diaphone, horn, compressor plant."),
("MASONRY","Masonry, render and pointing","SFAB",["SFAB-M"],False,"Lime mortar, rebuilds, render."),
("COATINGS","Surface preparation and coatings","SFAB",["SFAB-C"],False,"Prep, specified systems, corrosion control."),
("GLAZING","Glazing and weatherproofing","SFAB",["SFAB-G"],False,"Pane/bar replacement."),
("CONDITION_SURVEY","Condition inspection and reporting","SFAB",["SFAB-I"],False,"Surveys, defect schedules."),
("LIFTING","Lifting operations","LOSC",["LOSC-A","LOSC-P","LOSC-S"],True,"Operating appliances, planning lifts, slinging, signalling, lifting-gear inspection."),
("SUPERVISION","Supervising, training and assessing others","",[],False,"Leads parties, writes safe systems/methods, trains or assesses others (no ticket)."),
("EMERGENCY_PLAN","Emergency planning and incident leadership","",[],False,"Evacuation plans, taking charge in incidents (no ticket)."),
]
REQS=[dict(id=a,label=b,scheme=c,modules=d,gate=e,description=f) for a,b,c,d,e,f in R]
if __name__=='__main__':
    json.dump(REQS,open(OUT/'requirements.json','w'),indent=1); print(len(REQS),'requirements')

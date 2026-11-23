import os, pathlib
ROOT=pathlib.Path(__file__).resolve().parent.parent
DATA=pathlib.Path(os.environ.get("CARROWMORE_DATA",ROOT/"data"/"clean"))   # keepers.json, logbook_entries.json
OUT=ROOT/"outputs"; APP=ROOT/"app"
OUT.mkdir(exist_ok=True); APP.mkdir(exist_ok=True)

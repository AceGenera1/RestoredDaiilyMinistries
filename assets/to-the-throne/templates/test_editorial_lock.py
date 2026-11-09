#!/usr/bin/env python3
"""Guard against the precise mistakes from TTT-0003 visual production."""
import copy,json
from editorial_lock import FIXTURE,check,validate_renderer_payload
canonical=json.loads(FIXTURE.read_text(encoding="utf-8"))
def must_fail(mutated):
    try:check(mutated,canonical)
    except ValueError:return
    raise AssertionError("Unsafe weekly matter was accepted")
assert check(canonical,canonical)["passed"]
for field,value in (("edition","TTT-0001"),("week_of","2026-10-26"),
                    ("mandatory_closing","These are five situations."),
                    ("closing_tagline","")):
    changed=copy.deepcopy(canonical);changed[field]=value;must_fail(changed)
changed=copy.deepcopy(canonical);changed["matters"][0]["location"]="Abyei";must_fail(changed)
changed=copy.deepcopy(canonical);changed["matters"][0]["id"]="amiet-market";must_fail(changed)
changed=copy.deepcopy(canonical);changed["matters"][2]["scripture_text"]="Shortened";must_fail(changed)
changed=copy.deepcopy(canonical);changed["matters"][1]["prayer_focus"]=[];must_fail(changed)
changed=copy.deepcopy(canonical);changed["matters"].reverse();must_fail(changed)
changed=copy.deepcopy(canonical);changed["matters"][3]["factual_core"]="New flood";must_fail(changed)
changed=copy.deepcopy(canonical);changed["mandatory_closing"]+=" Extra";must_fail(changed)
payload={"edition":canonical["edition"],"matters":[
  {"location":m["location"],"heading":m["headline"],"scripture":{
   "reference":m["scripture_reference"],"text":m["scripture_text"]}}
  for m in canonical["matters"]],
 "closing":canonical["mandatory_closing"],"approved":False,"publication_authorized":False}
assert validate_renderer_payload(canonical,payload)
bad=copy.deepcopy(payload);bad["matters"][0]["location"]="TAIZ"
try:validate_renderer_payload(canonical,bad)
except ValueError:pass
else:raise AssertionError("Legacy place in renderer accepted")
bad=copy.deepcopy(payload);bad["closing"]="Summary only"
try:validate_renderer_payload(canonical,bad)
except ValueError:pass
else:raise AssertionError("Truncated closing accepted")
print("PASS: 14 negative controls and canonical renderer handshake; zero publication.")

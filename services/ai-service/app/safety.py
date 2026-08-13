import re
SAFETY_PATTERNS={
 "FIRE_OR_SMOKE":r"\b(fire|flames?|smoke|fire alarm (?:is )?(?:failed|failure|not working))\b",
 "GAS_LEAK":r"\b(gas leak|smell of gas|gas escaping)\b",
 "ELECTRICAL_DANGER":r"\b(exposed (?:electrical )?wir(?:e|es|ing)|live wire|electric shock|sparking cable)\b",
 "VIOLENCE_OR_WEAPON":r"\b(weapon|gun|knife attack|violence|violent threat|assault)\b",
 "STRUCTURAL_DANGER":r"\b(structural collapse|building collapse|ceiling (?:is )?collapsing|wall (?:is )?collapsing)\b",
 "SERIOUS_SECURITY":r"\b(armed intruder|active shooter|serious security incident)\b",
}
def critical_rule(text:str)->str|None:
 normalized=" ".join(text.lower().split())
 for name,pattern in SAFETY_PATTERNS.items():
  if re.search(pattern,normalized,re.IGNORECASE):return name
 return None

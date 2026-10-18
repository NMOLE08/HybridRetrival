"""Extract explicitly written CVE and ESP32 identifiers, preserving spans."""
from __future__ import annotations
from dataclasses import dataclass, asdict
import re
from .normalization import normalize_dashes

# Avoid fallback to generic ESP32 when a hyphenated model is malformed.
_PATTERN = re.compile(r"(?<![A-Za-z0-9])(?:CVE[ \t]*-[ \t]*[0-9]{4}[ \t]*-[ \t]*[0-9]{4,}(?![A-Za-z0-9])|ESP32(?:[ \t]*-[ \t]*[CSHP][0-9]{1,2}(?![A-Za-z0-9])|(?![A-Za-z0-9]|[ \t]*-[ \t]*[A-Za-z0-9])))", re.IGNORECASE)

@dataclass(frozen=True)
class Identifier:
    canonical: str
    family: str
    variant: str | None
    start: int
    end: int
    source: str

    def to_dict(self): return asdict(self)


def extract_identifiers(text):
    if not isinstance(text,str): raise TypeError("text must be a string")
    normalized = normalize_dashes(text)
    found=[]; seen=set()
    for match in _PATTERN.finditer(normalized):
        canonical=re.sub(r"\s+", "", match.group()).upper()
        if canonical in seen: continue
        seen.add(canonical)
        family="cve" if canonical.startswith("CVE-") else "esp32"
        variant=canonical if family == "cve" or canonical != "ESP32" else None
        found.append(Identifier(canonical,family,variant,match.start(),match.end(),text[match.start():match.end()]))
    return found


def conflicts(query_ids, doc_ids):
    """Families where explicit doc variants disagree and none of the requested variants occur.

    Generic ESP32 is not itself a contradictory explicit variant. If any
    requested variant of a family appears in the document, do not penalize
    that family, even if the document also mentions other variants.
    """
    bad=[]
    for family in sorted({x.family for x in query_ids}):
        wanted={x.canonical for x in query_ids if x.family==family and x.variant is not None}
        actual={x.canonical for x in doc_ids if x.family==family and x.variant is not None}
        if wanted and actual and wanted.isdisjoint(actual): bad.append(family)
    return bad

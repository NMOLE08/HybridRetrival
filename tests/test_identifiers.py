from iphr.identifiers import extract_identifiers, conflicts
from iphr.normalization import normalize_text


def ids(text): return [x.canonical for x in extract_identifiers(text)]


def test_supported_identifiers_normalization_and_spans():
    text="See esp32–s3, ESP32-C3, and cve−2024−3094."
    result=extract_identifiers(text)
    assert [x.canonical for x in result] == ["ESP32-S3","ESP32-C3","CVE-2024-3094"]
    assert all(text[x.start:x.end] == x.source for x in result)
    assert normalize_text(" ESP32–S3  ") == "esp32-s3"


def test_no_partial_matches_or_duplicate_ids():
    assert ids("ESP32-S3X CVE-2024-3094A ESP32-C3foo") == []
    assert ids("ESP32-S31; ESP32-S3; ESP32-S3; ESP32") == ["ESP32-S31","ESP32-S3","ESP32"]
    assert ids("CVE-2024-3094 and CVE-2024-3095") == ["CVE-2024-3094","CVE-2024-3095"]
    assert ids("") == []
    assert ids("How do computers learn?") == []


def test_conflicts_are_conservative():
    q=extract_identifiers("ESP32-S3")
    assert conflicts(q,extract_identifiers("ESP32-C3")) == ["esp32"]
    assert conflicts(q,extract_identifiers("ESP32")) == []
    assert conflicts(q,extract_identifiers("ESP32-S3 and ESP32-C3")) == []
    assert conflicts(extract_identifiers("ESP32"),extract_identifiers("ESP32-S3")) == []
    assert conflicts(extract_identifiers("CVE-2024-3094"),extract_identifiers("CVE-2024-3095")) == ["cve"]
    assert conflicts(extract_identifiers("ESP32-S3 ESP32-C3"),extract_identifiers("ESP32-C3")) == []

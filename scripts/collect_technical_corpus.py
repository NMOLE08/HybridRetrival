"""Fetch a small, immutable source-discovery sample; not a labeled benchmark."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

REVISION = "f36061cc9d42937cd6a7a7321a89da7ef625a190"
IDS = (
    "CVE-2024-3094", "CVE-2021-44228", "CVE-2017-0144", "CVE-2023-4863",
    "CVE-2021-45046", "CVE-2021-45105", "CVE-2021-44832", "CVE-2014-0160",
    "CVE-2014-6271", "CVE-2021-34527", "CVE-2022-22965", "CVE-2020-1472",
    "CVE-2019-0708", "CVE-2017-5638", "CVE-2018-11776", "CVE-2023-34362",
    "CVE-2023-23397", "CVE-2021-26855", "CVE-2022-30190", "CVE-2019-19781",
    "CVE-2020-0601",
)
ESP_REVISION = "1c42e514c90ae621af33bde3b6ad3dac22edcbfd"
ESP_CHIPS = ("esp32", "esp32s2", "esp32s3", "esp32c2", "esp32c3", "esp32c5", "esp32c6", "esp32c61", "esp32h2", "esp32p4")
ROOT = Path(__file__).resolve().parents[1]


def source_url(cve_id: str) -> str:
    _, year, number = cve_id.split("-")
    folder = f"{int(number) // 1000}xxx"
    return f"https://raw.githubusercontent.com/CVEProject/cvelistV5/{REVISION}/cves/{year}/{folder}/{cve_id}.json"


def collect() -> list[dict]:
    directory = ROOT / "cache" / "source_discovery"
    directory.mkdir(parents=True, exist_ok=True)
    records = []
    for cve_id in IDS:
        url = source_url(cve_id)
        request = Request(url, headers={"User-Agent": "iphr-research-source-check/0.1"})
        with urlopen(request, timeout=30) as response:
            raw = response.read()
        data = json.loads(raw)
        if data["cveMetadata"]["cveId"] != cve_id or data["cveMetadata"]["state"] != "PUBLISHED":
            raise ValueError(f"Unexpected CVE record: {cve_id}")
        path = directory / f"{cve_id}.json"
        path.write_bytes(raw)
        records.append({"id": cve_id, "url": url, "sha256": hashlib.sha256(raw).hexdigest(), "local_path": f"cache/source_discovery/{cve_id}.json", "rights": "CVE Program terms of use; preserve copyright designation and license when redistributing", "terms_url": "https://www.cve.org/Resources/Media/Archives/OldWebsite/about/termsofuse.html", "status": "source discovery only; not annotated"})
    for chip in ESP_CHIPS:
        url = f"https://raw.githubusercontent.com/espressif/esp-idf/{ESP_REVISION}/components/soc/{chip}/include/soc/soc_caps.h"
        request = Request(url, headers={"User-Agent": "iphr-research-source-check/0.1"})
        with urlopen(request, timeout=30) as response:
            raw = response.read()
        if b"SPDX-License-Identifier: Apache-2.0 OR MIT" not in raw[:500]:
            raise ValueError(f"Unexpected license header: {chip}")
        path = directory / f"{chip}-soc_caps.h"
        path.write_bytes(raw)
        records.append({"id": chip, "url": url, "sha256": hashlib.sha256(raw).hexdigest(), "local_path": f"cache/source_discovery/{chip}-soc_caps.h", "rights": "File header: Apache-2.0 OR MIT; preserve copyright and license notice when redistributing", "terms_url": f"https://github.com/espressif/esp-idf/blob/{ESP_REVISION}/LICENSE", "status": "source discovery only; not annotated"})
    return records


if __name__ == "__main__":
    records = collect()
    path = ROOT / "outputs" / "manifests" / "source_discovery.json"
    path.write_text(json.dumps({"cve_revision": REVISION, "esp_idf_revision": ESP_REVISION, "records": records}, indent=2) + "\n", encoding="utf-8")
    print(f"Fetched and validated {len(records)} public source records; manifest: {path}")

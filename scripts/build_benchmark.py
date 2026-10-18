"""Build the small agent-curated pilot from pinned, cached upstream records.

This creates labels before ranking comparisons. It intentionally does not claim
independent human annotation; see data/technical/annotation_guidelines.md.
"""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "cache/source_discovery"
OUT = ROOT / "data/technical"
MANIFEST = json.loads((ROOT / "outputs/manifests/source_discovery.json").read_text(encoding="utf-8"))
# Query wording, evidence and labeled negatives were authored before any runs.
# A negative pair here is specifically reviewed; unlisted pairs are unjudged.
DEV = [
 ("dev01", "What malicious xz library modification is described by CVE-2024-3094?", "identifier", "cve", "CVE-2024-3094", ["CVE-2021-44228"]),
 ("dev02", "How does CVE-2014-6271 involve Bash environment variables?", "identifier", "cve", "CVE-2014-6271", ["CVE-2014-0160"]),
 ("dev03", "What causes the recursion denial of service in CVE-2021-45105?", "identifier", "cve", "CVE-2021-45105", ["CVE-2021-44228", "CVE-2021-45046", "CVE-2021-44832"]),
 ("dev04", "Which SPI and UART peripheral counts are specified for ESP32-C2?", "identifier", "esp32", "esp32c2", ["esp32c3", "esp32c6"]),
 ("dev05", "Is USB OTG supported by ESP32-S2 according to the capability definitions?", "identifier", "esp32", "esp32s2", ["esp32s3", "esp32p4"]),
 ("dev06", "Which Windows certificate validation flaw can make a malicious executable appear signed by a trusted source?", "natural", "none", "CVE-2020-0601", ["CVE-2020-1472"]),
]
TEST = [
 ("test01", "What JNDI endpoint issue is described by CVE-2021-44228?", "identifier", "cve", "CVE-2021-44228", ["CVE-2021-44832", "CVE-2021-45105"]),
 ("test02", "How can CVE-2014-0160 expose memory through heartbeat packets?", "identifier", "cve", "CVE-2014-0160", ["CVE-2014-6271"]),
 ("test03", "Which file upload parser problem is described by CVE-2017-5638?", "identifier", "cve", "CVE-2017-5638", ["CVE-2018-11776"]),
 ("test04", "What deployment conditions are described for CVE-2022-22965?", "identifier", "cve", "CVE-2022-22965", ["CVE-2017-5638"]),
 ("test05", "What kind of database attack is associated with CVE-2023-34362?", "identifier", "cve", "CVE-2023-34362", ["CVE-2023-4863"]),
 ("test06", "What flaw affects Citrix ADC and Gateway under CVE-2019-19781?", "identifier", "cve", "CVE-2019-19781", ["CVE-2019-0708"]),
 ("test07", "How many GPIO pins are specified for ESP32-S3?", "identifier", "esp32", "esp32s3", ["esp32s2", "esp32c3"]),
 ("test08", "How many CPU cores are specified for ESP32-C3?", "identifier", "esp32", "esp32c3", ["esp32c2", "esp32s3"]),
 ("test09", "Does ESP32-C6 declare 802.15.4 support?", "identifier", "esp32", "esp32c6", ["esp32c5", "esp32c3"]),
 ("test10", "How many UART controllers are defined for ESP32-P4?", "identifier", "esp32", "esp32p4", ["esp32s3", "esp32c6"]),
 ("test11", "Which vulnerability allows unauthenticated remote desktop requests to cause code execution?", "natural", "none", "CVE-2019-0708", ["CVE-2017-0144"]),
 ("test12", "Find the libwebp heap overflow triggered by a crafted HTML page in Chrome.", "natural", "none", "CVE-2023-4863", ["CVE-2023-34362"]),
]
CHIP_NAMES = {"esp32":"ESP32", "esp32c2":"ESP32-C2", "esp32c3":"ESP32-C3", "esp32c5":"ESP32-C5", "esp32c6":"ESP32-C6", "esp32c61":"ESP32-C61", "esp32h2":"ESP32-H2", "esp32p4":"ESP32-P4", "esp32s2":"ESP32-S2", "esp32s3":"ESP32-S3"}
MACROS = ("SOC_BT_SUPPORTED", "SOC_WIFI_SUPPORTED", "SOC_IEEE802154_SUPPORTED", "SOC_USB_OTG_SUPPORTED", "SOC_CPU_CORES_NUM", "SOC_GPIO_PIN_COUNT", "SOC_SPI_PERIPH_NUM", "SOC_UART_NUM", "SOC_BLE_SUPPORTED")


def load_source(record):
    raw = (ROOT / record["local_path"]).read_bytes()
    if hashlib.sha256(raw).hexdigest() != record["sha256"]:
        raise ValueError(f"Source hash mismatch: {record['id']}; rerun collection and inspect")
    return raw


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    docs, provenance = [], []
    for record in MANIFEST["records"]:
        source_id = record["id"]
        raw = load_source(record)
        if source_id.startswith("CVE-"):
            source = json.loads(raw)
            descriptions = source["containers"]["cna"].get("descriptions", [])
            description = next((d["value"] for d in descriptions if d.get("lang", "").lower().startswith("en")), "")
            if not description:
                raise ValueError(f"Missing English description in {source_id}")
            # Preserve the complete first paragraph where practical; no generated facts.
            text = description.split("\n\n")[0].strip()
            title, family, source_type = source_id, "cve", "official CVE CNA description"
            method = "First English CNA description, first paragraph; original text retained"
            rights = "CVE terms; see LICENSES/CVE_TERMS.html and NOTICE.md"
        else:
            lines = raw.decode("utf-8").splitlines()
            selected = [line for line in lines if line.startswith("#define ") and line.split()[1] in MACROS]
            text = "\n".join(selected)
            title, family, source_type = CHIP_NAMES[source_id] + " SoC capabilities", "esp32", "Espressif source code"
            method = "Selected exact #define lines from per-chip soc_caps.h; title identifies source chip"
            rights = "Apache-2.0 OR MIT per source header; MIT option; see LICENSES/MIT.txt and NOTICE.md"
            if not text: raise ValueError(f"No capabilities for {source_id}")
        doc_id = source_id.lower()
        docs.append({"doc_id":doc_id,"title":title,"text":text,"source_url":record["url"],"source_type":source_type,"license_note":rights,"family":family})
        provenance.append({"doc_id":doc_id,"origin_url":record["url"],"origin_revision": MANIFEST["cve_revision"] if family == "cve" else MANIFEST["esp_idf_revision"],"access_date":"2026-10-18","rights":rights,"local_file":record["local_path"],"hash":record["sha256"],"extraction_method":method,"processing_notes":"No model predictions used to select judgments"})
    (OUT / "corpus.jsonl").write_text("".join(json.dumps(d,ensure_ascii=False)+"\n" for d in docs),encoding="utf-8",newline="\n")
    with (OUT / "provenance.csv").open("w",encoding="utf-8",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(provenance[0]),lineterminator="\n"); writer.writeheader(); writer.writerows(provenance)
    for split, items in (("dev", DEV), ("test", TEST)):
        queries=[]; qrels=[]; evidence=[]
        for qid, query, qtype, family, positive, negatives in items:
            queries.append({"query_id":qid,"text":query,"query_type":qtype,"identifier_family":family,"origin":"agent_authored","annotation_note":"Agent-authored query and source-grounded judgment; no independent human review."})
            qrels.append((qid,positive.lower(),1))
            evidence.append({"query_id":qid,"doc_id":positive.lower(),"relevance":1,"reason":"Source passage directly describes the entity and requested feature; see corpus text.","reviewer":"agent"})
            if qid == "test01":
                # The other record discusses the earlier fix and JNDI lookup;
                # retain this plausible cross-reference as relevant, not a negative.
                qrels.append((qid,"cve-2021-45046",1))
                evidence.append({"query_id":qid,"doc_id":"cve-2021-45046","relevance":1,"reason":"Explicitly discusses the incomplete CVE-2021-44228 fix and related JNDI lookup behavior.","reviewer":"agent"})
            for negative in negatives:
                qrels.append((qid,negative.lower(),0))
                evidence.append({"query_id":qid,"doc_id":negative.lower(),"relevance":0,"reason":"Passage concerns a different entity or mechanism and does not directly answer the stated query.","reviewer":"agent"})
        (OUT/f"queries_{split}.jsonl").write_text("".join(json.dumps(q,ensure_ascii=False)+"\n" for q in queries),encoding="utf-8",newline="\n")
        with (OUT/f"qrels_{split}.tsv").open("w",encoding="utf-8",newline="") as f:
            w=csv.writer(f,delimiter="\t",lineterminator="\n");w.writerow(("query_id","doc_id","relevance"));w.writerows(qrels)
        with (OUT/f"judgment_evidence_{split}.csv").open("w",encoding="utf-8",newline="") as f:
            w=csv.DictWriter(f,fieldnames=["query_id","doc_id","relevance","reason","reviewer"],lineterminator="\n");w.writeheader();w.writerows(evidence)
    print(f"Built {len(docs)} candidate passages; {len(DEV)} dev and {len(TEST)} test queries")

if __name__ == "__main__": main()

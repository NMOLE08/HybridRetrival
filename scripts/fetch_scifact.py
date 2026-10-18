"""Download the official BEIR SciFact archive and verify its published checksum."""
from __future__ import annotations
import hashlib,io,json,zipfile
from pathlib import Path
from urllib.request import urlopen
import truststore

URL="https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/scifact.zip"
EXPECTED_MD5="5f7d1de60b170fc8027bb7898e2efca1"  # BEIR wiki archive checksum
ROOT=Path(__file__).resolve().parents[1]

def main():
    destination=ROOT/"data/scifact"
    if destination.exists():raise FileExistsError("data/scifact already exists; preserve it and inspect before fetching again")
    truststore.inject_into_ssl()
    with urlopen(URL,timeout=60) as response: raw=response.read()
    if hashlib.md5(raw).hexdigest()!=EXPECTED_MD5:raise ValueError("SciFact archive does not match official BEIR MD5")
    needed=("scifact/corpus.jsonl","scifact/queries.jsonl","scifact/qrels/test.tsv")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        payload={name:z.read(name) for name in needed}
    for name,data in payload.items():
        path=ROOT/"data"/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    manifest={"source":URL,"published_md5":EXPECTED_MD5,"md5":hashlib.md5(raw).hexdigest(),"sha256":hashlib.sha256(raw).hexdigest(),"dataset_license":"CC BY-SA 4.0 per BeIR/scifact dataset card","license_source":"https://huggingface.co/datasets/BeIR/scifact","files":{name.removeprefix("scifact/"):hashlib.sha256(data).hexdigest() for name,data in payload.items()}}
    (ROOT/"outputs/manifests/scifact_download.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(manifest,indent=2))
if __name__=="__main__":main()

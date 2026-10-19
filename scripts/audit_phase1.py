"""Record Phase 1 tracked artifact hashes and compare them to the reference commit."""
from __future__ import annotations
import hashlib
import argparse
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REFERENCE='60405f7701b898aad6e753e5f441b73195d04cfa'
PATHS=['src/iphr','data/technical','configs/final.yaml','outputs/final','outputs/manifests']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',default='outputs/phase2/manifests/phase1_hashes.json')
    args=parser.parse_args()
    destination=Path(args.output)
    if destination.exists():raise FileExistsError(f'Preserve the existing audit; choose a new --output: {destination}')
    names=subprocess.check_output(['git','ls-tree','-r','--name-only',REFERENCE,'--',*PATHS],text=True).splitlines()
    if not names: raise RuntimeError('No reference artifacts found')
    hashes={}
    for name in names:
        path=Path(name)
        if not path.is_file(): raise RuntimeError(f'Missing Phase 1 artifact: {name}')
        hashes[name]=hashlib.sha256(path.read_bytes()).hexdigest()
    diff=subprocess.run(['git','diff','--exit-code',REFERENCE,'--',*PATHS],capture_output=True,text=True)
    if diff.returncode not in (0,1): raise RuntimeError(diff.stderr)
    destination.parent.mkdir(parents=True,exist_ok=True)
    result={'timestamp_utc':datetime.now(timezone.utc).isoformat(),'reference_commit':REFERENCE,'paths':PATHS,
            'tracked_files':len(hashes),'git_diff_clean':diff.returncode==0,'sha256_worktree_bytes':hashes,
            'python':sys.version,'platform':platform.platform(),'processor':platform.processor(),
            'note':'Hashes describe local checkout bytes; Git diff compares normalized tracked content against the Phase 1 reference.'}
    destination.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    if diff.returncode: raise RuntimeError('Protected Phase 1 artifacts differ from reference; see git diff')
    print(f'PASS: {len(hashes)} tracked Phase 1 artifacts match {REFERENCE[:7]} in Git; hashes recorded.')


if __name__=='__main__': main()

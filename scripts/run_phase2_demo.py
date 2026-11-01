"""Start the local, real-model Phase 2 demonstration."""
import argparse
from pathlib import Path
from iphr.demo_server import serve

def main():
    parser = argparse.ArgumentParser(description="Run the local Phase 2 retrieval demo")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    serve(args.host, args.port, root / "data/phase2/corpus.jsonl", root / "configs/phase2_exploratory_final.yaml", root / "demo")

if __name__ == "__main__":
    main()

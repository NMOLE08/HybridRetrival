"""Research command-line entry point."""
import argparse
import json
from .data_io import load_corpus


def main():
    parser = argparse.ArgumentParser(description="Identifier-preserving hybrid retrieval research")
    sub = parser.add_subparsers(dest="command")
    search = sub.add_parser("search", help="Search the technical corpus")
    search.add_argument("--query", required=True)
    search.add_argument("--method", choices=["dense"], default="dense")
    search.add_argument("--top-k", type=int, default=5)
    search.add_argument("--corpus", default="data/technical/corpus.jsonl")
    args=parser.parse_args()
    if args.command == "search":
        try:
            from .dense import DenseRetriever
            result=DenseRetriever(load_corpus(args.corpus)).search(args.query,args.top_k)
            print(json.dumps(result,ensure_ascii=False,indent=2))
        except (ValueError, OSError, RuntimeError) as exc:
            parser.exit(2, f"Error: {exc}\n")
    else:
        parser.print_help()

if __name__ == "__main__": main()

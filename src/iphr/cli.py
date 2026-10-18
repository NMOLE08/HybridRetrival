"""Research command-line entry point."""
import argparse
import json
from .data_io import load_corpus


def main():
    parser = argparse.ArgumentParser(description="Identifier-preserving hybrid retrieval research")
    sub = parser.add_subparsers(dest="command")
    search = sub.add_parser("search", help="Search the technical corpus")
    search.add_argument("--query", required=True)
    search.add_argument("--method", choices=["dense", "lexical", "rrf", "proposed"], default="dense")
    search.add_argument("--top-k", type=int, default=5)
    search.add_argument("--corpus", default="data/technical/corpus.jsonl")
    search.add_argument("--config", default="configs/final.yaml")
    search.add_argument("--explain", action="store_true", help="Include identifier scoring decisions for proposed results")
    args=parser.parse_args()
    if args.command == "search":
        try:
            docs=load_corpus(args.corpus)
            if args.top_k < 1: raise ValueError("top-k must be positive")
            if args.method == "dense":
                from .dense import DenseRetriever
                retriever=DenseRetriever(docs)
            elif args.method in ("rrf", "proposed"):
                from .hybrid import HybridRetriever
                if args.method == "proposed":
                    import yaml
                    from pathlib import Path
                    from .dense import DenseRetriever
                    from .reranker import rerank
                    cfg=yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
                    retriever=HybridRetriever(docs,k=cfg['rrf_k'],dense=DenseRetriever(docs,model_id=cfg['model'],revision=cfg['model_revision']))
                    result=rerank(args.query,retriever.search(args.query,len(docs)),docs,cfg['lambda_match'],cfg['lambda_conflict'])[:args.top_k]
                    if not args.explain:
                        for row in result: row.pop('explanation',None)
                else:
                    retriever=HybridRetriever(docs)
            else:
                from .lexical import LexicalRetriever
                retriever=LexicalRetriever(docs)
            if args.method != "proposed": result=retriever.search(args.query,args.top_k)
            print(json.dumps(result,ensure_ascii=False,indent=2))
        except (ValueError, OSError, RuntimeError) as exc:
            parser.exit(2, f"Error: {exc}\n")
    else:
        parser.print_help()

if __name__ == "__main__": main()

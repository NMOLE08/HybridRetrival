"""Run an equivalent nine-sentence toy example and a development query."""
import hashlib
import json
import time
from pathlib import Path
from huggingface_hub import hf_hub_download
from sentence_transformers import SentenceTransformer
from iphr.data_io import load_corpus
from iphr.dense import DenseRetriever, MODEL_ID, MODEL_REVISION

TOY = [
 "Neural networks learn patterns from examples.",
 "A machine learning algorithm can classify text.",
 "Backpropagation updates weights in a neural network.",
 "A spacecraft travels beyond Earth.",
 "Astronomers observe stars with telescopes.",
 "A rover explores the surface of Mars.",
 "Solar panels turn sunlight into electricity.",
 "Wind turbines generate renewable electricity.",
 "Climate change affects global temperatures.",
]

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for block in iter(lambda:f.read(1024*1024), b""): h.update(block)
    return h.hexdigest()

def main():
    t=time.perf_counter(); model=SentenceTransformer(MODEL_ID,revision=MODEL_REVISION,device="cpu"); load=time.perf_counter()-t
    toy=[{"doc_id":f"toy-{i:02d}","title":"", "text":text,"source_url":"synthetic toy example"} for i,text in enumerate(TOY)]
    toy_retriever=DenseRetriever(toy,model=model)
    toy_query="How do neural networks learn?"
    toy_result=toy_retriever.search(toy_query)
    docs=load_corpus("data/technical/corpus.jsonl")
    query=json.loads(Path("data/technical/queries_dev.jsonl").read_text(encoding="utf-8").splitlines()[0])
    dense=DenseRetriever(docs,model=model)
    result=dense.search(query["text"])
    repeat=dense.search(query["text"])
    if [x["doc_id"] for x in result] != [x["doc_id"] for x in repeat]: raise RuntimeError("Repeated rankings differed")
    weights=hf_hub_download(MODEL_ID,"model.safetensors",revision=MODEL_REVISION,local_files_only=True)
    output={"model_id":MODEL_ID,"model_revision":MODEL_REVISION,"weights_sha256":sha256_file(weights),"device":"cpu","embedding_dimension":int(dense.embeddings.shape[1]),"model_load_seconds":load,"technical_corpus_hash":dense.corpus_hash,"technical_cache_key":dense.cache_key,"technical_cache_hit":dense.cache_hit,"technical_preprocessing_seconds":dense.preprocessing_seconds,"toy":{"query":toy_query,"results":toy_result,"preprocessing_seconds":toy_retriever.preprocessing_seconds},"development_example":{"query_id":query["query_id"],"query":query["text"],"results":result,"repeat_order_identical":True},"note":"Pretrained model inference only; no training. Toy texts are synthetic and are not benchmark evidence."}
    path=Path("outputs/examples/dense_demo.json");path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(output,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(output,ensure_ascii=False,indent=2))

if __name__ == "__main__": main()

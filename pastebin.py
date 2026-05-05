import math
import os
import pathlib
import re

import numpy as np
import pandas as pd
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from beir import util
from beir.datasets.data_loader import GenericDataLoader

DATA_DIR = pathlib.Path('../data/beir')
RUNS_DIR = pathlib.Path('../data/runs')
RUNS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)



url = 'https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/nfcorpus.zip'
data_path = util.download_and_unzip(url, str(DATA_DIR))

corpus, queries, qrels = GenericDataLoader(data_folder=data_path).load(split='test')

print(f'Korpus : {len(corpus):>5} Dokumente')
print(f'Queries: {len(queries):>5} Test-Anfragen')
print(f'Qrels  : {len(qrels):>5} Anfragen mit Gold-Labels')

# Beispiel-Query und -Dokument
qid = list(queries.keys())[0]
did = list(corpus.keys())[0]
print(f"\nBeispiel-Query [{qid}]: {queries[qid]!r}")
print(f"\nBeispiel-Doc   [{did}]: title={corpus[did]['title']!r}")
print(f"Text (Auszug): {corpus[did]['text'][:200]}...")


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())

doc_ids = list(corpus.keys())
doc_texts = [(corpus[d]['title'] + ' ' + corpus[d]['text']) for d in doc_ids]
tokenized_corpus = [tokenize(t) for t in doc_texts]

bm25 = BM25Okapi(tokenized_corpus)





def bm25_topk(query: str, k: int = 10) -> list[tuple[str, float]]:
    scores = bm25.get_scores(tokenize(query))
    top_idx = np.argsort(scores)[::-1][:k]
    return [(doc_ids[i], float(scores[i])) for i in top_idx]

bm25_runs: dict[str, dict[str, float]] = {}
for qid, qtext in queries.items():
    bm25_runs[qid] = dict(bm25_topk(qtext, k=100))

print(f'BM25-Run: {len(bm25_runs)} Queries, je 100 Treffer.')



model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
doc_embeddings = model.encode(doc_texts, batch_size=64, show_progress_bar=True, normalize_embeddings=True)
print(f'Doc-Embeddings: shape={doc_embeddings.shape}')
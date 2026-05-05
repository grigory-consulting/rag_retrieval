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




query_ids = list(queries.keys())
query_texts = [queries[q] for q in query_ids]
query_embeddings = model.encode(query_texts, batch_size=64, show_progress_bar=True, normalize_embeddings=True)

sims = cosine_similarity(query_embeddings, doc_embeddings)  # shape: (n_queries, n_docs)

dense_runs: dict[str, dict[str, float]] = {}
for qi, qid in enumerate(query_ids):
    top_idx = np.argsort(sims[qi])[::-1][:100]
    dense_runs[qid] = {doc_ids[i]: float(sims[qi, i]) for i in top_idx}

print(f'Dense-Run: {len(dense_runs)} Queries.')




qid_demo = next(qid for qid, gold in qrels.items() if 5 <= len(gold) <= 15)
print(f'Demo-Query [{qid_demo}]: {queries[qid_demo]!r}')
print(f'Anzahl Gold-Labels: {len(qrels[qid_demo])}')
print(f'Verteilung der Relevanzgrade: {pd.Series(qrels[qid_demo]).value_counts().to_dict()}')


def show_top10(run: dict, qid: str, gold: dict[str, int]):
    top = sorted(run[qid].items(), key=lambda x: -x[1])[:10]
    rows = []
    for rank, (did, score) in enumerate(top, start=1):
        rel = gold.get(did, 0)
        rows.append((rank, did, round(score, 3), rel, corpus[did]['title'][:60]))
    return pd.DataFrame(rows, columns=['rank', 'docid', 'score', 'rel', 'title'])

gold = qrels[qid_demo]
print('--- BM25 Top-10 ---')
print(show_top10(bm25_runs, qid_demo, gold).to_string(index=False))
print('\n--- Dense Top-10 ---')
print(show_top10(dense_runs, qid_demo, gold).to_string(index=False))





def precision_at_k(run: dict, qid: str, gold: dict, k: int) -> float:
    top = [d for d, _ in sorted(run[qid].items(), key=lambda x: -x[1])[:k]]
    hits = sum(1 for d in top if gold.get(d, 0) >= 1)
    return hits / k

p5_bm25  = precision_at_k(bm25_runs,  qid_demo, gold, 5)
p5_dense = precision_at_k(dense_runs, qid_demo, gold, 5)
print(f'Precision@5  BM25 : {p5_bm25:.3f}')
print(f'Precision@5  Dense: {p5_dense:.3f}')



def recall_at_k(run: dict, qid: str, gold: dict, k: int) -> float:
    top = [d for d, _ in sorted(run[qid].items(), key=lambda x: -x[1])[:k]]
    hits = sum(1 for d in top if gold.get(d, 0) >= 1)
    total = sum(1 for r in gold.values() if r >= 1)
    return hits / total if total else 0.0

r10_bm25  = recall_at_k(bm25_runs,  qid_demo, gold, 10)
r10_dense = recall_at_k(dense_runs, qid_demo, gold, 10)
total_rel = sum(1 for r in gold.values() if r >= 1)
print(f'|R_q| (relevante Docs gesamt): {total_rel}')
print(f'Recall@10  BM25 : {r10_bm25:.3f}')
print(f'Recall@10  Dense: {r10_dense:.3f}')


def dcg(rels: list[int], k: int) -> float:
    return sum((2**r - 1) / math.log2(i + 2) for i, r in enumerate(rels[:k]))

def ndcg_at_k(run: dict, qid: str, gold: dict, k: int) -> float:
    top = [d for d, _ in sorted(run[qid].items(), key=lambda x: -x[1])[:k]]
    retrieved_rels = [gold.get(d, 0) for d in top]
    ideal_rels = sorted(gold.values(), reverse=True)
    idcg = dcg(ideal_rels, k)
    return dcg(retrieved_rels, k) / idcg if idcg > 0 else 0.0

ndcg10_bm25  = ndcg_at_k(bm25_runs,  qid_demo, gold, 10)
ndcg10_dense = ndcg_at_k(dense_runs, qid_demo, gold, 10)
print(f'nDCG@10  BM25 : {ndcg10_bm25:.3f}')
print(f'nDCG@10  Dense: {ndcg10_dense:.3f}')




from ranx import Qrels, Run, evaluate, compare

qrels_obj = Qrels(qrels)
run_bm25  = Run(bm25_runs,  name='BM25')
run_dense = Run(dense_runs, name='Dense')

metrics = ['precision@5', 'recall@10', 'recall@100', 'ndcg@10', 'map@100', 'mrr']

report_bm25  = evaluate(qrels_obj, run_bm25,  metrics=metrics)
report_dense = evaluate(qrels_obj, run_dense, metrics=metrics)

df_agg = pd.DataFrame({'BM25': report_bm25, 'Dense': report_dense}).round(3)
df_agg['Δ (Dense − BM25)'] = (df_agg['Dense'] - df_agg['BM25']).round(3)
df_agg
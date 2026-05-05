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
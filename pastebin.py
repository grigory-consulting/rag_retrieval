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
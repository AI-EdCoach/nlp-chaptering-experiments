import re
from typing import List, Union

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers.pipelines import pipeline


class ChapterEstimator:
    def __init__(self, model_checkpoint: str = 'paraphrase-multilingual-MiniLM-L12-v2',
                 hf_model: str = "bert-base-multilingual-cased"):
        self.model = SentenceTransformer(model_checkpoint)
        self.hf_model = pipeline("feature-extraction", model=hf_model)

    def __call__(self, text: Union[str, List[str]], threshold: float = None) -> pd.DataFrame:
        if isinstance(text, List):
            sentences = text
        else:
            sentences = self.get_sentences(text)
        embeddings = self.get_embeddings(sentences)
        dimension = len(embeddings[0])
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(embeddings).astype('float16'))

        distances = []
        values_dict = {"index": [i for i in range(len(sentences))], "sentence": sentences, "embedding": [e for e in embeddings]}
        df = pd.DataFrame(values_dict)
        for i in range(len(embeddings) - 1):
            distance = index.search(np.array([embeddings[i]]).astype('float32'), 2)[0][0][1]
            distances.append(distance)

        df['faiss_search'] = distances + [None]
        cos_dist = []
        for i in range(len(embeddings) - 1):
            sim = cosine_similarity(embeddings[i].reshape(1, -1), embeddings[1 + 1].reshape(1, -1))[0][0]
            cos_dist.append(sim)

        df['cos_sim'] = cos_dist + [None]
        df['super_score'] = df['faiss_search'] * df['cos_sim']
        if threshold is None:
            threshold = df['super_score'].quantile(.25)
        df['chapter'] = [1 if score < threshold else 0 for score in df['super_score']]
        return df

    def get_embeddings(self, sentences: List[str]):
        embeddings = self.model.encode(sentences)
        return embeddings

    @staticmethod
    def get_sentences(text: str):
        sentences = re.split(r'\.\s|\.\n', text)
        sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
        return sentences

from typing import List, Dict, Any

import pandas as pd


class ChapterTimecodesPipeline:
    def __init__(self, speach2text_model, chapter_estimator):
        self.speach2text_model = speach2text_model
        self.chapter_estimator = chapter_estimator

    def __call__(self, media_file):
        preds = self.speach2text_model(media_file)
        text = " ".join([seg['text'] for seg in preds['segments']])
        chapters_df = self.chapter_estimator(text, 0.25)

        return chapters_df

    def call_for_segments(self, segments: List[Dict[str, Any]], threshold: float = None):
        text_segs = [seg['text'] for seg in segments]
        chapters_df = self.chapter_estimator(text_segs, threshold)

        preds_df = pd.DataFrame({
            "segments": [seg['text'] for seg in segments],
            "start": [seg['start'] for seg in segments],
        })
        preds_df["score"] = chapters_df["super_score"]
        preds_df["chapter"] = chapters_df["chapter"]
        return preds_df

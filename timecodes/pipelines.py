from typing import List, Dict, Any

import numpy as np
import pandas as pd

from timecodes.types import Chapter, Timecodes


class ChapterTimecodesPipeline:
    """
    Pipeline for extracting chapters from media file.
    1. Extracts text from media file using speach2text_model
    2. Estimates chapters using chapter_estimator
    3. Returns chapters_df
    """

    def __init__(self, speach2text_model, chapter_estimator, summarizer=None):
        self.speach2text_model = speach2text_model
        self.chapter_estimator = chapter_estimator
        if summarizer is not None:
            self.summarizer = summarizer

    def __call__(self, media_file: str, min_chapter_length: int = 15, summarize: bool = False):
        """
        Extracts chapters from media file.
        :param media_file: str - path to media file
        :return: pd.DataFrame - chapters_df with columns: "index" (int), "sentence" (str), "super_score" (float),
            "chapter" (int)
        """

        preds = self.speach2text_model(media_file)
        text = " ".join([seg['text'] for seg in preds['segments']])
        chapters_df = self.chapter_estimator(text)

        return chapters_df

    def call_for_segments(self, segments: List[Dict[str, Any]], summarize: bool = False) -> Timecodes:
        text_segs = [seg['text'] for seg in segments]
        chapters_df = self.chapter_estimator(text_segs)

        preds_df = pd.DataFrame({
            "segments": [seg['text'] for seg in segments],
            "start": [seg['start'] for seg in segments],
        })

        preds_df["score"] = chapters_df["super_score"]
        preds_df["chapter"] = chapters_df["chapter"]

        timecodes = []
        new_chapter_indexes = preds_df[preds_df.apply(lambda x: x["chapter"] == 1, axis=1)].index
        chapters = np.split(preds_df, new_chapter_indexes)

        for i, chapter in enumerate(chapters):
            if len(chapter) > 0:
                if chapter["start"].max() - chapter["start"].min() < 15:
                    timecodes[-1].content += " ".join(chapter["segments"])
                    timecodes[-1].end = chapter["start"].max()

                    if summarize:
                        timecodes[-1].title = self.summarizer(timecodes[-1].content)

                    continue

                if summarize:
                    timecodes.append(
                        Chapter(start=chapter["start"].min(), end=chapter["start"].max(),
                                content=" ".join(chapter["segments"]),
                                title=self.summarizer(" ".join(chapter["segments"]))))
                else:
                    timecodes.append(
                        Chapter(start=chapter["start"].min(), end=chapter["start"].max(),
                                content=" ".join(chapter["segments"])))

        timecodes = Timecodes(
            chapters=timecodes,
            media_file="test",
        )
        return timecodes

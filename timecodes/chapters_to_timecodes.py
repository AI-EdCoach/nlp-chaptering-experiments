import pandas as pd


class ChapterTimecodesPipeline:
    def __init__(self, speach2text_model, chapter_estimator):
        self.speach2text_model = speach2text_model
        self.chapter_estimator = chapter_estimator

    def __call__(self, media_file):
        preds = self.speach2text_model(media_file)
        chapters_df = self.chapter_estimator(preds['text'], 0.25)
        preds_df = pd.DataFrame(preds['segments'])
        chapters_df['timecode'] = [preds_df for i in range(len(chapters_df))]
        return chapters_df



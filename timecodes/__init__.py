from timecodes.speech_to_text import SpeechToTextWhisperX
from timecodes.pipelines import ChapterTimecodesPipeline
from timecodes.chapter_estimation import ChapterEstimator
from timecodes.summarize import Summarizer

sp2txt = SpeechToTextWhisperX(model_name="tiny")
sp2chptrs = ChapterEstimator()
summarizer = Summarizer()
chptrs2timecodes = ChapterTimecodesPipeline(sp2txt, sp2chptrs, summarizer)


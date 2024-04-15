from timecodes.speech_to_text import SpeechToTextWhisperX
from timecodes.chapters_to_timecodes import ChapterTimecodesPipeline
from timecodes.speech_to_chapters import ChapterEstimator

sp2txt = SpeechToTextWhisperX()
sp2chptrs = ChapterEstimator()

chptrs2timecodes = ChapterTimecodesPipeline(sp2txt, sp2chptrs)


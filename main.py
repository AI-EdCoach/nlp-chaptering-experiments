import dill

from timecodes import sp2txt, sp2chptrs, chptrs2timecodes

res = sp2txt("content/test data/class_1_4.wav")
timecodes = chptrs2timecodes.call_for_segments(res, summarize=True)


with open("timecodes.dill", "wb") as f:
    dill.dump(timecodes.dict(), f)


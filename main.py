import dill

from timecodes import sp2txt, sp2chptrs, chptrs2timecodes

res = sp2txt("content/test data/class_1_4.wav")
timecoes = chptrs2timecodes.call_for_segments(res)

print(timecoes)

with open("timecoes.dill", "wb") as f:
    dill.dump(timecoes, f)


import dill

from timecodes import sp2txt, sp2chptrs, chptrs2timecodes

res = sp2txt("content/yt/test.mp4")
chapters_df = chptrs2timecodes.call_for_segments(res)

print(chapters_df)

with open("chapters_df.dill", "wb") as f:
    dill.dump(chapters_df, f)


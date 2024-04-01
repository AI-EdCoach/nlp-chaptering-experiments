import os

import whisperx
import gc

from dotenv import load_dotenv

load_dotenv("../.env")

HF_TOKEN = os.getenv("HF_TOKEN")

device = "cuda"
audio_file = "../content/yt/Го в геймдев!  Все о профессии тестировщика  BYTEX Артем Стукалов.mp4"
batch_size = 16
compute_type = "float16"


class SpeechToTextWhisperX:
    def __init__(self, batch_size: int = 16, compute_type: str = "float16", device: str = "cuda",
                 model_name: str = "tiny"):
        self.batch_size = batch_size
        self.compute_type = compute_type
        self.model = whisperx.load_model("tiny", device, compute_type=self.compute_type,
                                         download_root="models/whisperx/")

    def __call__(self, audio_file: str, save_path: str = "result.txt"):
        audio = whisperx.load_audio(audio_file)
        result = self.model.transcribe(audio, batch_size=self.batch_size)
        model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
        result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
        with open("result.txt", "w", encoding="utf-8") as f:
            for seg in result["segments"]:
                f.write(f"{seg['start']} {seg['end']} {seg['text']}\n")
        return result

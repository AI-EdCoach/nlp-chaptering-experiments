from transformers import T5ForConditionalGeneration, T5Tokenizer


class Summarizer:
    def __init__(self, model: str = "utrobinmv/t5_summary_en_ru_zh_base_2048"):
        self.model = T5ForConditionalGeneration.from_pretrained(model)
        self.tokenizer = T5Tokenizer.from_pretrained(model)

    def __call__(self, text: str, brief: bool = True, max_length: int = 512):
        prefix = "summarize brief to ru: " if brief else "summarize to ru: "
        inputs_ids = self.tokenizer(prefix + text, return_tensors='pt')

        summary_ids = self.model.generate(**inputs_ids)
        summary = self.tokenizer.batch_decode(summary_ids, skip_special_tokens=True)

        return summary

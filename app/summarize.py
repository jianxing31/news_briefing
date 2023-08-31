#!/usr/bin/env python
import torch
from transformers import PegasusForConditionalGeneration
from transformers import PegasusTokenizer


class summarize:
    def __init__(self):

        model_name = "google/pegasus-cnn_dailymail"
        self.torch_device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = PegasusTokenizer.from_pretrained(model_name)
        self.model = PegasusForConditionalGeneration.from_pretrained(model_name).to(
            self.torch_device
        )

    def summarize(
        self,
        text,
    ):
        if len(text.split(" ")) >= 1024:
            text = " ".join(text.split(" ")[:1024])
        batch = self.tokenizer.prepare_seq2seq_batch(
            [text], truncation=True, padding="longest", return_tensors="pt"
        ).to(self.torch_device)
        translated = self.model.generate(**batch)
        tgt_text = self.tokenizer.batch_decode(translated, skip_special_tokens=True)
        ret = tgt_text[0]

        return ret

from transformers import BertTokenizer, EncoderDecoderModel

def load_model_and_tokenizer():
    # Either download directly from HF hub, or
    # load from local directory where you saved previously
    tokenizer = BertTokenizer.from_pretrained("cahya/bert2bert-indonesian-summarization")
    model = EncoderDecoderModel.from_pretrained("cahya/bert2bert-indonesian-summarization")
    return tokenizer, model

tokenizer, model = load_model_and_tokenizer()

def summarize_text(text):
    input_ids = tokenizer.encode(text, return_tensors='pt')

    summary_ids = model.generate(
        input_ids,
        min_length=30,
        max_length=80,
        num_beams=5,
        repetition_penalty=2.5,
        length_penalty=1.0,
        early_stopping=True,
        no_repeat_ngram_size=2
    )

    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

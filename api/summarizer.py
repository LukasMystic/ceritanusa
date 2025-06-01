import requests
import os

HF_TOKEN = os.getenv("HF_TOKEN")
print(f"Hugging Face Token loaded: {HF_TOKEN is not None}")

API_URL = "https://router.huggingface.co/hf-inference/models/cahya/t5-base-indonesian-summarization-cased"
HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

def load_model_and_tokenizer():
    # Since you are using HF API, no local model/tokenizer loading is needed
    return None, None

tokenizer, model = load_model_and_tokenizer()

def summarize_text(text):
    payload = {
        "inputs": f"ringkasan: {text}",
        "parameters": {
            "max_length": 80,
            "min_length": 30,
            "do_sample": False,
            "early_stopping": True,
            "num_beams": 4
        }
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        json_response = response.json()
        try:
            return json_response[0]["summary_text"]
        except (KeyError, IndexError, TypeError):
            return "⚠️ Respons tidak terduga dari model."
    else:
        return f"⚠️ API Error {response.status_code}: {response.text}"

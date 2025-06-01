import requests
import os

HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://router.huggingface.co/hf-inference/models/cahya/t5-base-indonesian-summarization-cased"
HEADERS = {
    "Authorization": "Bearer {HF_TOKEN}"  
}

def load_model_and_tokenizer():
    return None, None

tokenizer, model = load_model_and_tokenizer()

def summarize_text(text):
    payload = {"inputs": f"ringkasan: {text}"}
    response = requests.post(API_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        json_response = response.json()
        try:
            return json_response[0]["summary_text"]  # <-- changed here
        except (KeyError, IndexError, TypeError):
            return "⚠️ Respons tidak terduga dari model."
    else:
        return f"⚠️ API Error {response.status_code}: {response.text}"



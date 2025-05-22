import os
import pickle
import requests
from transformers import BertTokenizer, EncoderDecoderModel

# Set BASE_DIR to current file's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# URL of the raw pickle file on Hugging Face repo
PICKLE_URL = "https://huggingface.co/LukasMystic/indonesian-summarizer/resolve/main/indonesian_summarization.pkl"

# Local model path
MODEL_PATH = os.path.join(BASE_DIR, "indonesian_summarization.pkl")

# Download the pickle file if it doesn't exist locally
if not os.path.exists(MODEL_PATH):
    print("Downloading model...")
    response = requests.get(PICKLE_URL)
    response.raise_for_status()
    with open(MODEL_PATH, "wb") as f:
        f.write(response.content)
    print("Download complete.")

# Load the model and tokenizer from pickle
with open(MODEL_PATH, "rb") as f:
    loaded_tokenizer, loaded_model = pickle.load(f)

def summarize_text(text):
    input_ids = loaded_tokenizer.encode(text, return_tensors='pt')

    summary_ids = loaded_model.generate(
        input_ids,
        min_length=30,
        max_length=80,
        num_beams=5,
        repetition_penalty=2.5,
        length_penalty=1.0,
        early_stopping=True,
        no_repeat_ngram_size=2
    )

    summary = loaded_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

import os

# Must be set before importing transformers
os.environ["TRANSFORMERS_NO_TF"] = "1"

from dotenv import load_dotenv
import torch
from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer
from langchain.llms import HuggingFacePipeline

# Load env
load_dotenv()

# Paths
model_path = os.getenv("model_path")
tokenizer_path = os.getenv("tokenizer_path")

# Validate
if not model_path or not tokenizer_path:
    raise ValueError("model_path or tokenizer_path not found in the .env file.")

# Device
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
print(f"Using device: {device}")

# Load model
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
model = AutoModelForTokenClassification.from_pretrained(model_path).to(device)

# Pipeline
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device=-1)

# LangChain
llm = HuggingFacePipeline(pipeline=pipe)

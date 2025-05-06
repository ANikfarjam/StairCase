# from langchain_core.prompts import ChatPromptTemplate
# from langchain_ollama.llms import OllamaLLM

# template = """Question: {question}"""

# # Answer: Let's think step by step."""

# prompt = ChatPromptTemplate.from_template(template)

# model = OllamaLLM(model="llama3.2")

# chain = prompt | model

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
import requests
import os
from dotenv import load_dotenv

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"
MISTRAL_MODEL = "mistral-small"  # or "mistral-medium", etc.

def mistral_call(prompt: str) -> str:
    try:
        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": MISTRAL_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }

        response = requests.post(MISTRAL_API_URL, headers=headers, json=payload)
        response.raise_for_status()

        result = response.json()
        message = result["choices"][0]["message"]["content"]
        print("Mistral Response:", message)  

        return message
    except Exception as e:
        print("Mistral API Error:", e)
        return "Trivia service failed." 


# Wrap it as a LangChain Runnable
mistral_model = RunnableLambda(
    lambda prompt_value: mistral_call(
        prompt_value.to_string() if hasattr(prompt_value, "to_string") else str(prompt_value)
    )
)

# Build prompt
template = "Question: {question}"
prompt = ChatPromptTemplate.from_template(template)

# Chain = prompt → mistral_model
chain = prompt | mistral_model
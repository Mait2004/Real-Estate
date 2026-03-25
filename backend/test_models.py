import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
print(f"KEY: {api_key[:5]}...{api_key[-5:]}")
genai.configure(api_key=api_key)

try:
    models = genai.list_models()
    for m in models:
        print(m.name)
except Exception as e:
    print(f"ERROR: {e}")

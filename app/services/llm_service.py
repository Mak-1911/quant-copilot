import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
print(api_key)
genai.configure(api_key=api_key)

def generate_strategy_code(user_prompt: str) -> str:
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt_text = (
            "You are a quantitative trading assistant. "
            "Generate Python backtrader code for the following strategy description. "
            "Do not include explanations, comments, or markdown. Only output valid Python code.\n\n"
            f"Strategy description:\n{user_prompt}"
        )
        response = model.generate_content(prompt_text)
        print("Raw response:", response)
        return response.text.strip()
    except Exception as e:
        print("Gemini LLM error:", e)
        return f"Error generating code: {e}"

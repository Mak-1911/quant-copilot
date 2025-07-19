import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

def explain_strategy(code:str) -> str:
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt=(
            "Explain the following Python backtrader strategy in simple terms. "
            "Describe what it does, how it enters/exits positions, and any indicators used. "
            "Avoid unnecessary code repetition. Keep it under 150 words.\n\n"
            f"{code}"
        )
        response = model.generate_content(prompt)
        return response.text.strip() if hasattr(response, "text") else str(response)
    except Exception as e:
        print("Gemini LLM error in Explaining Strategy:", e)
        return f"Error: {str(e)}"

# import google.generativeai as genai
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
client = genai.Client()

# model = genai.GenerativeModel("gemini-2.5-flash")

def call_gemini(prompt: str) -> str:
    # response = model.generate_content(prompt)
    response = client.models.generate_content(
        # model='gemini-2.5-flash',
        model='gemini-2.5-flash',
        contents=prompt
    )
    return response.text
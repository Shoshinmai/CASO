# import google.generativeai as genai
from google import genai
from dotenv import load_dotenv
from groq import Groq
import os

# from llm import prompts

load_dotenv()
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
client1 = genai.Client()
client2 = Groq()


# model = genai.GenerativeModel("gemini-2.5-flash")

def call_gemini(prompt: str) -> str:
    # response = model.generate_content(prompt)
    response = client1.models.generate_content(
        # model='gemini-2.5-flash',
        model='gemini-2.5-flash',
        contents=prompt
    )
    return response.text

def call_groq(prompt: str) -> str:
    response = client2.chat.completions.create(
        model = "groq/compound-mini",
        messages=[
        {
            "role": "user",
            "content": prompt
        }
        ],
        temperature=1,
        max_completion_tokens=1024,
    )
    return response.choices[0].message.content

# print(call_groq("what can you do?"))
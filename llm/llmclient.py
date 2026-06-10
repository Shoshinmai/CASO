# import google.generativeai as genai
from google import genai
from dotenv import load_dotenv
from groq import Groq
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq

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
    # response = client2.chat.completions.create(
    response = ChatGroq(
    model="groq/compound-mini",
    temperature=1.0,
    max_tokens=1024  # LangChain uses max_tokens instead of max_completion_tokens
)
    res = response.invoke([HumanMessage(content=prompt)])
    # return response.choices[0].message.content
    return res.content

def call_ollama(prompt: str, model: str) -> str:
    
#     llm = ChatOllama(
#     model="llama3.2:3b",      # Drops neatly into ~2.5GB VRAM
#     temperature=0,            # Enforces strict, deterministic routing logic
#     num_ctx=4000,             # Keeps context small to save VRAM memory allocation
#     # num_ctx=2048,             # Keeps context small to save VRAM memory allocation
#     num_gpu=99,                # Forces Ollama to prioritize your RTX 3050 GPU layers
#     # format="json",
#     low_vram=True,
#     keep_alive=0
# )
    llm = ChatOllama(
    model=model,      
    temperature=0.0,
    num_ctx=16384,    
    num_predict=1024,
    num_gpu=99,              # Guarantees ALL layers stay locked on your 3050 GPU
    low_vram=True,           # Enhances context scaling algorithms for low-VRAM machines
    keep_alive=0
)
    res = llm.invoke(prompt)
    res.pretty_print()
    return res.content
    
# print(call_ollama("what can you do? and who are you exactly", "qwen2.5:7b-instruct-q3_K_M"))
# print(call_groq("what can you do?"))
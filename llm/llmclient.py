# import google.generativeai as genai
from google import genai
from dotenv import load_dotenv
from groq import Groq
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from agents.terminal.models import TerminalAction, EvaluatorDecision

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
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text


def call_groq(prompt: str, subagent=False, state_model=None) -> str:
    llm = ChatGroq(model="groq/compound-mini", temperature=1.0, max_tokens=1024)
    if subagent:
        structured_llm = llm.with_structured_output(state_model)
        action = structured_llm.invoke([HumanMessage(content=prompt)])
        return action

    res = llm.invoke([HumanMessage(content=prompt)])
    return res.content


def call_ollama(prompt: str, model: str, subagent=False, state_model=None) -> str:

    llm = ChatOllama(
        model=model,
        temperature=0.0,
        num_ctx=16384,
        num_predict=1024,
        num_gpu=99,
        low_vram=True,
        keep_alive=0,
    )
    if subagent:
        structured_llm = llm.with_structured_output(state_model, method="json_mode")
        action = structured_llm.invoke(prompt)
        return action

    res = llm.invoke(prompt)
    res.pretty_print()
    return res.content


# print(call_ollama("what can you do? and who are you exactly", "qwen2.5:7b-instruct-q3_K_M"))
# print(call_groq("what can you do?"))

# import google.generativeai as genai
from google import genai
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from agents.terminal.tools import TOOLS

load_dotenv()
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
client1 = genai.Client()


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


def call_ollama(
    prompt: str, model: str, subagent=False, state_model=None, tool=False
) -> str:

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
        # structured_llm = llm.with_structured_output(state_model)
        structured_llm = llm.with_structured_output(state_model, method="json_mode")
        action = structured_llm.invoke(prompt)
        return action

    elif tool:
        llm_with_tools = llm.bind_tools(TOOLS)
        print(type(llm))
        print(type(llm_with_tools))
        return llm_with_tools.invoke(prompt)

    res = llm.invoke(prompt)
    res.pretty_print()
    return res.content

def call_nvidia(prompt: str, model: str, subagent=False, state_model=None, tool=False):
    llm = ChatNVIDIA(
    model=model,
    temperature=0.2,
    timeout= 180,
    top_p=0.95,
    max_completion_tokens=16384,
    )
    if subagent:
        structured_llm = llm.with_structured_output(state_model, method="json_mode")
        print(state_model)
        print(state_model.model_json_schema())
        action = structured_llm.invoke(prompt)
        return action

    elif tool:
        llm_with_tools = llm.bind_tools(TOOLS)
        print(type(llm))
        print(type(llm_with_tools))
        return llm_with_tools.invoke(prompt)
    res = llm.invoke(prompt)
    return res.content

# print(call_nvidia("what can you do?", "nvidia/nemotron-3-ultra-550b-a55b"))

# print(call_ollama("what can you do? and who are you exactly", "qwen2.5:7b-instruct-q3_K_M"))
# print(call_groq("what can you do?"))

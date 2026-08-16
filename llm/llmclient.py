# import google.generativeai as genai
import json
import re
import os
from google import genai
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from agents.terminal.tools import TOOLS
import requests
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

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


# def call_ollama(
#     prompt: str, model: str, subagent=False, state_model=None, tool=False
# ) -> str:

#     llm = ChatOllama(
#         model=model,
#         temperature=0.0,
#         num_ctx=16384,
#         num_predict=1024,
#         num_gpu=99,
#         low_vram=True,
#         keep_alive=0,
#     )
#     if subagent:
#         # structured_llm = llm.with_structured_output(state_model)
#         structured_llm = llm.with_structured_output(state_model)
#         action = structured_llm.invoke(prompt)
#         return action

#     elif tool:
#         llm_with_tools = llm.bind_tools(TOOLS)
#         # print(type(llm))
#         # print(type(llm_with_tools))
#         return llm_with_tools.invoke(prompt)

#     res = llm.invoke(prompt)
#     res.pretty_print()
#     return res.content

# def call_nvidia(prompt: str, model: str, subagent=False, state_model=None, tool=False):
#     llm = ChatNVIDIA(
#     model=model,
#     temperature=0.2,
#     timeout= 100,
#     top_p=0.95,
#     max_completion_tokens=16384,
#     )
#     if subagent:
#         structured_llm = llm.with_structured_output(state_model)
#         # print(state_model)
#         # print(state_model.model_json_schema())
#         action = structured_llm.invoke(prompt)
#         return action

#     elif tool:
#         llm_with_tools = llm.bind_tools(TOOLS)
#         # print(type(llm))
#         # print(type(llm_with_tools))
#         return llm_with_tools.invoke(prompt)
#     res = llm.invoke(prompt)
#     return res.content

# print(call_nvidia("what can you do?", "nvidia/nemotron-3-ultra-550b-a55b"))

# print(call_ollama("what can you do? and who are you exactly", "qwen2.5:7b-instruct-q3_K_M"))
# print(call_groq("what can you do?"))

def _robust_pydantic_parse(parser: PydanticOutputParser, raw_content: str, llm_instance=None, original_prompt: str = ""):
    """Cleans out thinking tags and markdown blocks, then parses cleanly."""
    if not raw_content or not raw_content.strip():
        raw_content = "{}"

    # CRITICAL DEEPSEEK FIX: Strip out the entire <think>...</think> block if it exists
    # This prevents the inner LangChain engine from trying to parse the thoughts as JSON
    raw_content = re.sub(r"<think>.*?</think>", "", raw_content, flags=re.DOTALL).strip()

    try:
        # 1. Attempt standard parsing
        return parser.parse(raw_content)
    except Exception:
        # 2. Fallback: Use Regex to extract valid curly brace boundaries
        try:
            match = re.search(r"(\{.*})", raw_content, re.DOTALL)
            if match:
                clean_json_str = match.group(1)
                json_dict = json.loads(clean_json_str)
                return parser.pydantic_object.model_validate(json_dict)
        except Exception:
            pass
        
        # 3. Auto-Correction Loop
        if llm_instance and original_prompt:
            print("\n🔄 [Parsing Failure] Model output is invalid JSON. Triggering automatic healing...")
            correction_prompt = (
                f"You are a strict data-fixing agent. The user prompt was:\n###\n{original_prompt}\n###\n\n"
                f"The model replied with invalid layout text:\n###\n{raw_content}\n###\n\n"
                f"Fix it completely. Return ONLY valid JSON adhering strictly to this schema instruction. "
                f"Do not include thoughts, introduction, or text outside the JSON:\n"
                f"{parser.get_format_instructions()}"
            )
            try:
                fixed_res = llm_instance.invoke(correction_prompt)
                fixed_content = re.sub(r"<think>.*?</think>", "", fixed_res.content, flags=re.DOTALL).strip()
                match_fixed = re.search(r"(\{.*})", fixed_content, re.DOTALL)
                if match_fixed:
                    return parser.pydantic_object.model_validate(json.loads(match_fixed.group(1)))
                return parser.parse(fixed_content)
            except Exception as healing_err:
                print(f"❌ [Healing Failed] Auto-correction loop failed: {healing_err}")
        
        raise OutputParserException(f"Failed to parse or heal output. Raw text: {raw_content}")


def call_ollama(
    prompt: str, model: str, subagent=False, state_model=None, tool=False
) -> str:
    # Force deepseek-r1:8b if coming from an external failover path
    local_model = model if "nvidia" not in model.lower() and "gpt" not in model.lower() else "deepseek-r1:8b"
    
    llm = ChatOllama(
        model=local_model,
        temperature=0.0,      
        num_ctx=8192,         
        num_predict=2048,     
        num_gpu=99,
        low_vram=True,
        keep_alive=0,
        # CRITICAL FIX: Stops LangChain from hiding the <think> tags from the stream
        reasoning=False
    )
    
    if subagent and state_model:
        parser = PydanticOutputParser(pydantic_object=state_model)
        structured_prompt = prompt + f"\n\n{parser.get_format_instructions()}"
        
        print(f"\n🧠 [{local_model}] Thinking process started:")
        full_content = ""
        
        # This loop will now display both <think> process tokens and the final JSON chunks live
        for chunk in llm.stream(structured_prompt):
            reasoning_chunk = chunk.additional_kwargs.get("reasoning_content")
            
            if reasoning_chunk:
                # Stream the live thought block
                print(reasoning_chunk, end="", flush=True)
            elif chunk.content:
                # Once thoughts end, seamlessly transition to streaming the JSON content
                print(chunk.content, end="", flush=True)
            full_content += chunk.content
            
        print("\n🏁 Thinking finished. Validating structure...")
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Hand the raw compiled string (including the streamed thoughts) to our regex-stripping parser
        return _robust_pydantic_parse(parser, full_content, llm_instance=llm, original_prompt=structured_prompt)

    elif tool:
        res = llm.invoke(prompt)
        print(f"\nFULL CONTENT--> {res}\n")
        return res

    # Standard non-structured execution stream
    full_content = ""
    for chunk in llm.stream(prompt):
        print(chunk.content, end="", flush=True)
        full_content += chunk.content
    return full_content


@retry(
    retry=retry_if_exception_type(requests.exceptions.ReadTimeout),
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=2, min=2, max=6),
    reraise=True
)
def _execute_nvidia_call(prompt, model, subagent, state_model, tool):
    llm = ChatNVIDIA(
        model=model,
        temperature=0.2,
        timeout=60, # Quick failover cutoff 
        top_p=0.95,
        max_completion_tokens=16384,
    )
    
    if subagent and state_model:
        parser = PydanticOutputParser(pydantic_object=state_model)
        structured_prompt = prompt + f"\n\n{parser.get_format_instructions()}"
        res = llm.invoke(structured_prompt)
        return _robust_pydantic_parse(parser, res.content, llm_instance=llm, original_prompt=structured_prompt)

    elif tool:
        llm_with_tools = llm.bind_tools(TOOLS)
        return llm_with_tools.invoke(prompt)
        
    res = llm.invoke(prompt)
    return res.content

def call_nvidia(
    prompt: str, model: str, subagent=False, state_model=None, tool=False
):
    try:
        return _execute_nvidia_call(prompt, model, subagent, state_model, tool)
    except (requests.exceptions.ReadTimeout, Exception) as e:
        # Catch timeouts or parsing exceptions to failover to local Ollama execution
        print(f"\n⚠️ [NVIDIA Error/Timeout] Swapping to local Ollama execution... Reason: {e}")
        fallback_local_model = "openai/gpt-oss-20b" 
        # fallback_local_model = "deepseek-r1:8b "
        # return call_ollama(
        #     prompt=prompt, 
        #     model=fallback_local_model, 
        #     subagent=subagent, 
        #     state_model=state_model, 
        #     tool=tool
        # )
        return call_nvidia(
            prompt=prompt, 
            model=fallback_local_model, 
            subagent=subagent, 
            state_model=state_model, 
            tool=tool
        )
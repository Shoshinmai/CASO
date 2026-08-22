# import google.generativeai as genai
import json
import re
import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_nvidia_ai_endpoints import ChatNVIDIA
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from agents.terminal.tools import TOOLS
import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

load_dotenv()
# genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# client1 = genai.Client()


# model = genai.GenerativeModel("gemini-2.5-flash")


# def call_gemini(prompt: str) -> str:
#     # response = model.generate_content(prompt)
#     response = client1.models.generate_content(
#         # model='gemini-2.5-flash',
#         model="gemini-2.5-flash",
#         contents=prompt,
#     )
#     return response.text


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


async def _robust_pydantic_parse_async(
    parser: PydanticOutputParser,
    raw_content: str,
    llm_instance=None,
    original_prompt: str = "",
):
    """Async version of robust structured-output parsing."""

    if not raw_content or not raw_content.strip():
        raw_content = "{}"

    raw_content = re.sub(
        r"<think>.*?</think>",
        "",
        raw_content,
        flags=re.DOTALL,
    ).strip()

    try:
        return parser.parse(raw_content)

    except Exception:

        try:
            match = re.search(
                r"(\{.*})",
                raw_content,
                re.DOTALL,
            )

            if match:
                clean_json_str = match.group(1)

                json_dict = json.loads(clean_json_str)

                return parser.pydantic_object.model_validate(json_dict)

        except Exception:
            pass

        if llm_instance and original_prompt:

            print(
                "\n🔄 [Parsing Failure] "
                "Model output is invalid JSON. "
                "Triggering automatic healing..."
            )

            correction_prompt = (
                f"You are a strict data-fixing agent. "
                f"The user prompt was:\n###\n"
                f"{original_prompt}\n###\n\n"
                f"The model replied with invalid layout text:"
                f"\n###\n{raw_content}\n###\n\n"
                f"Fix it completely. Return ONLY valid JSON "
                f"adhering strictly to this schema instruction. "
                f"Do not include thoughts, introduction, or text "
                f"outside the JSON:\n"
                f"{parser.get_format_instructions()}"
            )

            try:
                fixed_res = await llm_instance.ainvoke(correction_prompt)

                fixed_content = re.sub(
                    r"<think>.*?</think>",
                    "",
                    fixed_res.content,
                    flags=re.DOTALL,
                ).strip()

                match_fixed = re.search(
                    r"(\{.*})",
                    fixed_content,
                    re.DOTALL,
                )

                if match_fixed:
                    return parser.pydantic_object.model_validate(
                        json.loads(match_fixed.group(1))
                    )

                return parser.parse(fixed_content)

            except Exception as healing_err:

                print(
                    f"❌ [Healing Failed] "
                    f"Auto-correction loop failed: "
                    f"{healing_err}"
                )

        raise OutputParserException(
            "Failed to parse or heal output. " f"Raw text: {raw_content}"
        )

async def _stream_llm_response(
    llm,
    prompt: str,
    show_reasoning: bool = True,
) -> str:
    """
    Stream an LLM response live while accumulating the final content.

    Returns:
        The complete accumulated response content.
    """

    full_content = ""

    async for chunk in llm.astream(prompt):

        reasoning_chunk = chunk.additional_kwargs.get(
            "reasoning_content"
        )

        if show_reasoning and reasoning_chunk:
            print(
                reasoning_chunk,
                end="",
                flush=True,
            )

        if chunk.content:
            print(
                chunk.content,
                end="",
                flush=True,
            )

            full_content += chunk.content

    return full_content

async def call_ollama(
    prompt: str,
    model: str,
    subagent=False,
    state_model=None,
    tool=False,
) -> str:

    local_model = (
        model
        if (
            "nvidia" not in model.lower()
            and "gpt" not in model.lower()
        )
        else "deepseek-r1:8b"
    )

    llm = ChatOllama(
        model=local_model,
        temperature=0.0,
        num_ctx=16352,
        num_predict=2048,
        num_gpu=99,
        low_vram=True,
        keep_alive=0,
        reasoning=False,
    )

    # ----------------------------------------------------------
    # Structured subagent output
    # ----------------------------------------------------------

    if subagent and state_model:

        parser = PydanticOutputParser(
            pydantic_object=state_model
        )

        structured_prompt = (
            "nothink\n"
            + prompt
            + "\n\n"
            + parser.get_format_instructions()
        )

        print(
            f"\n🧠 [{local_model}] "
            "Thinking process started:\n"
        )

        full_content = await _stream_llm_response(
            llm=llm,
            prompt=structured_prompt,
            show_reasoning=True,
        )

        print(
            "\n\n🏁 Thinking finished. "
            "Validating structure..."
        )

        return await _robust_pydantic_parse_async(
            parser,
            full_content,
            llm_instance=llm,
            original_prompt=structured_prompt,
        )

    # ----------------------------------------------------------
    # Tool-enabled invocation
    # ----------------------------------------------------------

    if tool:

        res = await llm.ainvoke(
            prompt
        )

        print(
            f"\nFULL CONTENT--> {res}\n"
        )

        return res

    # ----------------------------------------------------------
    # Standard streamed output
    # ----------------------------------------------------------

    return await _stream_llm_response(
        llm=llm,
        prompt=prompt,
        show_reasoning=True,
    )


@retry(
    retry=retry_if_exception_type(
        requests.exceptions.ReadTimeout
    ),
    stop=stop_after_attempt(2),
    wait=wait_exponential(
        multiplier=2,
        min=2,
        max=6,
    ),
    reraise=True,
)
async def _aexecute_nvidia_call(
    prompt,
    model,
    subagent,
    state_model,
    tool,
):

    llm = ChatNVIDIA(
        model=model,
        temperature=0.2,
        timeout=60,
        top_p=0.95,
        max_completion_tokens=16384,
    )

    # ----------------------------------------------------------
    # Structured output
    # ----------------------------------------------------------

    if subagent and state_model:

        parser = PydanticOutputParser(
            pydantic_object=state_model
        )

        structured_prompt = (
            prompt
            + "\n\n"
            + parser.get_format_instructions()
        )

        print(
            f"\n🧠 [{model}] "
            "Thinking process started:\n"
        )

        full_content = await _stream_llm_response(
            llm=llm,
            prompt=structured_prompt,
            show_reasoning=True,
        )

        print(
            "\n\n🏁 Thinking finished. "
            "Validating structure..."
        )

        return await _robust_pydantic_parse_async(
            parser,
            full_content,
            llm_instance=llm,
            original_prompt=structured_prompt,
        )

    # ----------------------------------------------------------
    # Tool call
    # ----------------------------------------------------------

    if tool:

        llm_with_tools = llm.bind_tools(
            TOOLS
        )

        return await llm_with_tools.ainvoke(
            prompt
        )

    # ----------------------------------------------------------
    # Standard streamed output
    # ----------------------------------------------------------

    return await _stream_llm_response(
        llm=llm,
        prompt=prompt,
        show_reasoning=True,
    )

async def call_nvidia(
    prompt: str,
    model: str,
    subagent=False,
    state_model=None,
    tool=False,
):
    try:

        return await _aexecute_nvidia_call(
            prompt,
            model,
            subagent,
            state_model,
            tool,
        )

    except Exception as e:

        print(
            "\n⚠️ [NVIDIA Error/Timeout] "
            "Swapping to local Ollama execution... "
            f"Reason: {e}"
        )

        fallback_local_model = (
            # "openai/gpt-oss-20b"
            "freehuntx/qwen3-coder:8b"
        )

        return await call_ollama(
            prompt=prompt,
            model=fallback_local_model,
            subagent=subagent,
            state_model=state_model,
            tool=tool,
        )

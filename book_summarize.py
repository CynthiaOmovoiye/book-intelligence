"""Shared book summarization: OpenRouter (GPT) + Ollama, same prompts as the notebook."""

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

MODEL_GPT = "gpt-4o-mini"
MODEL_LLAMA = "llama3.2"
OLLAMA_BASE_URL = "http://localhost:11434/v1"

ollama = OpenAI(
    base_url=OLLAMA_BASE_URL,
    api_key="ollama",
    timeout=60,
)
api_key = os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
    default_headers={
        "HTTP-Referer": "http://localhost:8888",
        "X-Title": "llm_engineering_course",
    },
)

SYSTEM_PROMPT = """
You are a precise book-summary assistant.



Rules:
- Use ONLY the provided public description, title, Date published and authors.
- Do NOT add facts not present in the description.
- Do NOT include release/promotional lines unless central to the book's ideas.
- Output must follow the exact format below.
- Keep total output under 170 words.

Exact output format:
What it's about: <one sentence>
Author(s): <authors>
Date published: <date>

Key ideas:
- <idea 1>
- <idea 2>
- <idea 3>
- <idea 4>
- <idea 5>

Who it's for: <one line>
""".strip()


def build_user_prompt(meta: dict) -> str:
    authors = ", ".join(meta.get("authors") or []) or "Unknown"
    return f"""
Title: {meta.get("title", "Unknown")}
Author(s): {authors},
Date published: {meta.get("publishedDate", "Unknown")}

Public description:
{meta.get("description", "")}

Now follow the exact output format from the system message.
Do not write paragraphs beyond that format.
""".strip()


def llm_with_gpt(user_prompt: str, stream: bool = False) -> str:
    response = openai_client.chat.completions.create(
        model=MODEL_GPT,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
        stream=stream,
    )
    if stream:
        text = ""
        for chunk in response:
            text += chunk.choices[0].delta.content or ""
        return text
    return response.choices[0].message.content


def llm_with_llama(user_prompt: str, stream: bool = False) -> str:
    response = ollama.chat.completions.create(
        model=MODEL_LLAMA,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        stream=stream,
    )
    if stream:
        text = ""
        for chunk in response:
            text += chunk.choices[0].delta.content or ""
        return text
    return response.choices[0].message.content


def summarize_book(meta: dict, llm_callable, stream: bool = False) -> str:
    """
    Summarize a book using metadata from a public source.

    Parameters:
        meta (dict): Book metadata (title, authors, description, etc.)
        llm_callable (callable): Function that takes a prompt string and returns model output.
        stream (bool): Whether to stream tokens (accumulated into final string).

    Returns:
        str: Structured summary text from the LLM, or a fallback message.
    """
    if not meta or not meta.get("description"):
        return (
            "I couldn't find a public description for this book from the source used."
        )

    prompt = build_user_prompt(meta)
    return llm_callable(prompt, stream=stream)

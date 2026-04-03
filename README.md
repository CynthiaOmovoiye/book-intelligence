---
title: book-intelligence
app_file: gradio_app.py
sdk: gradio
sdk_version: 4.44.1
python_version: "3.12"
---
# 📚 Book Intelligence Tool

Look up any book and get a structured AI-powered summary — using **two model backends simultaneously**: a cloud LLM (GPT-4o-mini via OpenRouter) and a local LLM (Llama 3.2 via Ollama).

You can run the same flow in a **Gradio web UI** or in the **Jupyter notebook**.

---

## What it does

1. Takes a book title + author
2. Fetches metadata (description, publication date, categories) from the **Google Books API**
3. Sends the metadata to **two LLMs** with a strict system prompt
4. Returns a structured summary in a consistent format — from both models, so you can compare outputs

**Output format:**
```
What it's about: <one sentence>
Author(s): <authors>
Date published: <date>

Key ideas:
- <idea 1>
- ...

Who it's for: <one line>
```

---

## Project layout

| File | Role |
|------|------|
| `gradio_app.py` | Web UI: lookup + dual summaries (recommended for local demos) |
| `book_intelligence.ipynb` | Interactive notebook with optional live streaming in Jupyter |
| `book_lookup.py` | `lookup_book_google()` — Google Books API |
| `book_summarize.py` | Clients, prompts, `summarize_book()`, LLM helpers (shared by UI + notebook) |
| `requirements.txt` | Python dependencies (includes version pins for Gradio compatibility) |

---

## Why two backends?

Running the same task through a cloud model (GPT-4o-mini) and a local model (Llama 3.2 via Ollama) side by side shows how output quality, tone, and structure vary across providers — useful for:

- Evaluating whether a local model is good enough for a given task (cost vs. quality tradeoff)
- Understanding how prompt constraints hold up across different model families
- Offline-capable summarisation when no API key is available

---

## Features

- **Gradio UI** — enter title and author; see raw Google Books metadata plus GPT and Llama summaries side by side
- **Google Books API integration** — no scraping, clean structured metadata
- **Dual model support** — cloud (GPT-4o-mini) and local (Llama 3.2 via Ollama)
- **Streaming output (notebook)** — both models support real-time token streaming in Jupyter
- **Strict prompt engineering** — system prompt constrains the model to use only the provided description, reducing hallucination about book contents
- **Shared library code** — `book_lookup.py` and `book_summarize.py` keep the notebook and Gradio app in sync

---

## Quick Start

### 1. Install dependencies

**Use a virtual environment** for this project so Gradio’s pinned `huggingface_hub` does not clash with other tools (for example **langchain-huggingface**, which needs a newer `huggingface_hub`).

**Option A — `uv`**

```bash
cd /path/to/book-intelligence
uv venv
uv pip install -r requirements.txt
```

`uv pip install` only works after `uv venv` (or with an activated venv). Without a venv, uv will suggest `--system`; avoid `--system` if you already use LangChain or other HF tooling globally.

Run the app with:

```bash
uv run python gradio_app.py
```

**Option B — standard venv**

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python gradio_app.py
```

If you already ran `python3 -m pip install "huggingface_hub<0.23"` into your **user** site-packages and rely on **langchain-huggingface** elsewhere, restore the newer hub for your user install:

```bash
python3 -m pip install "huggingface_hub>=0.33.4"
```

Then keep Book Intelligence dependencies only inside `.venv` as above.

### 2. Configure the cloud API (OpenRouter)

1. Get an API key at [openrouter.ai](https://openrouter.ai)
2. Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=your_key_here
```

The app uses the OpenAI-compatible client pointed at `https://openrouter.ai/api/v1` (see `book_summarize.py`).

### 3. Run the local LLM (optional but recommended for full comparison)

```bash
# https://ollama.ai
ollama pull llama3.2
ollama serve
```

Leave this running in a separate terminal while you use the app.

### 4. Run the Gradio app (main way to run locally)

From the project directory, with dependencies installed in your venv:

```bash
uv run python gradio_app.py
```

If you use a classic venv and have activated it:

```bash
python gradio_app.py
```

Gradio binds to **127.0.0.1** on port **7860** by default (see `gradio_app.py`). Open the printed URL in your browser, enter **book title** and **author**, then click **Look up & summarize**.

**Runtime environment variables (optional)**

| Variable | Purpose |
|----------|---------|
| `GRADIO_SERVER_PORT` | Port (default `7860`). |
| `GRADIO_SHARE` | Set to `1`, `true`, or `yes` to create a temporary public Gradio link if localhost checks fail (VPN/proxy). |
| `NO_PROXY` | e.g. `127.0.0.1,localhost` — often fixes “localhost not accessible” when a system proxy intercepts local traffic. |

Example:

```bash
export NO_PROXY=127.0.0.1,localhost
uv run python gradio_app.py
```



### Notebook (Jupyter / VS Code)

```bash
jupyter notebook book_intelligence.ipynb
```

Run cells from top to bottom. The notebook imports `book_lookup` and `book_summarize`, so keep those files in the same directory as the notebook.

### Google Colab

Colab does not include this repo by default. Either **clone the repository** or **upload** `book_intelligence.ipynb`, `book_lookup.py`, and `book_summarize.py` into the same Colab session. Add `OPENAI_API_KEY` as a Colab secret or in a `.env` workflow you prefer.

---



## Example (Python)

```python
from book_lookup import lookup_book_google
from book_summarize import llm_with_gpt, summarize_book

meta = lookup_book_google("Atomic Habits", "James Clear")
summary = summarize_book(meta, llm_with_gpt)
```

Output:
```
What it's about: Transform your life with tiny changes in behaviour through atomic habits.
Author(s): James Clear
Date published: 2018-10-18

Key ideas:
- Real change comes from the compound effect of small decisions
- The concept of Habit Stacking for building routines
- The Two Minute Rule for overcoming procrastination
- Psychology and neuroscience behind habit formation
- Small changes produce revolutionary outcomes over time

Who it's for: Anyone looking to improve productivity and build lasting habits.
```

---

## Architecture Notes

**Why constrain the LLM to only the provided description?**
Book descriptions from Google Books are public, factual, and attribution-safe. Letting the model draw on training data would risk hallucinating plot details, misattributing quotes, or fabricating critical reception. The system prompt explicitly blocks this: *"Do NOT add facts not present in the description."*

**Why OpenRouter for the cloud backend?**
The same `openai.OpenAI` client works for both OpenRouter and direct OpenAI endpoints — swapping models is one line change.

**Why Ollama for local?**
Ollama exposes a local OpenAI-compatible endpoint (`http://localhost:11434/v1`), so the same function signature works for both backends. The `summarize_book()` function accepts any callable — you can swap in any LLM without changing the rest of the code.

---

## Requirements

Install everything inside your virtual environment:

```bash
uv pip install -r requirements.txt
```

(or `pip install -r requirements.txt` after `python3 -m venv .venv` and `source .venv/bin/activate`.)

Core packages: `openai`, `requests`, `python-dotenv`, `ipython`, `gradio` (4.44+), plus intentional pins:

- **`starlette<1`**, **`jinja2<3.1`** — avoid Gradio template / Jinja cache errors with Starlette 1.x.
- **`huggingface_hub<0.23`** — Gradio 4.x still expects APIs removed in newer `huggingface_hub` on some setups.

For the local model:

```bash
ollama pull llama3.2
```

---

## Author

Built by **Cynthia Omovoiye** — AI Engineer specialising in production LLM systems, multi-agent workflows, and RAG pipelines.

- [LinkedIn](https://www.linkedin.com/in/cynthia-omovoiye-469568184)
- [Portfolio](https://cynthia-omovoiye-portfolio.netlify.app)

## License

MIT

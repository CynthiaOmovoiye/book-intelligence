# 📚 Book Intelligence Tool

Look up any book and get a structured AI-powered summary — using **two model backends simultaneously**: a cloud LLM (GPT-4o-mini via OpenRouter) and a local LLM (Llama 3.2 via Ollama).

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

## Why two backends?

Running the same task through a cloud model (GPT-4o-mini) and a local model (Llama 3.2 via Ollama) side by side shows how output quality, tone, and structure vary across providers — useful for:

- Evaluating whether a local model is good enough for a given task (cost vs. quality tradeoff)
- Understanding how prompt constraints hold up across different model families
- Offline-capable summarisation when no API key is available

---

## Features

- **Google Books API integration** — no scraping, clean structured metadata
- **Dual model support** — cloud (GPT-4o-mini) and local (Llama 3.2 via Ollama) in the same notebook
- **Streaming output** — both models support real-time token streaming to notebook
- **Strict prompt engineering** — system prompt constrains the model to use only the provided description, preventing hallucination about book contents
- **Clean function design** — `lookup_book_google()`, `build_user_prompt()`, `summarize_book()` are independently testable and reusable

---

## Quick Start

### Cloud model (GPT-4o-mini via OpenRouter)

1. Get a free API key at [openrouter.ai](https://openrouter.ai)
2. Open `book_intelligence.ipynb` in Google Colab
3. Add your key as a Colab secret named `OPENAI_API_KEY`
4. Run all cells

### Local model (Llama 3.2 via Ollama)

```bash
# Install Ollama: https://ollama.ai
ollama pull llama3.2
ollama serve

# Then run the notebook locally in Jupyter
pip install openai requests python-dotenv
jupyter notebook book_intelligence.ipynb
```

---

## Example

```python
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

```
openai>=1.0.0
requests
python-dotenv
ipython
```

For local model:
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

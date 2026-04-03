"""Gradio UI: Google Books lookup + dual LLM summaries (same flow as book_intelligence.ipynb)."""

import json
import os

import gradio as gr
import requests

from book_lookup import lookup_book_google
from book_summarize import MODEL_LLAMA, llm_with_gpt, llm_with_llama, summarize_book


def run_lookup_and_summarize(book_title: str, author_name: str):
    title = (book_title or "").strip()
    author = (author_name or "").strip()
    empty_meta = "Please enter both a book title and an author name."

    if not title or not author:
        return empty_meta, "", ""

    try:
        meta = lookup_book_google(title, author)
    except requests.RequestException as e:
        return f"Lookup failed (network or API error): {e}", "", ""

    if meta is None:
        return (
            "No results found on Google Books for that title and author.",
            "",
            "",
        )

    meta_json = json.dumps(meta, indent=2, ensure_ascii=False)

    try:
        gpt_summary = summarize_book(meta, llm_with_gpt)
    except Exception as e:
        gpt_summary = f"GPT (OpenRouter) error: {e}"

    try:
        llama_summary = summarize_book(meta, llm_with_llama)
    except Exception as e:
        llama_summary = (
            f"Llama (Ollama) error: {e}. "
            f"Is `ollama serve` running with `{MODEL_LLAMA}` pulled?"
        )

    return meta_json, gpt_summary, llama_summary


def main() -> None:
    with gr.Blocks(title="Book Intelligence") as demo:
        gr.Markdown(
            "## Book Intelligence\n"
            "Enter **book title** and **author**. We fetch metadata from Google Books, "
            "then produce the same structured summary from **GPT-4o-mini** (OpenRouter) "
            "and **Llama** (local Ollama) — matching the notebook."
        )
        with gr.Row():
            book_title = gr.Textbox(label="Book title", placeholder="e.g. Atomic Habits")
            author_name = gr.Textbox(label="Author name", placeholder="e.g. James Clear")
        run_btn = gr.Button("Look up & summarize", variant="primary")

        gr.Markdown("### Raw metadata (Google Books)")
        metadata_out = gr.Code(language="json")

        gr.Markdown("### GPT-4o-mini (OpenRouter)")
        gpt_out = gr.Markdown()
        gr.Markdown("### Llama (Ollama)")
        llama_out = gr.Markdown()

        outs = [metadata_out, gpt_out, llama_out]
        run_btn.click(
            fn=run_lookup_and_summarize,
            inputs=[book_title, author_name],
            outputs=outs,
        )
        book_title.submit(
            fn=run_lookup_and_summarize,
            inputs=[book_title, author_name],
            outputs=outs,
        )
        author_name.submit(
            fn=run_lookup_and_summarize,
            inputs=[book_title, author_name],
            outputs=outs,
        )

    # VPN/proxy can make Gradio's localhost probe fail; 127.0.0.1 + NO_PROXY often fixes it.
    # If it still fails, run with: GRADIO_SHARE=1 uv run python gradio_app.py (temporary public URL).
    share = os.environ.get("GRADIO_SHARE", "").lower() in ("1", "true", "yes")
    demo.launch(
        server_name="127.0.0.1",
        server_port=int(os.environ.get("GRADIO_SERVER_PORT", "7860")),
        inbrowser=False,
        share=share,
    )


if __name__ == "__main__":
    main()

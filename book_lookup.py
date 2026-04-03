"""Google Books lookup used by the notebook and Gradio UI."""

import os
import time

import requests

# Cloud IPs (e.g. Hugging Face Spaces) often see transient 503/429 from Google without a key.
_RETRY_STATUS = (429, 503)
_MAX_ATTEMPTS = 4
_BACKOFF_SEC = (1.0, 2.0, 4.0)


def lookup_book_google(title: str, author: str, max_results: int = 3):
    """
    Look up a book on Google Books API using title + author,
    then return normalized metadata for the best match.

    Parameters:
        title (str): Book title to search for.
        author (str): Author name to search for.
        max_results (int): How many results to request from API.

    Returns:
        dict | None:
            Normalized metadata dict for best match, or None if no match found.
    """
    query = f"intitle:{title} inauthor:{author}"
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {"q": query, "maxResults": max_results}
    api_key = os.environ.get("GOOGLE_BOOKS_API_KEY")
    if api_key:
        params["key"] = api_key

    headers = {
        "User-Agent": "BookIntelligence/1.0 (book lookup; +https://developers.google.com/books)",
    }

    response = None
    for attempt in range(_MAX_ATTEMPTS):
        response = requests.get(
            url, params=params, headers=headers, timeout=25
        )
        if response.status_code in _RETRY_STATUS and attempt < _MAX_ATTEMPTS - 1:
            time.sleep(_BACKOFF_SEC[min(attempt, len(_BACKOFF_SEC) - 1)])
            continue
        response.raise_for_status()
        break

    data = response.json()
    items = data.get("items", [])
    if not items:
        return None

    best = items[0].get("volumeInfo", {})
    return {
        "title": best.get("title"),
        "authors": best.get("authors", []),
        "publishedDate": best.get("publishedDate"),
        "categories": best.get("categories", []),
        "description": best.get("description"),
        "pageCount": best.get("pageCount"),
        "previewLink": best.get("previewLink"),
    }

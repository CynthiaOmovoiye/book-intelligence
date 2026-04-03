"""Google Books lookup used by the notebook and Gradio UI."""

import requests


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

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

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

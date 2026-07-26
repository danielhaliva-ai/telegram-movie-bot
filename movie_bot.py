import os
import time
from typing import Callable, Dict, List

import requests


TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/{method}"
ITUNES_SEARCH_URL = "https://itunes.apple.com/search"


def search_movies(
    query: str,
    limit: int = 5,
    requester: Callable[..., requests.Response] = requests.get,
) -> List[Dict]:
    response = requester(
        ITUNES_SEARCH_URL,
        params={"term": query, "media": "movie", "limit": limit},
        timeout=10,
    )
    response.raise_for_status()
    payload = response.json()
    return payload.get("results", [])


def build_movie_results_message(query: str, movies: List[Dict]) -> str:
    if not movies:
        return f"לא נמצאו תוצאות עבור: {query}"

    lines = [f"תוצאות עבור: {query}"]
    for movie in movies:
        title = movie.get("trackName", "ללא שם")
        release_date = (movie.get("releaseDate") or "")[:4]
        year = f" ({release_date})" if release_date else ""
        lines.append(f"- {title}{year}")
    return "\n".join(lines)


def telegram_api_request(
    token: str,
    method: str,
    payload: Dict,
    requester: Callable[..., requests.Response] = requests.post,
) -> Dict:
    response = requester(
        TELEGRAM_API_URL.format(token=token, method=method),
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def handle_message(token: str, chat_id: int, text: str) -> None:
    normalized = (text or "").strip()

    if normalized == "/start":
        reply = "שלח /movie <שם סרט> או פשוט שם של סרט כדי לחפש מהר."
    elif normalized.startswith("/movie"):
        query = normalized.replace("/movie", "", 1).strip()
        if not query:
            reply = "שימוש: /movie <שם סרט>"
        else:
            movies = search_movies(query)
            reply = build_movie_results_message(query, movies)
    elif normalized:
        movies = search_movies(normalized)
        reply = build_movie_results_message(normalized, movies)
    else:
        return

    telegram_api_request(
        token,
        "sendMessage",
        {"chat_id": chat_id, "text": reply},
    )


def run_bot(token: str) -> None:
    offset = None
    while True:
        payload = {"timeout": 30}
        if offset is not None:
            payload["offset"] = offset

        updates = telegram_api_request(token, "getUpdates", payload).get("result", [])
        for update in updates:
            offset = update["update_id"] + 1
            message = update.get("message") or {}
            chat = message.get("chat") or {}
            chat_id = chat.get("id")
            text = message.get("text", "")
            if chat_id is not None:
                handle_message(token, chat_id, text)
        time.sleep(0.2)


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN environment variable.")
    run_bot(token)


if __name__ == "__main__":
    main()

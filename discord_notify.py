import os
import requests
from typing import Optional
from datetime import datetime


def send_showtimes(
    theater_name: str,
    movies: list[dict],
    webhook_url: Optional[str] = None
) -> bool:
    webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        raise ValueError("DISCORD_WEBHOOK_URL not set")

    today_str = datetime.now().strftime("%A, %B %d, %Y")
    
    lines = [f"## 🎬 Showtimes @ {theater_name}", f"**{today_str}**\n"]
    
    for movie in movies:
        lines.append(f"### {movie['title']}")
        for fmt, times in movie["formats"].items():
            lines.append(f"**{fmt}**")
            lines.append(f"```{' • '.join(times)}```")
        lines.append("")
    
    content = "\n".join(lines)
    
    if len(content) > 2000:
        chunks = _split_message(content, 2000)
        for chunk in chunks:
            _send_message(webhook_url, chunk)
    else:
        _send_message(webhook_url, content)
    
    return True


def _send_message(webhook_url: str, content: str) -> None:
    response = requests.post(
        webhook_url,
        json={"content": content},
        timeout=10
    )
    response.raise_for_status()


def _split_message(content: str, max_length: int) -> list[str]:
    chunks = []
    lines = content.split("\n")
    current_chunk = ""
    
    for line in lines:
        if len(current_chunk) + len(line) + 1 > max_length:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = line + "\n"
        else:
            current_chunk += line + "\n"
    
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    return chunks


"""Save documents to the local data folder (JSON for the MVP; MongoDB could replace this later)."""

from pathlib import Path
from urllib.parse import urlparse


def document_name(platform: str, url: str) -> str:
    """Build a file name from the platform and the URL path: "/" -> "buscaperlas_home"."""
    path = urlparse(url).path.strip("/").replace("/", "_")
    return f"{platform}_{path or 'home'}"


def write_text_atomically(path: Path, content: str) -> None:
    """Write to a temporary file first, then swap it in.

    If the program crashes mid-write, the previous good file stays untouched.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(path.name + ".tmp")
    tmp_path.write_text(content, encoding="utf-8")
    tmp_path.replace(path)

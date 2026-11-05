import pytest
from pydantic import ValidationError
from pathlib import Path
import json

from pearltracker.document import RawPageDocument

FIXTURES = Path(__file__).parent / "fixtures"

VALID_URL = "https://www.buscaperlas.com/"


def test_rejects_html_without_main():

    html_without_main = "a" * 60_000

    with pytest.raises(ValidationError, match="no <main"):
        RawPageDocument.model_validate({"url":VALID_URL, "platform":"buscaperlas", "html":html_without_main})

def test_rejects_short_html():
    
    short_html = "<main>" + "a" * 20_000

    with pytest.raises(ValidationError, match="string_too_short"):
        RawPageDocument.model_validate({"url":VALID_URL, "platform":"buscaperlas", "html":short_html})

def test_rejects_invalid_url():
    html = "<main>" + "a" * 60_000
    invalid_url = "www.buscaperlas.co"

    with pytest.raises(ValidationError, match="url_parsing"):
        RawPageDocument.model_validate({"url":invalid_url, "platform":"buscaperlas", "html":html})

def test_accepts_real_render_page():

    real_render_page = load_real_page_html()

    doc = RawPageDocument.model_validate(
        {"url": VALID_URL, "platform": "buscaperlas", "html": real_render_page}
    )

    assert doc.platform == "buscaperlas"
    assert str(doc.url) == VALID_URL
    assert "¿Por qué una propiedad es perla?" in doc.html

def load_real_page_html() -> str:

    raw_items = json.loads((FIXTURES / "raw_buscaperlas_home.json").read_text(encoding="utf-8"))
    return raw_items[0]["html"]
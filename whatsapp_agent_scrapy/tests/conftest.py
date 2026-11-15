"""Shared pytest fixtures: pytest finds this file automatically and gives them to any test that asks."""

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def real_page_item() -> dict:
    """The item the spider yielded for the real home page (frozen copy)."""
    raw_items = json.loads((FIXTURES / "raw_buscaperlas_home.json").read_text(encoding="utf-8"))
    return {**raw_items[0], "platform": "buscaperlas"}

import json

import pytest
from scrapy.exceptions import DropItem

from pearltracker.document import ProcessedPageDocument, RawPageDocument
from pearltracker.pipelines import (
    SaveProcessedPagePipeline,
    SaveRawPagePipeline,
    SplitSectionsPipeline,
    ValidateRawPagePipeline,
)


def test_validate_drops_a_page_that_did_not_render():
    empty_page = {
        "url": "https://www.buscaperlas.com/",
        "platform": "buscaperlas",
        "html": "<html><body></body></html>",
    }

    with pytest.raises(DropItem, match="Invalid raw page"):
        ValidateRawPagePipeline().process_item(empty_page)


def test_validate_returns_a_raw_document(real_page_item):
    document = ValidateRawPagePipeline().process_item(real_page_item)

    assert isinstance(document, RawPageDocument)


def test_split_drops_a_page_whose_layout_changed(real_page_item):
    raw = ValidateRawPagePipeline().process_item(real_page_item)
    # Same page, but the <section> tags disappeared (e.g. a redesign): no sections can be found.
    redesigned = raw.model_copy(update={"html": raw.html.replace("<section", "<div")})

    with pytest.raises(DropItem, match="valid sections"):
        SplitSectionsPipeline().process_item(redesigned)


def test_full_pipeline_writes_raw_and_processed_files(real_page_item, tmp_path):
    steps = [
        ValidateRawPagePipeline(),
        SaveRawPagePipeline(tmp_path),
        SplitSectionsPipeline(),
        SaveProcessedPagePipeline(tmp_path),
    ]

    item = real_page_item
    for step in steps:
        item = step.process_item(item)

    assert isinstance(item, ProcessedPageDocument)
    assert (tmp_path / "raw" / "buscaperlas_home.json").exists()
    processed = json.loads((tmp_path / "processed" / "buscaperlas_home.json").read_text(encoding="utf-8"))
    assert len(processed["sections"]) == 8
    markdown = (tmp_path / "processed" / "buscaperlas_home.md").read_text(encoding="utf-8")
    assert "## ¿Por qué una propiedad es perla?" in markdown

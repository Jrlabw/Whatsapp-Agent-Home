"""Item pipelines: validate -> save raw -> split into sections -> save processed.

Each class does one job, in the order set by ITEM_PIPELINES in settings.py.
The real logic lives in document.py (rules), transform.py (HTML -> Markdown)
and storage.py (files); these classes only connect it to Scrapy.
"""

from pathlib import Path

from pydantic import ValidationError
from scrapy.exceptions import DropItem

from pearltracker.document import ProcessedPageDocument, RawPageDocument
from pearltracker.storage import document_name, write_text_atomically
from pearltracker.transform import sections_to_markdown, split_into_sections


class ValidateRawPagePipeline:
    """Step 1: turn the spider's dict into a RawPageDocument, or drop it if the page is invalid."""

    def process_item(self, item):
        try:
            return RawPageDocument.model_validate(item)
        except ValidationError as error:
            raise DropItem(f"Invalid raw page {item.get('url')}: {error}") from error


class SaveRawPagePipeline:
    """Step 2: keep the validated raw HTML, so we can re-transform it without crawling again."""

    def __init__(self, data_dir: Path):
        self.output_dir = data_dir / "raw"

    @classmethod
    def from_crawler(cls, crawler):
        return cls(Path(crawler.settings["DATA_DIR"]))

    def process_item(self, document: RawPageDocument):
        name = document_name(document.platform, str(document.url))
        write_text_atomically(
            self.output_dir / f"{name}.json",
            document.model_dump_json(indent=2),
        )
        return document


class SplitSectionsPipeline:
    """Step 3: split the page into Markdown sections, or drop it if the result is not valid."""

    def process_item(self, raw: RawPageDocument):
        try:
            sections = split_into_sections(raw.html, str(raw.url))
            return ProcessedPageDocument.model_validate(
                {
                    "url": raw.url,
                    "platform": raw.platform,
                    "crawled_at": raw.crawled_at,
                    "sections": sections,
                }
            )
        except ValidationError as error:
            raise DropItem(f"Could not split {raw.url} into valid sections: {error}") from error


class SaveProcessedPagePipeline:
    """Step 4: save the sections as JSON (for the LLM) and as Markdown (for human review)."""

    def __init__(self, data_dir: Path):
        self.output_dir = data_dir / "processed"

    @classmethod
    def from_crawler(cls, crawler):
        return cls(Path(crawler.settings["DATA_DIR"]))

    def process_item(self, document: ProcessedPageDocument):
        name = document_name(document.platform, str(document.url))
        write_text_atomically(
            self.output_dir / f"{name}.json",
            document.model_dump_json(indent=2),
        )
        write_text_atomically(
            self.output_dir / f"{name}.md",
            sections_to_markdown(document.sections),
        )
        return document

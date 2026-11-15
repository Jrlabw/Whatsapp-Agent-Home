"""Turn a rendered HTML page into clean, LLM-ready Markdown sections.

These are pure functions: they receive text and return data, and they know nothing
about Scrapy. That makes them fast to test and reusable by later pipelines.
"""

import re

from markdownify import MarkdownConverter
from parsel import Selector

from pearltracker.document import PageSection

# Each <section> inside <main> is one topic of the page.
SECTION_SELECTOR = "main section"
# The section title is its first <h1> or <h2>, with all inner whitespace collapsed.
TITLE_XPATH = "normalize-space((.//h1 | .//h2)[1])"
# Keep the text of these tags but drop the markup: buttons and images mean nothing to an LLM.
TAGS_TO_STRIP = ["button", "img"]
# Sections deliberately left out.
# "Perlas destacadas" shows demo listings: the agent must not present them as real offers.
EXCLUDED_SECTION_TITLES = frozenset({"Perlas destacadas"})

class LlmMarkdownConverter(MarkdownConverter):
    """Markdown for an LLM: drop normal links, but keep the email of mailto: links."""

    def convert_a(self, el, text, parent_tags):
        href = el.get("href", "")
        if href.startswith("mailto:"):
            email = href.removeprefix("mailto:")
            return f"{text} ({email})"

        return text



    
def html_to_markdown(html: str) -> str:
    """Convert an HTML fragment to Markdown and tidy the whitespace."""
    markdown = LlmMarkdownConverter(heading_style="ATX", bullets="-", strip=TAGS_TO_STRIP).convert(html)
    lines = (line.rstrip() for line in markdown.splitlines())
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def split_into_sections(html: str, url: str) -> list[PageSection]:
    """Split the <main> of a page into validated sections, keeping the page order."""
    page = Selector(text=html)
    sections = []
    for position, section in enumerate(page.css(SECTION_SELECTOR)):
        title = section.xpath(TITLE_XPATH).get()
        if title in EXCLUDED_SECTION_TITLES:
            continue
        sections.append(
            PageSection.model_validate(
                {
                    "title": title,
                    "url": url,
                    "text": html_to_markdown(section.get()),
                    "position": position,
                }
            )
        )
    return sections


def sections_to_markdown(sections: list[PageSection]) -> str:
    """Join the sections into one Markdown document, for people to review."""
    return "\n\n---\n\n".join(section.text for section in sections) + "\n"

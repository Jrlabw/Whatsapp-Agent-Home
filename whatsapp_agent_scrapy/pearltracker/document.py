from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator
from datetime import datetime, timezone


class RawPageDocument(BaseModel):
    """A web page exactly as the crawler downloaded it (rendered HTML)."""

    model_config = ConfigDict(str_strip_whitespace=True, frozen=True)

    url: HttpUrl
    platform: str = Field(min_length=1)
    html: str = Field(min_length=50_000)
    crawled_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))

    @field_validator("html")
    @classmethod
    def html_must_have_main(cls, value:str) -> str:
        if "<main" not in value:
            raise ValueError("HTML has no <main> element: the page probably did not render")
        return value


class PageSection(BaseModel):

    model_config= ConfigDict(str_strip_whitespace=True, frozen=True)
    
    title: str = Field(min_length=1)
    url: HttpUrl
    text: str = Field(min_length=50)
    position: int = Field(ge=0)


# The real home page has 9 sections (8 after exclusions). Far fewer means the layout changed.
MIN_SECTIONS_PER_PAGE = 5


class ProcessedPageDocument(BaseModel):
    """A page split into clean Markdown sections, ready to be chunked for the LLM."""

    model_config = ConfigDict(frozen=True)

    url: HttpUrl
    platform: str = Field(min_length=1)
    crawled_at: datetime
    sections: list[PageSection] = Field(min_length=MIN_SECTIONS_PER_PAGE)


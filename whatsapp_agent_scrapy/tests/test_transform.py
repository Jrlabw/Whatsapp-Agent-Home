from pearltracker.transform import html_to_markdown, sections_to_markdown, split_into_sections


def test_html_to_markdown_keeps_headings_and_drops_links():
    html = '<h2>Planes</h2><p>Precio: <a href="/x">ver más</a></p>'

    markdown = html_to_markdown(html)

    assert markdown == "## Planes\n\nPrecio: ver más"


def test_splits_real_page_into_its_sections(real_page_item):
    sections = split_into_sections(real_page_item["html"], real_page_item["url"])

    titles = [section.title for section in sections]
    assert len(sections) == 8
    assert titles[0] == "Encuentra la oportunidad antes que otros"
    assert "¿Por qué una propiedad es perla?" in titles
    assert "Elige cuánto quieres anticiparte" in titles

def test_contain_contact_information(real_page_item):
    sections = split_into_sections(real_page_item["html"], real_page_item["url"])
    plans = next(s for s in sections if s.title =="Elige cuánto quieres anticiparte")
    
    assert "ventas@buscaperlas.co" in plans.text

    
def test_excludes_demo_listings_section(real_page_item):
    sections = split_into_sections(real_page_item["html"], real_page_item["url"])

    assert "Perlas destacadas" not in [section.title for section in sections]


def test_sections_keep_page_order(real_page_item):
    sections = split_into_sections(real_page_item["html"], real_page_item["url"])

    positions = [section.position for section in sections]
    assert positions == sorted(positions)


def test_sections_contain_markdown_not_html(real_page_item):
    sections = split_into_sections(real_page_item["html"], real_page_item["url"])

    for section in sections:
        assert "<div" not in section.text
        assert "<span" not in section.text


def test_plans_section_has_the_plan_names(real_page_item):
    sections = split_into_sections(real_page_item["html"], real_page_item["url"])
    plans = next(s for s in sections if s.title == "Elige cuánto quieres anticiparte")

    for plan in ("### Gratis", "### Pro", "### Empresa"):
        assert plan in plans.text


def test_sections_to_markdown_separates_sections(real_page_item):
    sections = split_into_sections(real_page_item["html"], real_page_item["url"])

    markdown = sections_to_markdown(sections)

    assert markdown.count("\n---\n") == len(sections) - 1

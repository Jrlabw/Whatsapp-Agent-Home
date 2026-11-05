import scrapy
from scrapy_playwright.page import PageMethod





class BuscaperlasHomeSpider(scrapy.Spider):
    name = "buscaperlas_home"
    START_URL = "https://www.buscaperlas.com/"
    READY_SELECTOR = "h2:has-text(' con más contexto y menos ruido')"

    async def start(self):
        yield scrapy.Request(
            url= self.START_URL,
            meta={
                "playwright":True,
                "playwright_page_methods":[

                    PageMethod("wait_for_selector", self.READY_SELECTOR,timeout=60_000)
                ],
            },
            callback=self.parse

        )    
    def parse(self,response):
        yield{
            "url": response.url,
            "html": response.text
        }

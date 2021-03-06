import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from oddo.items import Article


class OddoSpider(scrapy.Spider):
    name = 'oddo'
    start_urls = ['http://www.oddo.eu/en/News/All']

    def parse(self, response):
        links = response.xpath('//div[@class="card-item col-xl-4 col-sm-6"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//a[@id="loadMore"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//span[@class="text-12 font-normal text-date"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="article-page"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()

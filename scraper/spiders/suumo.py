import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import re


class SuumoSpider(CrawlSpider):
    name = "suumo"
    allowed_domains = ["suumo.jp"]
    start_urls = [
        'http://suumo.jp/jj/chintai/ichiran/FR301FC005/?ar=030&bs=040&ra=013&rn=0005&ek=000539110&sngz=&po2=99&po1=01'
    ]

    rules = [
        Rule(LinkExtractor(allow=['suumo.jp/jj/chintai/ichiran/'])),
        Rule(LinkExtractor(allow=['^https://suumo.jp/chintai/tokyo/sc_(?:meguro)/']), callback='parse_item')
    ]

    def parse_item(self, response):
        NUMBER_PATTERN = '\d+(?:\.\d+)?'
        def parse_number(selector):
            maybe_num_str = selector
            if maybe_num_str and len(maybe_num_str) > 0:
                return float(maybe_num_str)
            else:
                return 0

        item = {}

        match = re.search('/jnc_(\d+)/', response.url)
        if match is not None:
            item['id'] = match[1]

        for txt in response.css('.detailvalue-txt'):
            first_span_text = txt.css('span::text').extract_first()
            if first_span_text and first_span_text.strip() == '敷':
                item['shikikin'] = parse_number(txt.css('span::text').re_first(NUMBER_PATTERN))
            if first_span_text and first_span_text.strip() == '礼':
                item['reikin'] = parse_number(txt.css('span::text').re_first(NUMBER_PATTERN))

        item['kanrihi'] = parse_number(response.css('.detailvalue-item-txt::text').re_first('(%s)円' % NUMBER_PATTERN))

        item['address'] = response.css('.detailvalue-txt::text').re_first('東京.+')
        item['size'] = parse_number(response.css('.detailvalue-txt::text').re_first('(%s)m' % NUMBER_PATTERN))
        age = response.css('.detailvalue-txt::text').re_first('築(\d+)')
        if age:
            item['age'] = int(age)
        else:
            if response.css('.detailvalue-txt::text').re_first('新築'):
                item['age'] = 0

        yield {
            **item,
            **{
                'title': response.css('title::text').extract_first(),
                'url': response.url,
                'keywords': response.css('meta[name="keywords"]::attr(content)').extract_first(),
                'info': ",".join([ re.sub('\\r|\\n', '', t).strip() for t in response.css('.detailinfo-col span::text, .detailinfo-col .detailvalue-txt::text').extract()]),
                'chinryo': parse_number(response.css('.detailvalue-item-accent::text').re_first('(%s)万円' % NUMBER_PATTERN)),
            }
        }

    # def parse(self, response):
    #     next_page = response.css('p.pagination-parts a::attr(href)').extract()[-1]
    #
    #     if next_page is not None:
    #         next_page = response.urljoin(next_page)
    #         yield scrapy.Request(next_page, callback=self.parse)

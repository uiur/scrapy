import scrapy


class SuumoSpider(scrapy.Spider):
    name = "suumo"
    allowed_domains = ["suumo.jp"]
    start_urls = [
        'http://suumo.jp/jj/chintai/ichiran/FR301FC005/?ar=030&bs=040&ra=013&rn=0005&ek=000539110&sngz=&po2=99&po1=01'
    ]

    def parse(self, response):
        for property in response.css('.property'):
            yield {
                'title': property.css('.property_inner-title > a::text').extract_first(),
                'point': property.css('.detailbox-property-point::text').extract_first(),
                'url': property.css('.property_inner-title a::attr(href)').extract_first(),
            }

        next_page = response.css('p.pagination-parts a::attr(href)').extract()[-1]

        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

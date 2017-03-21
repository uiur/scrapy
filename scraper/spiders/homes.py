# -*- coding: utf-8 -*-
import scrapy

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
import re


class HomesSpider(CrawlSpider):
    name = "homes"
    allowed_domains = ["www.homes.co.jp"]
    start_urls = [
        'http://www.homes.co.jp/chintai/tokyo/meguro_00576-st/list/',
        'http://www.homes.co.jp/chintai/tokyo/ebisu_00577-st/list/',
    ]

    rules = [
        Rule(LinkExtractor(allow=['http://www.homes.co.jp/chintai/tokyo/meguro_00576-st/list/'])),
        Rule(LinkExtractor(allow=['www.homes.co.jp/chintai/ky-']), callback='parse_item')
    ]

    def parse_item(self, response):
        NUMBER_PATTERN = '\d+(?:\.\d+)?'

        def shikirei_to_num(target, chinryo):
            if target == '無':
                return 0

            match = re.search('(\d+)ヶ月', target)
            if match:
                month = int(match[1])
                return month * chinryo

            match = re.search('(%s)万円' % NUMBER_PATTERN, target)
            if match:
                return float(match[1])

        if len(response.css('.mod-bukkenNotFound')) > 0:
            return None

        item = {}
        kanrihi = response.css('#chk-bkc-moneyroom::text').re_first('([\d,]+)円')
        if kanrihi:
            item['kanrihi'] = float(re.sub(',', '', kanrihi)) / 10000

        item['chinryo'] = float(response.css('#chk-bkc-moneyroom .num span::text').extract_first())

        shiki, rei = [ s.strip() for s in response.css('#chk-bkc-moneyshikirei::text').extract_first().split('/') ]

        item['shikikin'] = shikirei_to_num(shiki, item['chinryo'])
        item['reikin'] = shikirei_to_num(rei, item['chinryo'])

        year, month = response.css('#chk-bkc-kenchikudate::text').re('(\d+)年(\d+)月')
        item['built_at'] = datetime(int(year), int(month), 1).strftime('%Y-%m-%d %H:%M:%S')

        item['keywords'] = '\t'.join([re.sub('、', '', text).strip()  for text in response.css('#prg-bukkenNotes li::text').extract()])

        match = re.search('/ky-([a-f0-9]+)/', response.url)

        result = {
            'id': match and match[1],
            'url': response.url,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'posted_at': datetime.strptime('2017/03/10', '%Y/%m/%d').strftime('%Y-%m-%d %H:%M:%S'),
            'name': response.css('#chk-bkh-name::text').extract_first(),
            'address': response.css('#chk-bkc-fulladdress::text').extract_first().strip(),
            'size': float(response.css('#chk-bkc-housearea::text').re_first('(%s)m²' % NUMBER_PATTERN).strip()),
        }

        result.update(item)
        return result

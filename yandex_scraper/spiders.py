#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import scrapy
import urllib


class YandexSpider(scrapy.Spider):
    name = 'yandex_spider'
    start_urls = ['https://www.yandex.com/search/?%s']
    custom_settings = {
        'ITEM_PIPELINES': {
            'yandex_scraper.pipelines.YandexScraperPipeline': 400
        }
    }

    def __init__(self, search_phrase: str, pages: int, callback_url='') -> None:
        if not isinstance(pages, int):
            pages = int(pages)
        self.search_phrase = search_phrase
        self.pages = pages
        self.callback_url = callback_url

    def start_requests(self):
        for url in self.start_urls:
            for page in range(self.pages):
                yield self.make_requests_from_url(url % urllib.parse.urlencode({
                    'text': self.search_phrase,
                    'p': page
                }))

    def parse(self, response: scrapy.http.Response) -> None:
        ensure_response_200(response)
        for post in response.css('li.serp-item'):
            yield {
                'data': post.extract()
            }


def ensure_response_200(response: scrapy.http.Response) -> None:
    if response.status != 200:
        raise Exception('Expected HTTP response 200')

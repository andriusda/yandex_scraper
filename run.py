#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import getopt
import redis
from scrapy.signals import spider_closed
from scrapy.crawler import CrawlerProcess, Crawler
from scrapy.utils.project import get_project_settings
from yandex_scraper.spiders import YandexSpider
from yandex_scraper.pipelines import format_callback_url
from FlaskApp.config import REDIS_HOST, REDIS_PORT, REDIS_DB


def parse_args(argv):
    keywords = ''
    pages = 0
    callback_url = ''
    try:
        opts, args = getopt.getopt(argv, "hk:p:c:r:", ["keywords=", "pages=", "callback_url=", "read="])
        for opt, arg in opts:
            if opt == '-h':
                print('run.py -k <keywords> -o <pages> -c <callback_url> or -r <read>')
                sys.exit()
            elif opt in ("-r", "--read"):
                db = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
                if db.get(arg):
                    response = format_callback_url(arg)
                    print(response)
                    return {'response': response}
                raise Exception('Task does not exist')
            elif opt in ("-k", "--keywords"):
                keywords = arg
            elif opt in ("-p", "--pages"):
                pages = int(arg)
            elif opt in ("-c", "--callback_url"):
                callback_url = arg
        if not keywords or not pages:
            raise KeyError
    except KeyError:
        print('run.py -k <keywords> -o <pages> -c <callback_url> or -r <read>')
        sys.exit(2)
    return {
        'keywords': keywords,
        'pages': pages,
        'callback_url': callback_url
    }


def main(argv):
    args = parse_args(argv)
    if args.get('response'):
        return args['response']
    keywords, pages, callback_url = args['keywords'], args['pages'], args['callback_url']

    crawler = Crawler(YandexSpider, settings=get_project_settings())

    tasks = []

    def get_task_id(**kwargs):
        if kwargs.get('spider') and hasattr(kwargs['spider'], 'task_id'):
            tasks.append(kwargs['spider'].task_id)

    crawler.signals.connect(get_task_id, signal=spider_closed)
    process = CrawlerProcess(get_project_settings())
    process.crawl(crawler, keywords, pages, callback_url)
    process.start()
    if tasks:
        print('Task ID:', tasks[0])
        return tasks[0]
    raise Exception('No data has been retrieved.')


if __name__ == "__main__":
    main(sys.argv[1:])

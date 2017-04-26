#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import redis
from FlaskApp import config


INITIAL_DB_STRING_LENGTH = 4


def format_callback_url(task_id):
    return '{}/task?id={}'.format(config.SERVER_NAME, task_id)


class YandexScraperPipeline(object):
    def __init__(self):
        self.redis = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB)
        keys = [int(key) for key in self.redis.keys()]
        self.key = (int(max(keys)) + 1) if keys else 1

    def open_spider(self, spider):
        self.redis.set(self.key, '<ol>')

    def close_spider(self, spider):
        if len(self.redis.get(self.key)) == INITIAL_DB_STRING_LENGTH:
            self.redis.delete(self.key)
            return
        self.redis.append(self.key, '</ol>')
        spider.task_id = self.key
        if spider.callback_url:
            requests.get(spider.callback_url, {'url': format_callback_url(self.key)})

    def process_item(self, item, spider):
        if item.get('data'):
            self.redis.append(self.key, item['data'])
        return item

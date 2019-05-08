# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ChinataxItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    taxpayer_name = scrapy.Field()
    taxpayer_id = scrapy.Field()
    org_code = scrapy.Field()
    reg_addr = scrapy.Field()
    legal_person_info = scrapy.Field()
    financial_admin_info = scrapy.Field()
    intermediary_info = scrapy.Field()
    case_type = scrapy.Field()
    illegal_fact = scrapy.Field()
    punishment = scrapy.Field()
    pass

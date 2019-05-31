# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy import FormRequest
from chinatax.items import ChinataxItem
import re
import json


# 请求头
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Host': 'hd.chinatax.gov.cn',
    'Upgrade-Insecure-Requests': '1',
}


class ChinataxSpider(scrapy.Spider):
    name = 'chinatax'
    allowed_domains = ['hd.chinatax.gov.cn']
    request_body = {}

    def __init__(self):
        '读取请求体'
        filename = 'body.json'
        with open(filename, 'r') as f:
            self.request_body = json.load(f)

    def start_requests(self):
        '模拟访问主页'
        return [Request(
            headers=headers,
            url='http://hd.chinatax.gov.cn/xxk',
            callback=self.parse,
            dont_filter=True
        )]

    def parse(self, response):
        '获取案件列表'
        return [FormRequest.from_response(
            response,
            url='http://hd.chinatax.gov.cn/xxk/action/ListXxk.do',
            formdata=self.request_body,
            callback=self.parse_list,
            dont_filter=True
        )]

    def parse_list(self, response):
        '获取案件的url和下一页'
        href_list = response.xpath('//*[@id="searchForm"]/table[2]/tr/td/a/@href').extract()
        top_bar = response.xpath('//*[@id="searchForm"]/table[1]//tr/td').extract()[0]
        have_next = re.search('下一页', top_bar)
        if have_next is not None:
            self.request_body['cPage'] = str(int(self.request_body['cPage']) + 1)
            yield FormRequest.from_response(
                response,
                headers=headers,
                url='http://hd.chinatax.gov.cn/xxk/action/ListXxk.do',
                formdata=self.request_body,
                callback=self.parse_list,
                dont_filter=True
            )
        for href in href_list:
            yield Request(
                headers=headers,
                url='http://hd.chinatax.gov.cn/xxk/action/' + href,
                callback=self.parse_detail,
                dont_filter=True
            )

    def parse_detail(self, response):
        '获取案件详情'
        items = ChinataxItem()
        info = response.xpath('/html/body/table/tr/td/table')
        keys = ['taxpayer_name', 'taxpayer_id', 'org_code', 'reg_addr',
                'legal_person_info', 'financial_admin_info', 'intermediary_info', 'case_type']
        for i in range(1, 9):
            temp = info.xpath('./tr[' + str(i) + ']/td[2]/text()').extract()
            items[keys[i - 1]] = temp[0] if len(temp) > 0 else ''
        illegal_fact = info.xpath('./tr[9]/td[2]/text()').extract()
        items['illegal_fact'] = illegal_fact[0] if len(illegal_fact) > 0 else ''
        punishment = info.xpath('./tr[9]/td[2]/text()').extract()
        items['punishment'] = punishment[1] if len(punishment) > 0 else ''
        yield items

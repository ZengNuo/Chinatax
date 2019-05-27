# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy import FormRequest
from chinatax.items import ChinataxItem
import re


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

request_body = {
    # 查询类型：法人-24 自然人-25
    'categeryid': '24',

    # 查询关键字：
    # 法人类型：纳税人名称-02 纳税人识别号-03 组织机构代码-04 法定代表人或负责人姓名-06  负有直接责任的财务负责人姓名-09
    # 自然人类型：姓名-09
    'querystring24': 'articlefield02',

    # 暂未发现用途，先忽略
    'querystring25': 'articlefield02',

    # 查询字符串
    'queryvalue': '北京',

    # 页码
    'cPage': '1',

    # 页面切换次数
    'scount': '5',
}


class ChinataxSpider(scrapy.Spider):
    name = 'chinatax'
    allowed_domains = ['hd.chinatax.gov.cn']
    #
    # type = input("查询类型（1.法人  2.自然人）：")
    # if type == '1':
    #     request_body['categeryid'] = '24'
    #     keyword = input("查询关键字（1.纳税人名称  2.纳税人识别码  3.组织机构代码  4.法定代表人或负责人姓名  5.负有直接责任的财务负责人姓名）：")
    #     if keyword == '1':
    #         request_body['querystring24'] = 'articlefield02'
    #     elif keyword == '2':
    #         request_body['querystring24'] = 'articlefield03'
    #     elif keyword == '3':
    #         request_body['querystring24'] = 'articlefield04'
    #     elif keyword == '4':
    #         request_body['querystring24'] = 'articlefield06'
    #     elif keyword == '5':
    #         request_body['querystring24'] = 'articlefield09'
    #     else:
    #         print("输入不正确")
    #         exit(0)
    # elif type == '2':
    #     request_body['categeryid'] = '25'
    #     keyword = input("查询关键字（1.姓名）：")
    #     if keyword == '1':
    #         request_body['querystring24'] = 'articlefield09'
    # else:
    #     print("输入不正确")
    #     exit(0)
    #
    # value = input("请输入查询字符串：")
    # request_body['queryvalue'] = value

    def start_requests(self):
        '模拟访问主页'
        return [Request(
            headers=headers,
            url='http://hd.chinatax.gov.cn/xxk',
            callback=self.parse
        )]

    def parse(self, response):
        '获取案件列表'
        return [FormRequest.from_response(
            response,
            url='http://hd.chinatax.gov.cn/xxk/action/ListXxk.do',
            formdata=request_body,
            callback=self.parse_list
        )]

    def parse_list(self, response):
        '获取案件的url和下一页'
        href_list = response.xpath('//*[@id="searchForm"]/table[2]/tr/td/a/@href').extract()

        top_bar = response.xpath('//*[@id="searchForm"]/table[1]//tr/td').extract()[0]
        have_next = re.search('下一页', top_bar)

        if have_next is not None:
            request_body['cPage'] = str(int(request_body['cPage']) + 1)
            yield FormRequest.from_response(
                response,
                headers=headers,
                url='http://hd.chinatax.gov.cn/xxk/action/ListXxk.do',
                formdata=request_body,
                callback=self.parse_list
            )

        for href in href_list:
            yield Request(
                headers=headers,
                url='http://hd.chinatax.gov.cn/xxk/action/' + href,
                callback=self.parse_detail
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

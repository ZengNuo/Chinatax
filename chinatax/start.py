from scrapy.cmdline import execute
import json

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
    'queryvalue': '阿',
    # 页码
    'cPage': '1',
    # 页面切换次数
    'scount': '5',
}


if __name__ == '__main__':
    '输入查询信息'
    type = input("查询类型（1.法人  2.自然人）：")
    if type == '1':
        request_body['categeryid'] = '24'
        keyword = input("查询关键字（1.纳税人名称  2.纳税人识别码  3.组织机构代码  4.法定代表人或负责人姓名  5.负有直接责任的财务负责人姓名）：")
        if keyword == '1':
            request_body['querystring24'] = 'articlefield02'
        elif keyword == '2':
            request_body['querystring24'] = 'articlefield03'
        elif keyword == '3':
            request_body['querystring24'] = 'articlefield04'
        elif keyword == '4':
            request_body['querystring24'] = 'articlefield06'
        elif keyword == '5':
            request_body['querystring24'] = 'articlefield09'
        else:
            print("输入不正确")
            exit(0)
    elif type == '2':
        request_body['categeryid'] = '25'
        keyword = input("查询关键字（1.姓名）：")
        if keyword == '1':
            request_body['querystring24'] = 'articlefield09'
    else:
        print("输入不正确")
        exit(0)
    value = input("请输入查询字符串：")
    request_body['queryvalue'] = value

    filename = 'body.json'
    with open(filename, "w") as f:
        json.dump(request_body, f)

    # 启动爬虫
    execute(['scrapy', 'crawl', 'chinatax'])

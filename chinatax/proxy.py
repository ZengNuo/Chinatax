# *-* coding:utf-8 *-*
from bs4 import BeautifulSoup
from multiprocessing import Process, Queue
import re
import time
import requests


class Proxies(object):
    """docstring for Proxies"""

    def __init__(self, page=1):
        self.proxies = []
        self.verify_pro = []
        self.page = page
        self.headers = {
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8'
        }
        self.get_proxies_xici()
        self.get_proxies_bajiu()

    def get_proxies_xici(self):
        if requests.get('http://www.xicidaili.com', headers=self.headers, timeout=2).status_code != 200:
            print('error in server: xicidaili.com')
            return
        page = 1
        page_stop = page + self.page
        print('crawling data from www.xicidaili.com...')
        while page < page_stop:
            url_nn = 'http://www.xicidaili.com/nn/%d' % page
            html = requests.get(url_nn, headers=self.headers).content
            soup = BeautifulSoup(html, 'lxml')
            ip_list = soup.find(id='ip_list')
            for odd in ip_list.find_all(class_='odd'):
                protocol = odd.find_all('td')[5].get_text().lower() + '://'
                self.proxies.append(protocol + ':'.join([x.get_text() for x in odd.find_all('td')[1:3]]))
            page += 1
            time.sleep(1)

    def get_proxies_bajiu(self):
        if requests.get('http://www.89ip.cn', headers=self.headers, timeout=2).status_code != 200:
            print('error in server: 89ip.cn')
            return
        print('crawling data from www.89ip.com...')
        html = requests.get('http://www.89ip.cn/tqdl.html?api=1&num=100').text
        ip_list = re.split(r'<br>', html)
        ip_list = ip_list[:-1]
        ip_list = ip_list[2:]
        for odd in ip_list:
            proxy = 'http://' + odd
            # print(proxy)
            self.proxies.append(proxy)

    def verify_proxies(self):
        if len(self.proxies) < 1:
            return
        # 没验证的代理
        old_queue = Queue()
        # 验证后的代理
        new_queue = Queue()
        print('verify proxy........')
        works = []
        for _ in range(15):
            works.append(Process(target=self.verify_one_proxy, args=(old_queue, new_queue)))
        for work in works:
            work.start()
        for proxy in self.proxies:
            old_queue.put(proxy)
        for work in works:
            old_queue.put(0)
        for work in works:
            work.join()
        self.proxies = []
        while 1:
            try:
                self.proxies.append(new_queue.get(timeout=1))
            except:
                break
        print('verify_proxies done!')

    def verify_one_proxy(self, old_queue, new_queue):
        while 1:
            proxy = old_queue.get()
            if proxy == 0: break
            protocol = 'https' if 'https' in proxy else 'http'
            proxies = {protocol: proxy}
            try:
                if requests.get('http://hd.chinatax.gov.cn/xxk/action/ListXxk.do', proxies=proxies, timeout=2).status_code == 200:
                    print('success %s' % proxy)
                    new_queue.put(proxy)
            except:
                print('fail %s' % proxy)


if __name__ == '__main__':
    a = Proxies(2)
    a.verify_proxies()
    proxy = a.proxies
    with open('proxies.txt', 'w+') as f:
        for item in proxy:
            f.write(item + '\n')

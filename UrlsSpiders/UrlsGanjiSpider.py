import re
import time

from Downloader.Downloader import downloadHttpsResponse
from Utils.RedisUtils import RedisUtils
from Utils.Utils import getCurrentTime

name = 'SpiderGanji'
rootUrls = ["http://gz.ganji.com/fang1/", "http://sz.ganji.com/fang1/",
            "http://bj.ganji.com/fang1/", "http://sh.ganji.com/fang1/"]

redis = RedisUtils()


def parse_page(page_url):
    response = downloadHttpsResponse(page_url)
    base_url = re.findall(r'http.*com', page_url)[0]
    lis = response.xpath('//div[@class="f-list-item ershoufang-list"]')
    total = len(lis)
    new_urls = 0
    old_urls = 0
    for li in lis:
        try:
            url = li.xpath('./dl/dd/a/@href').extract()[0]
            if not re.search(r'http:', url):
                url = '%s%s' % (base_url, url)
            if redis.add_to_redis(name, url):
                print('%s %s新房源链接: %s' % (getCurrentTime(), name, url))
                new_urls += 1
            else:
                print('%s %s旧房源链接: %s' % (getCurrentTime(), name, url))
                old_urls += 1
        except:
            pass
    print('%s %s新房源数量: %d, 旧房源数量: %d' % (getCurrentTime(), name, new_urls, old_urls))
    if new_urls / total <= 0.4:
        print('%s %s旧房源过多，停止采集%s' % (getCurrentTime(), name, page_url))
        return None

    try:
        _next_url = response.xpath('//a[@class="next"]/@href').extract()[0]
        next_url = base_url + _next_url
        return next_url
    except:
        return None


def crawlRoot(root):
    index = 1
    nextpage = parse_page(root)
    while index <= 30:
        time.sleep(30)
        if nextpage is None:
            return
        nextpage = parse_page(nextpage)
        index += 1


def crawlGanjiUrls():
    for item in rootUrls:
        crawlRoot(item)



if __name__ == '__main__':
    crawlGanjiUrls()

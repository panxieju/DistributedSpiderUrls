import re
import time

from Downloader.Downloader import downloadHttpsResponse
from Utils.RedisUtils import RedisUtils
from Utils.Utils import getCurrentTime

name = 'SpiderFang'
rootUrls = [
    "http://zu.gz.fang.com/",
    "http://zu.sh.fang.com/",
    "http://zu.fang.com/",
    "http://zu.sz.fang.com/", ]

redis = RedisUtils()

# 解析一个页面下的所有房源链接，并获取下一页的链接
def parsePage(page_url):
    base_url = re.findall(r'http.*com', page_url)[0]
    if re.match('http://zu\.\w+\.fang\.com', page_url):
        response = downloadHttpsResponse(page_url)
    else:
        response = downloadFangBeijing(page_url)
    lis = response.xpath('//div[@class="houseList"]/dl')
    total = len(lis)
    new_urls = 0
    old_urls = 0
    for li in lis:
        try:
            _url = li.xpath('.//p[@class="title"]/a/@href').extract()[0]
            url = base_url + _url
            if redis.add_to_redis(name, url):
                print('%s %s新房源链接: %s' % (getCurrentTime(), name, url))
                new_urls += 1
            else:
                print('%s %s旧房源链接: %s' % (getCurrentTime(), name, url))
                old_urls += 1
        except:
            pass
    print('新房源数量: %d, 旧房源数量: %d' % (new_urls, old_urls))
    if new_urls / total <= 0.4:
        print('%s旧房源过多，停止采集%s' % (getCurrentTime(), page_url))
        return None

    try:
        _next_url = response.xpath('//div[@class="fanye"]/a[text()="下一页"]/@href').extract()[0]
        next_url = base_url + _next_url
        return next_url
    except:
        return None


# 循环解析一个城市的所有房源链接
def crawlRoot(root):
    index = 1
    nextpage = parsePage(root)
    while index <= 30:
        time.sleep(30)
        if nextpage is None:
            return
        nextpage = parsePage(nextpage)
        index += 1


def crawlFangUrls():
    for item in rootUrls:
        crawlRoot(item)



if __name__ == '__main__':
    crawlFangUrls()

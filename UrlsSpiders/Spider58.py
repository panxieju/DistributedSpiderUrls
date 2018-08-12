import re
import time

from Downloader.Downloader import *
from Utils import Utils
from Utils.RedisUtils import RedisUtils

name = 'Spider58'
rootUrls = ["http://gz.58.com/chuzu/",
            "http://sz.58.com/chuzu/",
            "http://bj.58.com/chuzu/",
            "http://sh.58.com/chuzu/"
            ]

redis = RedisUtils()
# 解析一个页面下的所有房源链接，并获取下一页的链接
def parsePage(page_url):
    response = downloadHttpResponse(page_url)
    lis = response.xpath('//ul[@class="listUl"]/li')
    total = len(lis)
    new_urls = 0
    old_urls = 0
    for li in lis:
        try:
            url_ = li.xpath('./div[@class="img_list"]/a/@href').extract()[0]
            if re.match(r'^http', url_):
                url = url_
            else:
                url = "http:%s"%url_

            if redis.add_to_redis(name, url):
                print('%s %s新房源链接: %s' % (Utils.getCurrentTime(), name, url))
                new_urls += 1
            else:
                print('%s %s旧房源链接: %s' % (Utils.getCurrentTime(), name, url))
                old_urls += 1
        except:
            pass
    print('新房源数量: %d, 旧房源数量: %d' % (new_urls, old_urls))
    if new_urls / total <= 0.4:
        print('%s旧房源过多，停止采集%s' % (Utils.getCurrentTime(), page_url))
        return None

    try:
        next_url = response.xpath('//div[@class="pager"]/a[@class="next"]/@href').extract()[0]
        return next_url
    except:
        return None


# 循环解析一个城市的所有房源链接
def crawlRoot(root):
    index = 1
    nextpage = parsePage(root)
    while nextpage is not None:
        time.sleep(random.randint(10,20))
        nextpage = parsePage(nextpage)
        index += 1
        if index > 30:
            break


def crawl58Urls():
    for item in rootUrls:
        crawlRoot(item)



if __name__ == '__main__':
    crawl58Urls(rootUrls[0])

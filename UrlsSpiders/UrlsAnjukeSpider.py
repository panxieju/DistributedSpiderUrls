import time

from Downloader.Downloader import downloadHttpsResponse
from Utils.RedisUtils import RedisUtils
from Utils.Utils import getCurrentTime

name = 'SpiderAnjuke'
rootUrls = ['https://gz.zu.anjuke.com/', 'https://sz.zu.anjuke.com/',
            'https://bj.zu.anjuke.com/', 'https://sh.zu.anjuke.com/']

redis = RedisUtils()


def parse_page(page_url):
    response = downloadHttpsResponse(page_url)
    if response is None:
        return None
    lis = response.xpath('//div[@class="list-content"]/div/@link').extract()
    total = len(lis)
    new_urls = 0
    old_urls = 0
    for url in lis:
        try:
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
        next_url = response.xpath('//div[@class="multi-page"]/a[@class="aNxt"]/@href').extract_first()
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

def crawlAnjukeUrls():
    for item in rootUrls:
        crawlRoot(item)


if __name__ == '__main__':
    crawlAnjukeUrls()

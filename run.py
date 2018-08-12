import queue
import threading

import grpc
import time

import message_pb2_grpc
from UrlsSpiders.Spider58 import crawl58Urls
from UrlsSpiders.UrlsAnjukeSpider import crawlAnjukeUrls
from UrlsSpiders.UrlsFangSpider import crawlFangUrls
from UrlsSpiders.UrlsGanjiSpider import crawlGanjiUrls
from Utils.Utils import getIp, getTime
from message_pb2 import Register

'''
    这是一个用于爬取房源列表页面的链接，从列表文件中爬取每个一个房源详情的下一级链接
'''
spiderStatus = dict()


class UrlsSpider(object):
    idle = True
    isSpider58Running = False
    isSpiderAnjukeRunning = False
    isSpiderGanjiRunning = False
    isSpiderFangRunning = False
    status = queue.Queue(maxsize=10)
    thread58 = threading.Thread(target=crawl58Urls)
    threadAnjuke = threading.Thread(target=crawlAnjukeUrls)
    threadFang = threading.Thread(target=crawlFangUrls)
    threadGanji = threading.Thread(target=crawlGanjiUrls)

    def getStatus(self):
        status = list()
        import message_pb2
        status.append(message_pb2.Status(spider="Spider58", timestamp=getTime(), isalive=self.thread58.is_alive()))
        status.append(
            message_pb2.Status(spider="SpiderAnjuke", timestamp=getTime(), isalive=self.threadAnjuke.is_alive()))
        status.append(message_pb2.Status(spider="SpiderFang", timestamp=getTime(), isalive=self.threadFang.is_alive()))
        status.append(
            message_pb2.Status(spider="SpiderGanji", timestamp=getTime(), isalive=self.threadGanji.is_alive()))
        return status

    #构建Hello信息
    def registerInfo(self):
        return Register(
            host=getIp(),
            timestamp=getTime(),
            status=self.getStatus()
        )

    #向服务器发送hello, 从服务器中获取需要爬取的爬虫名称
    def hello(self):
        channel = grpc.insecure_channel('39.108.51.140:16305')
        stub = message_pb2_grpc.SpiderServerStub(channel)
        ack = stub.keepalive(self.registerInfo())
        print("Receive ack from ", ack.work, ack.spider, ack.timestamp)
        if ack.work and len(ack.spider) > 0:
            for spider in ack.spider:
                if not self.isCrawling(spider=spider):
                    self.runSpider(spider=spider)

    def isCrawling(self, spider):
        if spider == 'Spider58':
            return self.thread58.is_alive()
        if spider == 'SpiderAnjuke':
            return self.threadAnjuke.is_alive()
        if spider == 'SpiderFang':
            return self.threadFang.is_alive()
        if spider == 'SpiderGanji':
            return self.threadGanji.is_alive()

    def runSpider(self, spider):
        self.status.put({spider: True})
        if spider == 'Spider58':
            self.thread58.start()
        if spider == 'SpiderAnjuke':
            self.threadAnjuke.start()
        if spider == 'SpiderFang':
            self.threadFang.start()
        if spider == 'SpiderGanji':
            self.threadGanji.start()

    def keepalive(self):
        while True:
            print("Sending keepalive message")
            self.hello()
            time.sleep(30)


if __name__ == '__main__':
    urlsSpider = UrlsSpider()
    threading.Thread(target=urlsSpider.keepalive).start()

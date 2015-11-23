#!usr/bin/env python
#coding: utf-8

from scrapy import Spider
from scrapy import log
from scrapy import Request, FormRequest
from scrapy import Selector
from scrapy import signals
from scrapy.utils.request import request_fingerprint
from specialworker.items import *
import re
import codecs
# import redis

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class JudicialOpinions(Spider):
    """
    从http://www.court.gov.cn/fabu-gengduo-14.html
    上抓取开庭公告数据并写入到文件中
    """
    name = 'open_court'
    download_delay = 1
    start_urls = ['http://www.baidu.com']
    # myRedis = redis.StrictRedis(host='localhost',port=6379) #connected to redis
    model_urls = "http://www.court.gov.cn/fabu-gengduo-14.html?page=%s"
    # writeInFile = "/home/dyh/data/specialworker/openCourt/openCourt.txt"
    writeInFile = "E:/DLdata/openCourt.txt"
    # controlFile = "/home/dyh/data/specialworker/openCourt/openCourt_url.txt"
    controlFile = "E:/DLdata/openCourt_url.txt"
    # haveRequested = "/home/dyh/data/specialworker/openCourt/haveRequestedDetail.txt"
    haveRequested = "E:/DLdata/haveRequestedDetail.txt"

    def set_crawler(self,crawler):
        super(JudicialOpinions, self).set_crawler(crawler)
        self.bind_signal()


    def bind_signal(self):
        self.crawler.signals.connect(self.open_file, \
            signal=signals.spider_opened)  #爬虫开启时，打开文件
        self.crawler.signals.connect(self.close_file, \
            signal=signals.spider_closed)  #爬虫关闭时，关闭文件

    def open_file(self):
        self.file_handler = codecs.open(self.writeInFile, "a",\
        encoding='utf-8')  #写内容
        self.file_haveRequested = open(self.haveRequested, "a+")  #写入已请求成功的url
        # self.url_have_seen = "dup_open"
        # for line in self.file_haveRequested:
        #     fp = self.url_fingerprint(line)
        #     self.myRedis.sadd(self.url_have_seen,fp)

    def url_fingerprint(self, url):
        req = Request(url.strip())
        fp = request_fingerprint(req)
        return fp 

    def close_file(self):
        self.file_handler.close()

    def parse(self, response):
        pages = 32
        for i in range(1,32)[2:3]:
            yield Request(self.model_urls%str(i),
                callback=self.cases,dont_filter=True)

    def cases(self, response):
        """
        提取各个案件的url
        """
        sel = Selector(text=response.body)
        urls = sel.xpath("//div[@class='sec_list']//ul[1]\
            /li/a/@href").extract()
        title = sel.xpath("//div[@class='sec_list']//ul[1]\
            /li/a/text()").extract()
        date = sel.xpath("//div[@class='sec_list']//ul[1]\
            /li/i/text()").extract()
        title_date = map(lambda x,y: x+"\001"+y, title, date)
        url_title_date = zip(urls, title_date)
        for el in url_title_date:
            url = "http://www.court.gov.cn" + el[0]
            yield Request(url, callback=self.detail, \
                dont_filter=True, meta={"t_d":el[1]})

    def detail(self, response):
        """
        """
        sel = Selector(text=response.body)
        self.file_haveRequested.write(response.url+"\n")
        item =  SpecialworkerItem()
        con = sel.xpath("string(//div[@class='txt_txt'])").extract()
        con_s = "".join([i.strip() for i in con[0].split("\n")])
        con_a = response.meta["t_d"] +"\001" + response.url+"\001" + con_s +"\n"
        item["content"] = con_a
        yield item          
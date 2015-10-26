#!usr/bin/env python
#coding: utf-8

from scrapy import Spider
from scrapy import log
from scrapy import Request, FormRequest
from scrapy import Selector
from scrapy import signals
from scrapy.dupefilter import RFPDupeFilter
from specialworker.items import *
import re

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class JudicialOpinions(Spider):
    """
    从http://www.court.gov.cn/zgcpwsw/sc/scsdzszjrmfy/zx/
    上抓取判决书数据并写入到文件中
    """
    name = 'j_url'
    download_delay = 1
    start_urls = ['http://www.iplaypython.com']
    model_urls = "http://www.court.gov.cn/zgcpwsw/zj/"
    writeInFile = "/home/dyh/data/specialworker/judicial/url_j.txt"
    #writeInFile = "E:/DLdata/judicial.txt"
    haveRequested = "/home/dyh/data/specialworker/judicial/haveRequestedUrl.txt"
    #haveRequested = "E:/DLdata/haveRequestedUrl.txt"

    def set_crawler(self,crawler):
        super(JudicialOpinions, self).set_crawler(crawler)
        self.bind_signal()


    def bind_signal(self):
        self.crawler.signals.connect(self.open_file, \
            signal=signals.spider_opened)  #爬虫开启时，打开文件
        self.crawler.signals.connect(self.close_file, \
            signal=signals.spider_closed)  #爬虫关闭时，关闭文件

    def open_file(self):
        self.file_handler = open(self.writeInFile, "a")  #写内容
        self.file_haveRequested = open(self.haveRequested, "a+")  #写入已请求成功的url

    def close_file(self):
        self.file_handler.close()

    def parse(self, response):
        return Request(self.model_urls,
            callback=self.province,dont_filter=True)

    def province(self, response):
        """
        提取省法院的url，并发起请求
        """
        sel = Selector(text = response.body)
        baseurl = "http://www.court.gov.cn/zgcpwsw/"
        urls = sel.xpath(u"//table[@class='tbfy']/tr/td/a/@href").extract()
        urls = [baseurl + i.split("/")[1]+"/" for i in urls]
        classi = ['ms','xs','xz','zscp','pc','zx']
        for url in urls[0:1]:
            for i in classi[0:1]:   #for test
                # self.file_haveRequested.write(url+i+"/"+"\n")
                yield Request(url+i+"/", callback=self.pages, 
                    dont_filter=True)

    def pages(self, response):
        """
        提取各种案件的页数，并发起请求
        """
        sel = Selector(text=response.body)
        self.file_haveRequested.write(response.url+"\n")
        self.cases(response)   #提取首页的内容
        iscontinue = len(sel.xpath("//div[@id='bottom_right_con_five_xsaj']//ul"))
        if iscontinue:  #如果当前页不为空
            try:
                pages = sel.xpath("//div[@id='bottom_right_con_five_xsaj']//script").re("createPageHTML\(([\d]*?),")[0]
                baseurl = response.url
                for i in range(1, int(pages)+1)[0:1]: #fort test
                    # self.file_haveRequested.write(baseurl+"index_"+str(i)+".htm"+"\n")
                    yield Request(baseurl+"index_"+str(i)+".htm", 
                        callback = self.cases, dont_filter=False)
            except Exception, e:
                log.msg("only_one url==%s== error=%s" %(response.url,\
                    e), level=log.ERROR)
    
    def cases(self, response):
        """
        提取各个案件的url
        """
        item = SpecialworkerItem()
        sel = Selector(text=response.body)
        self.file_haveRequested.write(response.url+"\n")
        urls = sel.xpath("//div[@id='bottom_right_con_five_xsaj']//ul\
                    /li/div/div[2]/a/@href").extract()
        r_url = response.url
        baseurl = "/".join(r_url.split("/")[:6])
        urls = [baseurl+i[1:] for i in urls]
        con_url = ""
        for url in urls[0:1]:     #for test
            con_url += (url+"\n")
        item["content"] = con_url
        yield item
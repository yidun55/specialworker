#!usr/bin/env python
#coding: utf-8

from scrapy import Spider
from scrapy import log
from scrapy import Request, FormRequest
from scrapy import Selector
from scrapy import signals
from specialworker.items import *
import re

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class Pharmacist(Spider):
    """
    从http://fw.zjfda.gov.cn/sp/personnel!new_app_zyysList.do
    上抓取执业药师信息数据并写入到文件中
    """
    name = 'pharmacist'
    download_delay = 1
    start_urls = ['http://www.iplaypython.com']
    model_urls = "http://fw.zjfda.gov.cn/sp/personnel!new_app_zyysList.do"
    writeInFile = "/home/dyh/data/specialworker/pharmacist.txt"

    def set_crawler(self,crawler):
        super(Pharmacist, self).set_crawler(crawler)
        self.bind_signal()


    def bind_signal(self):
        self.crawler.signals.connect(self.open_file, \
            signal=signals.spider_opened)  #爬虫开启时，打开文件
        self.crawler.signals.connect(self.close_file, \
            signal=signals.spider_closed)  #爬虫关闭时，关闭文件

    def open_file(self):
        self.file_handler = open(self.writeInFile, "a")

    def close_file(self):
        self.file_handler.close()

    def parse(self, response):
        return FormRequest(self.model_urls,
            formdata={"onkeydown":"1"},
            callback=self.total,dont_filter=True)

    def total(self, response):
        """
        extract total pages and post request
        """
        sel = Selector(text=response.body)
        try:
            pages = sel.xpath(u"//td[contains(text(),'每页')]\
                /text()").re(u"第1/([\d]*)")[0]
        except:
            pages = 1086
            log.msg("unget total pages######################################", level=log.ERROR)

        for i in xrange(1, int(pages)+1):
            yield FormRequest(self.model_urls,
                formdata={"pAttr.pageCur":str(i)},
                callback=self.detail, dont_filter=True)

    def detail(self, response):
        """
        extract detail info
        """
        sel = Selector(text=response.body)
        blocks = sel.xpath(u"//td[@width='12%']/..")
        writeIn = ""
        for i in blocks:
            container = i.xpath("./td/text()").extract()
            writeIn += "\001".join(container) + "\n"

        item = SpecialworkerItem()
        item["content"] = writeIn
        yield item

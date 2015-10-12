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

class FoodBeverage(Spider):
    """
    从http://fw.zjfda.gov.cn/sp/cyfw!new_app_cyfwList.do
    上抓取餐饮服务许可证信息数据并写入到文件中
    """
    name = 'food'
    start_urls = ['http://www.iplaypython.com']
    model_urls = "http://fw.zjfda.gov.cn/sp/cyfw!new_app_cyfwList.do"
    writeInFile = "E:/DLdata/foodBeverage.txt"

    def set_crawler(self,crawler):
        super(FoodBeverage, self).set_crawler(crawler)
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
            pages = 9348
            log.msg("unget total pages######################################", level=log.ERROR)

        for i in range(1, int(pages)+1)[1:8]:
            yield FormRequest(self.model_urls,
                formdata={"onkeydown":str(i)},
                callback=self.detail, dont_filter=True)

    def detail(self, response):
        """
        extract detail info's url
        """
        sel = Selector(text=response.body)
        urls = sel.xpath(u"//td[@width='10%' and not(text()='详细')]/a/@href").extract()
        base_url = "http://fw.zjfda.gov.cn"
        for url in urls:
            yield Request(base_url+url, callback=self.detail_info,
                dont_filter=True)

    def detail_info(self, response):
        """
        extract detail info from table
        """
        sel = Selector(text=response.body)
        blocks = sel.xpath(u"//table[@bgcolor='#e2e2e2']/tr")
        container = []
        for i in blocks:
            tmp = i.xpath("./td[2]/text()").extract()
            if len(tmp) == 0:   #没有信息的以""填补
                container.append("")
            else:
                container.append(tmp[0])
        writeIn = "\001".join([ele.strip() for ele in container]) + "\n"

        item = SpecialworkerItem()
        item["content"] = writeIn
        yield item

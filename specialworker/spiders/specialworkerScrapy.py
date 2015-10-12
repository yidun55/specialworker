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

class SpecialWorker(Spider):
    """
    从http://manager.zjsafety.gov.cn/search.do?page=100&method=getSpecialworkerPage&&flag=z&&temp=index
    上抓取特种作业人员信息数据并写入到文件中
    """
    name = 'special'
    download_delay = 1
    start_urls = ['http://manager.zjsafety.gov.cn/search.do?page=1&method=getSpecialworkerPage&&flag=z&&temp=index']
    model_urls = "http://manager.zjsafety.gov.cn/search.do?page=%s&method=getSpecialworkerPage&&flag=z&&temp=index"
    writeInFile = "/home/dyh/data/specialworker/special.txt"

    def set_crawler(self,crawler):
        super(SpecialWorker, self).set_crawler(crawler)
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
        """
        提取总页面数
        """
        sel = Selector(text=response.body)
        try:
            tail_url = sel.xpath(u"//a[text()='尾页']/@href").extract()[0]
            pat = r"page=([\d]*)"
            pages = re.findall(pat, tail_url)[0]
            pages = int(pages)
        except:
            log.msg("tial pages un-get尾页未提取到",level=log.ERROR)
            pages = 52918
        for i in xrange(1, pages+1):
            yield Request(self.model_urls %i, callback=self.detail,\
                dont_filter=True)


    def detail(self, response):
        """
        提取页面最终的数据
        """
        sel = Selector(text=response.body)
        con_body = sel.xpath("//table[@width='100%']/tr[position()>2 and position()<18]")
        try:
            for i in con_body:
                container = []
                container.append(i.xpath("./td[1]/text()").extract()[0].strip())
                container.append(i.xpath("./td[3]/text()").extract()[0].strip())
                container.append(i.xpath("./td[4]/text()").extract()[0].strip())
                container.append(i.xpath("./td[6]/text()").extract()[0].strip())
                container.append(i.xpath("./td[7]/text()").extract()[0].strip())
                #==============================================================
                #提取第二元素
                raw_con2 = i.xpath("./td[2]/script/text()").extract()[0]
                pat2 = r"sex='([\d])"
                sexy = re.findall(pat2, raw_con2)
                container.append(sexy[0])
                #==============================================================
                #提取第五个元素
                raw_con5 = i.xpath("./td[5]/script/text()").extract()[0]
                pat5 = r"card='([\d]*)"
                id_card = re.findall(pat5, raw_con5)
                container.append(id_card[0])
                item = SpecialworkerItem()
                item["content"] = "\001".join(container) + "\n"
                yield item
        except IndexError:
            log.msg("response.url=%s and container=%s"%(response.url,"\001".join(container)),\
                level=log.ERROR)

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

class JudicialOpinions(Spider):
    """
    从http://www.court.gov.cn/zgcpwsw/sc/scsdzszjrmfy/zx/
    上抓取判决书数据并写入到文件中
    """
    name = 'judicial'
    download_delay = 1
    start_urls = ['http://www.iplaypython.com']
    model_urls = "http://www.court.gov.cn/zgcpwsw/zj/"
    writeInFile = "/home/dyh/data/specialworker/judicial/judicial.txt"
    #writeInFile = "E:/DLdata/judicial.txt"

    def set_crawler(self,crawler):
        super(JudicialOpinions, self).set_crawler(crawler)
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
        for url in urls:
            for i in classi:
                yield Request(url+i+"/", callback=self.pages, 
                    dont_filter=True,meta = {
                  'dont_redirect': True,
                  'handle_httpstatus_list': [302]})

    def pages(self, response):
        """
        提取各种案件的页数，并发起请求
        """
        sel = Selector(text=response.body)
        self.cases(response)   #提取首页的内容
        iscontinue = len(sel.xpath("//div[@id='bottom_right_con_five_xsaj']//ul"))
        if iscontinue:  #如果当前页不为空
            try:
                pages = sel.xpath("//div[@id='bottom_right_con_five_xsaj']//script").re("createPageHTML\(([\d]*?),")[0]
                baseurl = response.url
                for i in range(1, int(pages)):
                    yield Request(baseurl+"index_"+str(i)+".htm", 
                        callback = self.cases, dont_filter=True)
            except Exception, e:
                log.msg("only_one url=%s error=%s" %(response.url,\
                    e), level=log.ERROR)
    
    def cases(self, response):
        """
        提取各个案件的url
        """
        sel = Selector(text=response.body)
        urls = sel.xpath("//div[@id='bottom_right_con_five_xsaj']//ul\
                    /li/div/div[2]/a/@href").extract()
        r_url = response.url
        baseurl = "/".join(r_url.split("/")[:6])
        urls = [baseurl+i[1:] for i in urls]
        for url in urls:
            yield Request(url, callback=self.detail, 
                dont_filter=True)

    def detail(self, response):
        """
        提取判决书的详细信息
        """
        item = SpecialworkerItem()
        sel = Selector(text=response.body)
        court = sel.xpath("//div[@id='nav']/a[2]/text()").extract()
        classi = sel.xpath("//div[@id='nav']/a[3]/text()").extract()
        title = sel.xpath("//div[@id='ws']//tr[1]/td/div/text()").extract()
        up_time = sel.xpath("//div[@id='wsTime']/span/text()").re(u"提交时间：(.*)")
        id_case = sel.xpath("//div[@id='DocArea']/div[contains(@style, 'TEXT-ALIGN: right')][1]/text()").extract()
        i_url = response.url
        if len(id_case) != 0:
            doc = sel.xpath("//div[@id='DocArea']/*[count(*)=0]/text()").extract()
        else:
            tmp = sel.xpath("//div[@id='DocArea']")
            container = tmp.xpath("string(.)").extract()
            tmp1 = container[0].strip().split()
            if len(tmp1) >=3:
                id_case = [tmp1[2]]
            else:
                id_case = [""]
            doc = [i.strip() for i in tmp1]
        try:
            con = [court[0], classi[0], title[0],up_time[0],
            id_case[0], i_url]
            con = [i.strip() for i in con]
            con.append("\002".join(doc))
            item['content'] = "\001".join(con)+"\n"
            yield item
        except Exception,e:
            log.msg("undown url=%s info=%s"%(response.request.url,\
                e), level=log.ERROR)







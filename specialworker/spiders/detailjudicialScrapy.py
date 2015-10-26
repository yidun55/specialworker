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

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class JudicialOpinions(Spider):
    """
    从http://www.court.gov.cn/zgcpwsw/sc/scsdzszjrmfy/zx/
    上抓取判决书数据并写入到文件中
    """
    name = 'j_detail'
    download_delay = 1
    start_urls = ['http://www.baidu.com']
    model_urls = "http://www.court.gov.cn/zgcpwsw/zj/"
    # writeInFile = "/home/dyh/data/specialworker/judicial/url_j.txt"
    writeInFile = "E:/DLdata/judicial.txt"
    #controlFile = "/home/dyh/data/specialworker/judicial/judicial_url.txt"
    controlFile = "E:/DLdata/judicial_url.txt"
    # haveRequested = "/home/dyh/data/specialworker/judicial/haveRequestedUrl.txt"
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
        self.file_handler = open(self.writeInFile, "a")  #写内容
        self.file_haveRequested = open(self.haveRequested, "a+")  #写入已请求成功的url
        self.url_have_seen = set()
        for line in self.file_haveRequested:
            fp = self.url_fingerprint(line)
            self.url_have_seen.add(fp)

    def url_fingerprint(self, url):
        req = Request(url.strip())
        fp = request_fingerprint(req)
        return fp 

    def close_file(self):
        self.file_handler.close()

    def parse(self, response):
        return Request(self.model_urls,
            callback=self.cases,dont_filter=True)

    
    def cases(self, response):
        """
        提取各个案件的url
        """
        f = open(self.controlFile, "r")
        for url in f:     #for test
            fp = self.url_fingerprint(url)
            if fp not in self.url_have_seen:
                self.url_have_seen.add(fp)
                yield Request(url.strip(), callback = self.detail, \
                    dont_filter=False)
            else:
                pass 


    def detail(self, response):
        """
        提取判决书的详细信息
        """
        item = SpecialworkerItem()
        sel = Selector(text=response.body)
        self.file_haveRequested.write(response.url+"\n")
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
            tmp1 = container[0].strip().split("\n")
            tmp1_1 = [i.strip() for i in tmp1]
            tmp2 = [i for i in tmp1_1 if (len(i)!=0 and len(filter(str.isalpha, i.encode('utf-8')))/float(len(i))<0.35)]
            if len(tmp2) >=3:
                id_case = [tmp2[2]]
            else:
                id_case = [""]
            doc = tmp2
        try:
            #================================================
            """
            判别id_case是否是id号
            """
            pat = ur"第[\d]"
            isid = len(re.findall(pat, id_case[0]))
            if isid == 0:
                id_case = [""]
            #================================================
            con = [court[0], classi[0], title[0],up_time[0],
            id_case[0], i_url]
            con = [i.strip() for i in con]
            doc = "".join([i.strip() for i in "\002".join(doc).split("\n")])  #去除"\n"
            con.append(doc)
            item['content'] = "\001".join(con)+"\n"
            yield item
        except Exception,e:
            log.msg("undown url=%s info=%s"%(response.request.url,\
                e), level=log.ERROR)
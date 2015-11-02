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
import redis

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class JudicialOpinions(Spider):
    """
    从http://www.court.gov.cn/zgcpwsw/sc/scsdzszjrmfy/zx/
    上抓取判决书数据并写入到文件中
    """
    name = 'all_url_j'
    #download_delay = 1
    start_urls = ['http://www.baidu.com']
    myRedis = redis.StrictRedis(host='localhost',port=6379) #connected to redis
    model_urls = "http://www.court.gov.cn/extension/search.htm"
    writeInFile = "/home/dyh/data/specialworker/judicial/all_url_j.txt"
    # writeInFile = "E:/DLdata/judicial_url.txt"
    haveRequested = "/home/dyh/data/specialworker/judicial/haveRequestedUrl.txt"
    # haveRequested = "E:/DLdata/haveRequestedUrl.txt"
    data = {
        "keyword":"法院",
        "caseCode":"",
        "wenshuanyou":"",
        "anjianleixing":"民事案件",
        "docsourcename":"",
        "court":"",
        "beginDate":"2014-01-01",
        "endDate":"2015-10-30",
        "adv":"1",
        "orderby":"",
        "order":"",
        "page":"1"
    }

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
        self.url_have_seen = "dup_j"
        for line in self.file_haveRequested:
            fp = self.url_fingerprint(line)
            self.myRedis.sadd(self.url_have_seen,fp)

    def url_fingerprint(self, url):
        req = Request(url.strip())
        fp = request_fingerprint(req)
        return fp 

    def close_file(self):
        self.file_handler.close()

    def parse(self, response):
        case_type = ["民事案件", "刑事案件", "行政案件",\
           "知识产权","赔偿案件", "执行案件"]
        for i in case_type:
            self.data["anjianleixing"] = i
            con = ["=".join(item) for item in self.data.items()]
            tail = "&".join(con)
            url = self.model_urls + "?" + tail
            yield Request(url,
                callback=self.pages,dont_filter=True)


    def pages(self, response):
        """
        提取各种案件的页数，并发起请求
        """
        sel = Selector(text=response.body)
        self.cases(response)   #提取首页的内容
        total = sel.xpath("//table/tbody//script/text()").re(u"共[\D]*?([\d]*?)[\D]*?页")
        try:
            total = int(total[0]) + 1
            for i in xrange(2, total):
                self.data['page'] = str(i)
                con = ["=".join(item) for item in self.data.items()]
                tail = "&".join(con)
                url = self.model_urls + "?" + tail
                fp = self.url_fingerprint(url)
                isexist = self.myRedis.sadd(self.url_have_seen,fp)
                if isexist:
                    #如果redis set ppai_dup_redis没有则插入并返回1，否则
                    #返回0
                    yield Request(url, callback=self.cases,\
                        dont_filter=False)
                else:
                    pass
        except Exception, e:
            log.msg("only_one url==%s== error=%s" %(response.url,\
                e), level=log.ERROR)
    
    def cases(self, response):
        """
        提取各个案件的url
        """
        item = SpecialworkerItem()
        sel = Selector(text=response.body)
        self.file_haveRequested.write(response.url+"\n") #记录已请求的页面url
        blocks = sel.xpath("//table[@class='tablestyle']/\
            tbody/tr[position()>1]")
        xp = "string(./td[%s])"
        xp_u = "./td[3]/a/@href"
        con = []
        for b in blocks:
            tmp = [b.xpath(xp%str(i)).extract() for i in range(2, 6)]
            tmp.append(b.xpath(xp_u).extract())
            con.append(tmp)
        content = ""
        for ele in con:
            try:
                content += "\001".join(["" if len(i)==0 else str(i[0]).strip() \
                    for i in ele]) + "\n"
            except Exception,e:
                log.msg("error==%s, cases"%e, level=log.ERROR)
    
        item["content"] = content
        yield item

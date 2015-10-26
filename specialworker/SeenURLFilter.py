#!usr/bin/env python
#coding: utf-8


from scrapy.dupefilter import RFPDupeFilter
from scrapy.dupefilter import BaseDupeFilter
from scrapy import Request, FormRequest
from scrapy.utils.request import request_fingerprint

class SeenURLFilter(RFPDupeFilter):
    """A dupe filter that considers the URL"""

    def __init__(self):
        path1 = "E:/DLdata/haveRequestedUrl.txt"
        f = open(path1, "r")
        for line in f:
            req = Request(line.strip())
            self.request_seen(req)


    def request_seen(self, request):
        #来自scrapy.utils.request的request_fingerprint函数接受request参数并返回fingerprint
        fp = request_fingerprint(request)
        added = self.fingerprints.add(fp)
        if fp in self.fingerprints:
            return True


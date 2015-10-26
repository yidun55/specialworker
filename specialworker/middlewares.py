# -*- coding: utf-8 -*-

from scrapy import log
from scrapy.exceptions import CloseSpider, IgnoreRequest


class IgnoreHttpError(IgnoreRequest):
    """A non-200 response was filtered
    """
    def __init__(self, response, *args, **kwargs):
        self.response = response
        super(IgnoreHttpError, self).__init__(*args, **kwargs)

class Redirect302Middleware(object):
    """处理302帖子被删除的情况
    """
    def __init__(self):
        pass

    def process_spider_input(self, response, spider):
        if response.status == 302:
            raise IgnoreHttpError(response, '302 post deleted, Ignoring 302 response')

    def process_spider_exception(self, response, exception, spider):
        if isinstance(exception, IgnoreHttpError):
            log.msg(
                    format="Ignoring response %(response)r: 302 deleted",
                    level=log.WARNING,
                    spider=spider,
                    response=response
            )
            request = response.request.copy()
            retries = request.meta.get('retry_times', 0)
            if retries <=3:
                retries += 1
                request.meta['retry_times'] = retries
                request.dont_filter = True
                return [request]
            else:
                log.msg("give_up_ul==%s=="%request.url, level=log.ERROR)
                return []




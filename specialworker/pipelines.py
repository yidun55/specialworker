# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import log
from os.path import getsize

class SpecialworkerPipeline(object):
    """
    文件如果大于一百M就重新打开一个文件 
    """
    file_counter = 0 
    def process_item(self, item, spider):
        try:
            file_size = getsize(spider.file_handler.name)/float(1000000)
            if file_size > 100:
                new_name = spider.writeInFile + "_"+ str(file_counter) 
                spider.file_handler = open(new_name, "a")
                self.file_counter += 1
        except Exception,e:
            log.msg("error_info=%"%e, level=log.ERROR)
        spider.file_handler.write(item['content'])

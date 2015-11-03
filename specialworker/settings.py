# -*- coding: utf-8 -*-

# Scrapy settings for specialworker project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#
# import sys
# import os
# from os.path import dirname
# path = dirname(dirname(os.path.abspath(os.path.dirname(__file__))))
# sys.path.append(path)

BOT_NAME = 'specialworker'

SPIDER_MODULES = ['specialworker.spiders']
NEWSPIDER_MODULE = 'specialworker.spiders'

DEFAULT_ITEM_CLASS = 'specialworker.items.SpecialworkerItem'
ITEM_PIPELINES={'specialworker.pipelines.SpecialworkerPipeline':0}

LOG_FILE = "/home/dyh/data/specialworker/judicial/log"
# DUPEFILTER_CLASS = 'specialworker.SeenURLFilter.SeenURLFilter'

SPIDER_MIDDLEWARES = {
    # handle 302 deleted error
    'specialworker.middlewares.Redirect302Middleware': 49
}

DOWNLOADER_MIDDLEWARES = {
    # this middleware handles redirection of requests based on response status.
    'scrapy.contrib.downloadermiddleware.redirect.RedirectMiddleware': None,

}

# DUPEFILTER_CLASS = "specialworker.MyBloomFilter.BLOOMDupeFilter"
LOG_LEVEL = 'INFO'
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'specialworker (+http://www.yourdomain.com)'

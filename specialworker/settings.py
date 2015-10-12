# -*- coding: utf-8 -*-

# Scrapy settings for specialworker project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'specialworker'

SPIDER_MODULES = ['specialworker.spiders']
NEWSPIDER_MODULE = 'specialworker.spiders'

DEFAULT_ITEM_CLASS = 'specialworker.items.SpecialworkerItem'
ITEM_PIPELINES={'specialworker.pipelines.SpecialworkerPipeline':0}

#LOG_FILE = "/home/dyh/data/specialworker/log"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'specialworker (+http://www.yourdomain.com)'

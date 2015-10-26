from scrapy.dupefilter import RFPDupeFilter

class SeenURLFilter(RFPDupeFilter):
    """A dupe filter that considers the URL"""

    def __init__(self, path=None):
        path1 = "E:/DLdata/haveRequestedUrl.txt"
        f = open(path1, "r")
        for line in f:
            super(SeenURLFilter, self).request_seen(line.strip())


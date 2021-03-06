import scrapy
import argh
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]

class BHarianListingSpider(scrapy.Spider):


    allowed_domains = ['bharian.com.my']


    def parse(self, response):
        for newslead in response.css('.view-section-listing > .view-content > .row'):
            title = newslead.css('h2 > a::text').extract_first() or ''
            url = newslead.css('h2 > a::attr(href)').extract_first() or ''
            summary = newslead.css('p.lead::text').extract_first() or ''
            postdate = newslead.css('small::text').extract_first() or ''
            yield {'title': title.strip(), 
                    'summary': summary.strip(), 
                    'postdate': postdate.strip(),
                    'type': self._type, 
                    'url': response.urljoin(url)}

        nextpage = response.css('.pager .pager-next a::attr(href)').extract_first()
        if nextpage:
            yield scrapy.Request(response.urljoin(nextpage), self.parse)

class CrimeNewsSpider(BHarianListingSpider):
    name = 'BHarian Crime News Scraper'

    _type = 'crime'

    start_urls = [
        'http://www.bharian.com.my/jenayah'
    ]

class BusinessNewsSpider(BHarianListingSpider):
    name = 'BHarian Business News Scraper'

    _type = 'business'

    start_urls = [
        'http://www.bharian.com.my/bisnes'
    ]

class PoliticsNewsSpider(BHarianListingSpider):
    name = 'BHarian Political News Scraper'

    _type = 'politics'

    start_urls = [
        'http://www.bharian.com.my/politik'
    ]


class Runner(object):

    def __init__(self, output, spider):
        self.output = output
        self.spider = spider

    def run(self):
        process = CrawlerProcess({
            'FEED_URI': self.output,
            'FEED_FORMAT': 'jsonlines',
            'USER_AGENTS': USER_AGENTS,
            'DOWNLOAD_DELAY': 3,
            'AUTOTHROTTLE_ENABLED': True,
            'AUTOTHROTTLE_START_DELAY': 3,
            'AUTOTHROTTLE_MAX_DELAY': 60
        })

        process.crawl(self.spider)
        process.start()


@argh.arg('output', help='Output file')
def crime(output):
    runner = Runner(output, CrimeNewsSpider)
    runner.run()

@argh.arg('output', help='Output file')
def business(output):
    runner = Runner(output, BusinessNewsSpider)
    runner.run()


@argh.arg('output', help='Output file')
def politics(output):
    runner = Runner(output, PoliticsNewsSpider)
    runner.run()

parser = argh.ArghParser()
parser.add_commands([crime,  business, politics])

def main():
    parser.dispatch()

if __name__ == '__main__':
    main()


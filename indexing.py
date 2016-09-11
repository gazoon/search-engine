import re
from collections import defaultdict
from urllib.request import urlopen

from bs4 import BeautifulSoup


class Crawler(object):
    def __init__(self, domain):
        self.domain = domain
        self.indexed_urls = set()
        self.bad_urls = set()
        self.index = defaultdict(lambda: defaultdict(list))

    def add_to_index(self, url, soup):
        for x in soup(['script', 'style', '[document]', 'title', 'head']):
            x.extract()
        text = soup.text.lower()
        words = re.findall(r'[\w-]+', text)
        for pos, word in enumerate(words):
            self.index[word][url].append(pos)
        self.indexed_urls.add(url)

    def get_urls(self, soup):
        urls = set()
        for link in soup.find_all('a'):
            url = link.get('href')
            if url is None:
                continue
            if self.domain not in url:
                continue
            url = url.split('?')[0]
            url = url.split('#')[0]
            if url not in self.indexed_urls and url not in self.bad_urls:
                urls.add(url)
        return urls

    def get_index(self):
        return dict(self.index)

    def crawl(self, start_url):
        urls = set()
        urls.add(start_url)
        while urls:
            url = urls.pop()
            print(url)
            try:
                with urlopen(url) as f:
                    page = f.read()
                soup = BeautifulSoup(page, 'html.parser')
            except:
                self.bad_urls.add(url)
                continue

            self.add_to_index(url, soup)
            urls.update(self.get_urls(soup))

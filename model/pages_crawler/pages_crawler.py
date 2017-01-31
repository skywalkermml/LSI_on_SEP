'''
Download all pages from SEP's index page
'''

import sys
from argparse import ArgumentParser
from HTMLParser import HTMLParser
import urlparse

import gevent
from gevent.monkey import patch_all; patch_all()
import random
import requests


class SEPEntry(object):

	SEP_URL_PREFIX = 'https://plato.stanford.edu/'

	def __init__(self, title, url):
		self.title = title
		self.url = url
		self.contents = None

	def request_content(self):
		resp = requests.get(urlparse.urljoin(SEPEntry.SEP_URL_PREFIX, self.url))
		assert resp.status_code == 200
		self.content = resp.text
		print '{} success'.format(self.title)

class IndexParser(HTMLParser):
	def __init__(self, entry_links):
		HTMLParser.__init__(self)
		assert isinstance(entry_links, list)
		self.entry_links = entry_links
		self.adding_entry = False
		self.current_title = None
		self.current_url = None

	def handle_starttag(self, tag, attrs):
		if tag == 'a' and not self.adding_entry:
			for attr in attrs:
				if len(attr) == 2 and attr[0] == 'href' and attr[1].startswith('entries/'):
					self.current_url = attr[1]
					self.adding_entry = True

	def handle_data(self, data):
		if self.adding_entry:
			self.current_title = data

	def handle_endtag(self, tag):
		if self.adding_entry:
			self.entry_links.append(SEPEntry(self.current_title, self.current_url))
			self.adding_entry = False
			self.current_title = None
			self.current_url = None

def command_line_args():
    parser = ArgumentParser('Pages Crawler')
    parser.add_argument('--index-page-url',
                        help='Index page url', default='https://plato.stanford.edu/contents.html')
    return parser.parse_args()

def index_page_content(index_page):
	resp = requests.get(index_page)
	assert resp.status_code == 200
	return resp.text

def get_content(sep_entry):
	gevent.sleep(random.random() * 60)
	sep_entry.request_content()

def main():
    options = command_line_args()
    index_content = index_page_content(options.index_page_url)
    #sep_entries = [SEPEntry('abducion', 'entries/abduction/'), SEPEntry('abilities', 'entries/abilities/')]
    sep_entries = []
    parser = IndexParser(sep_entries)
    parser.feed(index_content)
    threads = [gevent.spawn(get_content, sep_entry) for sep_entry in sep_entries]
    gevent.joinall(threads)


if __name__ == '__main__':
    sys.exit(main())


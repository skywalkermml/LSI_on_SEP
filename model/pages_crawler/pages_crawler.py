'''
Download all pages from SEP's index page
'''

import sys
from argparse import ArgumentParser
from collections import namedtuple
from HTMLParser import HTMLParser

import requests


EntryLink = namedtuple('EntryLink', ['entry', 'link'])


class IndexParser(HTMLParser):
	def __init__(self, entry_links):
		HTMLParser.__init__(self)
		assert isinstance(entry_links, list)
		self.entry_links = entry_links
		self.adding_entry = False
		self.current_entry = None
		self.current_link = None

	def handle_starttag(self, tag, attrs):
		if tag == 'a' and not self.adding_entry:
			for attr in attrs:
				if len(attr) == 2 and attr[0] == 'href' and attr[1].startswith('entries/'):
					self.current_link = attr[1]
					self.adding_entry = True

	def handle_data(self, data):
		if self.adding_entry:
			self.current_entry = data

	def handle_endtag(self, tag):
		if self.adding_entry:
			self.entry_links.append(EntryLink(self.current_entry, self.current_link))
			self.adding_entry = False
			self.current_entry = None
			self.current_link = None

def command_line_args():
    parser = ArgumentParser('Pages Crawler')
    parser.add_argument('--index-page-url',
                        help='Index page url', default='https://plato.stanford.edu/contents.html')
    return parser.parse_args()

def index_page_content(index_page):
	resp = requests.get(index_page)
	assert resp.status_code == 200
	return resp.text


def main():
	options = command_line_args()
	index_content = index_page_content(options.index_page_url)
	#index_content = '<a href="https://www.cwi.nl/">test</a>'
	entry_links = []
	parser = IndexParser(entry_links)
	parser.feed(index_content)
	print entry_links

if __name__ == '__main__':
    sys.exit(main())


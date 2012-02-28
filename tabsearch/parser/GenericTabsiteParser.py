# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# The Rhythmbox authors hereby grant permission for non-GPL compatible
# GStreamer plugins to be used and distributed together with GStreamer
# and Rhythmbox. This permission is above and beyond the permissions granted
# by the GPL license by which Rhythmbox is covered. If you modify this code
# you may extend this exception to your version of the code, but you are not
# obligated to do so. If you do not wish to do so, delete this exception
# statement from your version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301  USA.

from lxml.html import fromstring
from Tab import Tab
import re
from lxml import etree
from gi.repository import Gio
from gi._glib import GError

class GenericTabsiteParser(object):
	website_title = ''
	website_short = ''
	artist = ''
	title = ''
	tab_list = []
	callback_content = None
	callback_info = None
	
	def __init__(self, website_title, website_short, callback_content, callback_info):
		self.website_title = website_title
		self.website_short = website_short
		self.callback_content = callback_content
		self.callback_info = callback_info

	def tabs_finder(self, artist, title):
		""" initiates web lookup for given artist and title """
		self.artist = artist
		self.title = title
		
		print 'Checking ' + self.website_title + '...'
		
		url = self.generate_url_to_overview()
		# continue with processing of the url in other function,
		# so this classes subclass (concrete: AZChordsParser) can jump 
		# between this and the other function
		self.process_url_to_overview_page(url)
		
	def process_url_to_overview_page(self, url):
		""" does a lookup to overview page and calls the function to
			process it asynchronously """
		if url is None:
			print "-> No tabs found for '" + self.artist + "' on " + self.website_title + ' (' + self.website_short + ')'
			return
		
		print "-> overview: " + url
		
		# fetch overview page with artist's titles
		self.file_res = Gio.File.new_for_uri(url)
		self.file_res.load_contents_async(None, self.process_overview_page, url)
		print 'waiting for results ...'

	def preprocess_overview_page(self, html):
		return unicode(html, encoding='iso_8859_1')

	def preprocess_single_page(self, html):
		return unicode(html, encoding='iso_8859_1')

	def process_overview_page(self, gdaemonfile, result, url):
		""" Processes html of artists overview page, scans it for 
			links to title pages and initiates fetching of those pages """
		
		if result is None:
			print 'Error: no overview page'
			self.callback_info(
					'\t-> No overview page found on '+self.website_title+' ('+self.website_short+')!\n'
					'\t   Maybe this is a bug in this plugin. Please have a look on the overview page\n' + 
					'\t   and report at http://code.google.com/p/tab-rhythmbox-plugin/ if the tabs\n' + 
					'\t   for this song are linked to on this page:\n\t   ' + url)
			return

		try:
			result = self.file_res.load_contents_finish(result)
		except GError:
			print "Error: can't read from url:\n\t" + url
			return
		successful = result[0]
		html = result[1]
		
		print 'Overview page found'
		html = self.preprocess_overview_page(html)
		searchTree = fromstring(html)
		
		expr = self.get_title_expr()
		print "using expression: " + expr
		
		tree = searchTree.xpath(expr)
		print "found " + str(len(tree)) + " tabs for '" + self.title + "'"
		if len(tree) == 0:
			self.callback_info(
					'\t-> Nothing found on '+self.website_title+' ('+self.website_short+')!\n'
					'\t   Not one single link for this song found on artists overview page!\n' +
					'\t   Maybe this is a bug in this plugin. Please have a look on the overview page\n' + 
					'\t   and report at http://code.google.com/p/tab-rhythmbox-plugin/ if the tabs\n' + 
					'\t   for this song are linked to on this page:\n\t   ' + url)
		else:
			self.fetch_tabs(tree)

	def fetch_tabs(self, tree):
		""" Takes links from overview page (tree) and fetches sites """
		tabs = []
		for a in tree:
			link = a.get('href')
			tab = self.fetch_single_tab(link)

	def fetch_single_tab(self, url, type, title):
		""" Fetches page from given url and fetches tabs """
		print "-> " + url
		
		tab = "nothing"
		if url != "":
			self.file_res = Gio.File.new_for_uri(url)
			self.file_res.load_contents_async(None, self.process_single_page, {'url': url, 'type': type, 'title': title})

	def process_single_page(self, gdaemonfile, result, params):
		""" Processes html of tab site, extracts relevant part
			returns it to notebook """
		try:
			result = self.file_res.load_contents_finish(result)
		except GError:
			print "Error: can't read from url:\n\t" + params['url']
			return
		successful = result[0]
		html = result[1]

		html = self.preprocess_single_page(html)
		
		if html is None:
			print 'Error: html is None'
			return
		if html == '':
			print 'Error: html is empty string'
			return
	
		text = ""	
		searchTree = fromstring(html)
		expr = self.get_tab_expr()
		preTags = searchTree.xpath(expr)
		if len(preTags) == 0:
			info =	'no pre tag found this tab site!\n\n'
			info +=	'maybe this is a bug in this plugin. please have a look on the page\n'
			info +=	'and report at http://code.google.com/p/tab-rhythmbox-plugin/ if this site\n'
			info +=	'does contain for this song:\n' + params['url']
			self.callback_info(info)
		elif len(preTags) > 0:
			pre = etree.Element('pre')
			# philipp changed the second parameter from "encoding=unicode"
			# to "utf-8" since the internal processing of tabs works exclusivly
			# with this encoding.
			# have a look at the function process_tab()
			for i in range(0, len(preTags)):
				text += etree.tostring(preTags[i], encoding='utf-8')

			text = self.process_tab(text)
			if len(preTags) > 1:
				text = "More than one <pre> found.\n\n" + text + "\n\n" + html
		# return loaded tabs to notebook:
		self.callback_content(text, {'source': 'web ('+self.website_short+')', 'type': params['type'], 'artist': self.artist, 'title': self.title, 'title_on_website': params['title']})

	def get_tab_expr(self):
		""" Return a XPath expression that matches the one element 
			within a HTML document that contains the guitar tabs """
		return ".//*/pre"

	def get_title_expr(self):
		title = self.cleanTitle()
		title = title.replace(', ', ' ')	# hail, hail from pearl jam
		title = title.replace(',', ' ')
		title = title.replace('\'', '')		# let's ride from airbourne
		title = title.replace('/', ' ')		# "1/2 Lovesong" from "Die Ärzte"
		title = title.replace('&', 'and')	# "us & them" by pink floyd
		title = title.title()
		if(title.startswith("The ")):				# 'the riddle' and 'the man who sold the world'
			title = title.replace("The ","", 1)		# -> 'riddle'       -> 'man who sold the world'
		return ".//*/a[contains(., \""+title+"\")]"

	def prepare_artist_for_url(self):
		return self.artist.decode('utf-8')
		
	def prepare_title_for_url(self):
		return self.title.decode('utf-8')

	# cleans the incoming tabs
	def process_tab(self, tab):
		tab = tab.replace('&#13;','\r')
		tab = tab.replace('&#146;', '\'')#	some kind of weird '
		tab = tab.replace('&#150;', '-')#	some kind of weird -
		tab = tab.replace('&#151;', '-')#	some kind of weird -
		tab = tab.replace('&gt;', '>')
		tab = tab.replace('<br/>','\n')
		tab = tab.replace('<br />','\n')
		tab = self.remove_html_tags(tab)
		return tab

	# will be overwritten in subclasses
	def generate_url_to_overview(self):
		return "http://www.example.com?artist=" + self.prepare_artist_for_url() + "&title" + self.prepare_title_for_url() ;

	def remove_html_tags(self, data):
		p = re.compile(r'<.*?>')
		return p.sub('', data)

	def remove_par(self, data):
		p = re.compile(r'\s\([^)]*\)')
		return re.sub(p, '', data)


	def cleanTitle(self):
		title = self.title
		
		# cut off ".mp3" or ".mP3"
		title = re.sub("\.[Mm][Pp]3$","",title)
		
		# cut off "01 -"
		title = re.sub(".*[-]","",title)
		#print "\t-> cleanTitle(): '" + self.title + "' -> '" + title + "'"
		return title

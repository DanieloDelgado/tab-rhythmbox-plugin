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

import rb
from Tab import Tab
from lxml.html import fromstring
from GenericTabsiteParser import GenericTabsiteParser
from Helper import remove_accents


class AZChordsParser (GenericTabsiteParser):
	def __init__(self, callback_content, callback_info):
		GenericTabsiteParser.__init__(self, "AZChords", 'AZ', callback_content, callback_info)

	def prepare_artist_for_url(self):
		artist = remove_accents(self.artist.lower())
		if artist.startswith("the "):
			# 'the doors' -> 'doors'
			artist = artist.replace("the ","",1)
		# special case ac/dc
		if artist.startswith("ac") and artist.endswith("dc"):
			artist = "ac/dc"
		artist = artist.replace("&", "and")		# simon & garfunkel, angels & airwaves
		artist = artist.replace("'", "")		# Gigi D'Agostino
		artist = artist.replace(',', '')		# Crosby, Stills & Nash
		return artist

	def tabs_finder(self, artist, title):
		""" initiates web lookup for given artist and title """
		self.artist = artist
		self.title = title
		
		print 'Checking ' + self.website_title + '...'
		
		artist_url = None
		
		artist = self.prepare_artist_for_url()
		first_letter = artist[0]
		
		# url for overview page that lists all artists with that first letter
		url = "http://www.azchords.com/"+first_letter+".html"

		loader = rb.Loader()
		loader.get_url(url, self.generate_url_to_overview_AZ, artist, url)

	def generate_url_to_overview_AZ(self, html, artist, url):
		if html is None:
			print 'Error: html is None'
			self.callback_info(
				'\t-> No index page found on '+self.website_title+' ('+self.website_short+')!\n'
				'\t   Maybe this is a bug in this plugin. Please have a look on the overview page\n' + 
				'\t   and report at http://code.google.com/p/tab-rhythmbox-plugin/ if the artist\n' + 
				'\t   of this song is listed on this page:\n\t   ' + url)
			return
		
		searchTree = fromstring(html)
		
		# get the url for artists overview page
		expr = ".//*/a[contains(., \""+artist.title()+"\") ]"
		print "\t-> using expression: " + expr
		tree = searchTree.xpath(expr)
		
		if len(tree) > 0:
			overview_url = "http://www.azchords.com/"+tree[0].get('href')
			self.process_url_to_overview_page(overview_url)
		else:
			print 'Error: no overview page'
			self.callback_info(
					'\t-> No overview page found on '+self.website_title+' ('+self.website_short+')!\n'
					'\t   Maybe this is a bug in this plugin. Please have a look on the index page\n' + 
					'\t   and report at http://code.google.com/p/tab-rhythmbox-plugin/ if the artist\n' + 
					'\t   of this song is linked to on this page:\n\t   ' + url)

	def fetch_tabs(self, tree):
		first_letter = self.prepare_artist_for_url()[0]
		
		tabs = []
		for a in tree:
			link = "http://www.azchords.com/"+first_letter+"/"+a.get('href')
			title = a.text_content()
			# TODO: grapping the real type
			type = ''
			self.fetch_single_tab(link, type, title)

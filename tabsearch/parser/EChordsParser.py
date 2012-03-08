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

from Tab import Tab
from lxml.html import fromstring
from GenericTabsiteParser import GenericTabsiteParser
from Helper import remove_accents
from gi._glib import GError
from gi.repository import Gio

class EChordsParser (GenericTabsiteParser):
	def __init__(self, callback_content, callback_info):
		GenericTabsiteParser.__init__(self, "EChords", 'EC', callback_content, callback_info)

	def prepare_artist_for_url(self):
		artist = remove_accents(self.artist.lower())
		if artist.startswith("the "):
			# 'the doors' -> 'doors'
			artist = artist.replace("the ","",1)
		# special case ac/dc
		if artist.startswith("ac") and artist.endswith("dc"):
			artist = "ac/dc"
		artist = artist.replace(' ', '-')
		artist = artist.replace("&", "and")		# simon & garfunkel, angels & airwaves
		artist = artist.replace("'", "")		# Gigi D'Agostino
		artist = artist.replace(',', '')		# Crosby, Stills & Nash
		return artist

	def prepare_title_for_url(self):
		title = self.remove_par(self.title)
		title = title.lower()
		title = title.replace(' ', '-')
		title = title.replace ('\'', '')
		title = title.replace ('.', '')
		title = title.replace ('?', '')
		title = title.replace (':', '')
		title = title.replace (', ', '-')
		title = title.replace (',', '-')
		title = title.replace('/', '-')		# "1/2 Lovesong" from "Die Ärzte"
		title = title.replace('&', 'and')	# "Us & Them" by Pink Floyd
		title = self.remove_par(title)
		return title

	def tabs_finder(self, artist, title):
		""" initiates web lookup for given artist and title """
		self.artist = artist
		self.title = title
		
		print 'Checking ' + self.website_title + '...'
		
		artist_url = None
		
		artist = self.prepare_artist_for_url()
		title = self.prepare_title_for_url()
		first_letter = artist[0]

		opts = ['chords','tabs','drums','bass']

		for o in opts:
			url = "http://www.e-chords.com/"+o+"/"+artist+"/"+title
			print url
			self.fetch_single_tab(url,'',title);

	# def process_single_page(self, gdaemonfile, result, params):
	# 	""" Processes html of tab site, extracts relevant part
	# 		returns it to notebook """
	# 	try:
	# 		result = self.file_res.load_contents_finish(result)
	# 	except GError:
	# 		print "Error: can't read from url:\n\t" + params['url']
	# 		return
	# 	successful = result[0]
	# 	html = result[1]

	# 	html = self.preprocess_single_page(html)
		
	# 	if html is None:
	# 		print 'Error: html is None'
	# 		return
	# 	if html == '':
	# 		print 'Error: html is empty string'
	# 		return
	
	# 	text = ""	
	# 	searchTree = fromstring(html)
	# 	expr = self.get_tab_expr()
	# 	preTags = searchTree.xpath(expr)
	# 	if len(preTags) > 0:
	# 		pre = etree.Element('pre')
	# 		# philipp changed the second parameter from "encoding=unicode"
	# 		# to "utf-8" since the internal processing of tabs works exclusivly
	# 		# with this encoding.
	# 		# have a look at the function process_tab()
	# 		for i in range(0, len(preTags)):
	# 			text += etree.tostring(preTags[i], encoding='utf-8')

	# 		text = self.process_tab(text)
	# 		if len(preTags) > 1:
	# 			text = "More than one <pre> found.\n\n" + text + "\n\n" + html
	# 	# return loaded tabs to notebook:
	# 	self.callback_content(text, {'source': 'web ('+self.website_short+')', 'type': params['type'], 'artist': self.artist, 'title': self.title, 'title_on_website': params['title']})

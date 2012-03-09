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
		artist = artist.replace('/', '')
		artist = artist.replace(' ', '%20')
		artist = artist.replace("&", "")		# simon & garfunkel, angels & airwaves
		artist = artist.replace("'", "")		# Gigi D'Agostino
		artist = artist.replace(',', '')		# Crosby, Stills & Nash
		return artist

	def prepare_title_for_url(self):
		title = self.remove_par(self.title)
		title = title.lower()
		title = title.replace(' ', '%20')
		title = title.replace ('\'', '')
		title = title.replace ('.', '')
		title = title.replace ('?', '')
		title = title.replace (':', '')
		title = title.replace (', ', '%20')
		title = title.replace('/', '')		# "1/2 Lovesong" from "Die Ärzte"
		title = title.replace('&', '')	# "Us & Them" by Pink Floyd
		title = self.remove_par(title)
		return title

	def generate_url_to_overview(self):
		artist = self.prepare_artist_for_url()
		title = self.prepare_title_for_url()
		return "http://www.e-chords.com/search-all/"+artist+"%20"+title

	def fetch_single_tab(self, url, type, title):
		""" Fetches page from given url and fetches tabs """
		print "-> " + url
		
		tab = "nothing"
		if url != "":
			url = "http://www.e-chords.com/"+url
			self.file_res = Gio.File.new_for_uri(url)
			self.file_res.load_contents_async(None, self.process_single_page, {'url': url, 'type': type, 'title': title})

	
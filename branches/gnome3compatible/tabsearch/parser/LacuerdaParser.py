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
from GenericTabsiteParser import GenericTabsiteParser
from Helper import remove_accents

class LacuerdaParser (GenericTabsiteParser):
	def __init__(self, callback_content, callback_info):
		GenericTabsiteParser.__init__(self, "Lacuerda", 'LC', callback_content, callback_info)

	def prepare_artist_for_url(self):
		artist = remove_accents(self.artist, True)
		artist = artist.lower()
		artist = artist.replace(' ', '_')
		return artist

	def prepare_title_for_url(self):
		title = remove_accents(self.title, True)
		title = title.lower()
		#title = title.encode('ASCII', 'ignore')
		title = title.replace('\'', '')		# let's ride von airbourne
		title = title.replace(' ', '_')
		return title

	def generate_url_to_overview(self):
		artist = self.prepare_artist_for_url()
		title = self.prepare_title_for_url()
		first_letter = artist[0]
		
		#http://lacuerda.net/tabs/n/nacho_vegas/al_final_te_estare_esperando
		return "http://lacuerda.net/tabs/" + first_letter + "/" + artist + "/" + title

	def get_title_expr(self):
		print 'title: ' + self.title
		title = self.cleanTitle()
		title = title.decode('utf-8')
		title = title.replace(', ', ' ')	# hail, hail from pearl jam
		title = title.replace(',', ' ')
		title = title.replace('\'', '')		# let's ride from airbourne
		#title = u'Al final te estaré esperando'
		return ".//*/tr[@onclick]/td[contains(., \""+title+"\")]"

	def fetch_tabs(self, tree):
		artist = self.prepare_artist_for_url()
		first_letter = artist[0]
		title = self.prepare_title_for_url()
		tabs = []
		for td in tree:
			js = td.getparent().get('onclick')
			tmp = js[2:3]
			print 'title: ' + title + ', tmp: ' + tmp
			if tmp == "1":
				tmp = title
			else:
				tmp = title + "-" + tmp
			tab_title = td.text_content()
			# TODO: grapping the real type
			tab_type = ''
			link = "http://lacuerda.net/tabs/" + first_letter + "/" + artist + "/" + tmp + ".shtml"
			self.fetch_single_tab(link, tab_type, tab_title) 

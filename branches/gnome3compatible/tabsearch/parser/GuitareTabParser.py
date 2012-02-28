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

class GuitareTabParser (GenericTabsiteParser):
	def __init__(self, callback_content, callback_info):
		GenericTabsiteParser.__init__(self, "Guitare Tab", 'GT', callback_content, callback_info)

	def prepare_artist_for_url(self):
		artist = self.artist.lower()
		if(artist.startswith("the ")):
			# 'the doors' -> 'doors'
			artist = artist.replace("the ","",1)
		artist = self.remove_par(artist)
		artist = artist.replace(' ', '-')
		artist = artist.replace('\'', '')
		artist = artist.replace('.', '')		# dr. feelgood -> dr feelgood
		artist = artist.replace('&', 'and')		# simon & garfunkel
		artist = artist.replace(',', '')		# crosby, stills & nash
		return artist

	def generate_url_to_overview(self):
		artist = self.prepare_artist_for_url()
		first_letter = artist[0]
		
		return "http://www.guitaretab.com/"+first_letter+"/"+artist+"/all.htm"

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
		return ".//*/a[contains(., \""+title+"\") and not(contains(., \"lyrics\"))]"

	def fetch_tabs(self, tree):
		""" Takes links from overview page (tree) and fetches sites """
		tabs = []
		for a in tree:
			if a.get('href').startswith('/'):
				link = "http://www.guitaretab.com/"+a.get('href')[1:]
			else:
				link = "http://www.guitaretab.com/"+a.get('href')
			#TODO: grabbing real type and title
			type = ''
			title = ''
			self.fetch_single_tab(link, type, title) 


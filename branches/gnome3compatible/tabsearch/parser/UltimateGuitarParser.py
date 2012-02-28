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

class UltimateGuitarParser (GenericTabsiteParser):
	def __init__(self, callback_content, callback_info):
		GenericTabsiteParser.__init__(self, "Ultimate Guitar", 'UG', callback_content, callback_info)

	def prepare_artist_for_url(self):
		artist = self.artist.lower()
		if(artist.startswith("the ")):
			# 'the doors' -> 'doors'
			artist = artist.replace("the ","",1)
		artist = artist.replace ('\'', '')
		artist = artist.replace(' ', '+')
		artist = artist.replace('&', 'and')	# crosby, stills & nash
		artist = artist.replace('.', '')	# dr. feelgood
		return artist

	def prepare_title_for_url(self):
		title = self.remove_par(self.title)
		title = title.lower()
		title = title.replace ('\'', '')
		title = title.replace ('.', '')
		title = title.replace ('?', '')
		title = title.replace (':', ' ')
		title = title.replace (', ', ' ')
		title = title.replace (',', ' ')
		title = title.replace('/', ' ')		# "1/2 Lovesong" from "Die Ärzte"
		title = title.replace(' ', '+')
		title = title.replace('&', 'and')	# "Us & Them" by Pink Floyd
		title = self.remove_par(title)
		return title

	def generate_url_to_overview(self):
		artist = self.prepare_artist_for_url()
		title = self.prepare_title_for_url()
		return "http://www.ultimate-guitar.com/search.php?view_state=advanced&band_name="+artist+"&song_name="+title+"&type[]=200&type[]=400&type[]=300&type[]=700&version_la="

	def fetch_tabs(self, tree):
		""" Takes links from overview page (tree) and fetches sites """
		tabs = []
		for a in tree:
			if a.get('href').startswith("http://"):
				link = a.get('href')
			else:
				link = "http://www.ultimate-guitar.com"+a.get('href')
			type = a.getparent().getnext().getnext().text_content()
			title = a.text_content()
			self.fetch_single_tab(link, type, title)

	def get_tab_expr(self):
		"""	returns an expression that graps a <pre>-tag whose parent 
			is NOT <div class="cn"> which is the new ugly disclamer """
		# the original one:
		#	return ".//*/pre"
		# the one philipp would like to use but doesnt work for some reason ;-)
		#	return ".//*/pre/..[not(@class='dn')]"
		
		# the one that works: 
		return ".//*/pre/parent::*[not(@class='dn')]/pre"

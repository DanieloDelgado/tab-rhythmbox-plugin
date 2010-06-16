
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

import gtk, gobject
import webkit
import re
import urllib
from lxml.html import fromstring
from lxml import etree
from Tab import Tab

class AZChordsParser (object):
	def __init__(self, artist, title, tab_list):
		self.artist = artist
		self.title = title
		self.tab_list = tab_list
		self.tabs_finder(artist, title, tab_list)
		


	def tabs_finder(self, artist, title, tab_list):

		# Recursion for case as "The Doors" -> "Doors"
		if(artist.lower().startswith("the ")):
		    the_artist = artist.lower()
		    the_artist = the_artist.replace("the ","",1)
		    self.tabs_finder(the_artist, title)	   

		first_letter = artist[0].lower() 
		url = self.get_artist_url(artist)

		title = self.remove_par(title)
		title = title.replace ('\'', '')
		title = title.replace ('?', '')
		title = title.replace (':', ' ')
		title = title.replace ('&', 'And')
		title = self.remove_par(title)
		title = title.lower().replace(' ', '+')
		
		print "Searching for \""+title+"\" from \""+url+"\"..."	
		sock = urllib.urlopen(url)
		html = sock.read()
		sock.close()	
		searchTree = fromstring(html)	
		title = title.lower().replace('+', ' ')
		title = title.title()

		expr = ".//*/a[contains(., \""+title+"\") ]"
		tree = searchTree.xpath(expr)
		if len(tree) == 0:
    			t = Tab("Not Found", "")
			tab_list.append(t)     
		else :
		    for a in tree:			
			link = "http://www.azchords.com/"+first_letter+"/"+a.get('href')
			tab = self.get_tab(link)
			tab_title = a.text_content()
			t = Tab("\""+tab_title+"\" (AZ)", tab)
			tab_list.append(t)

	def get_tab(self,link):
		if link != "":		
		    sock = urllib.urlopen(link)
		    html = sock.read()
		    sock.close()	
		    searchTree = fromstring(html)	
		    expr = ".//*/pre"
		    
		    a = searchTree.xpath(expr)
		    if len(a) == 0:
			tab = "No tag <pre> found."
		    elif len(a) == 1:
			pre = etree.Element("pre")
			tab = etree.tostring(a[0], encoding=unicode)
			tab = tab.replace('&#13;','\r')
			tab = tab.replace('<br/>', '\n')
			tab = self.remove_html_tags(tab)	
		    	#print tab
	
		return tab

	def get_artist_url(self, artist):
		
		first_letter = artist[0].lower()
		artist_name = artist.title()
		artist_name = self.remove_par(artist_name)

		url = "http://www.azchords.com/"+first_letter+".html"
					
		sock = urllib.urlopen(url)
		html = sock.read()
		sock.close()	
		searchTree = fromstring(html)	

		expr = ".//*/a[contains(., \""+artist_name+"\") ]"
		print expr
		tree = searchTree.xpath(expr)
		
		if len(tree) == 0:
		    artist_url = "http://www.google.it"
		else :					
		    artist_url = "http://www.azchords.com/"+tree[0].get('href')

		return artist_url

	def remove_html_tags(self, data):
		p = re.compile(r'<.*?>')
		return p.sub('', data)

	def remove_par(self, data):
        	p = re.compile(r'\s\([^)]*\)')
        	return re.sub(p, '', data)

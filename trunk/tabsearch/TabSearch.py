# -*- coding: iso-8859-15 -*-

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


import os
import rb, rhythmdb
import gtk, gobject
import gconf
import webkit
import re
import unicodedata
import urllib
from lxml.html import fromstring
from lxml import etree
from GuitareTabParser import GuitareTabParser
from UltimateGuitarParser import UltimateGuitarParser
from AZChordsParser import AZChordsParser
from Tab import Tab
from TabSites import tab_sites

tab_search_ui = """
<ui>
    <toolbar name="ToolBar">
        <toolitem name="TabSearch" action="ToggleTabSearch" />
    </toolbar>
</ui>
"""

class TabSearch (gobject.GObject) :

    def __init__ (self, shell, plugin, gconf_keys) :
        gobject.GObject.__init__ (self)
        self.shell = shell
        self.sp = shell.get_player ()
        self.db = shell.get_property ('db')
        self.plugin = plugin

	self.gconf = gconf.client_get_default()
	self.gconf_keys = gconf_keys
	self.sites = self.get_sites()
	self.tab_list = []

	gtk.gdk.threads_init()

        self.basepath = 'file://' + os.path.split(plugin.find_file('TabSearch.py'))[0]
        self.visible = True

        self.init_gui()
        self.connect_signals()

        self.action = ('ToggleTabSearch', gtk.STOCK_INFO, _('Toggle tab search pane'),
                None, _('Change the visibility of the tab search pane'),
                self.toggle_visibility, True)
        self.action_group = gtk.ActionGroup('TabSearchActions')
        self.action_group.add_toggle_actions([self.action])
        uim = self.shell.get_ui_manager()
        uim.insert_action_group (self.action_group, 0)
        self.ui_id = uim.add_ui_from_string(tab_search_ui)
        uim.ensure_update()

    def connect_signals(self) :
        self.player_cb_ids = ( self.sp.connect ('playing-changed', self.playing_changed_cb))

    def get_sites (self):
	try:
		sites = gconf.client_get_default().get_list(self.gconf_keys['sites'], gconf.VALUE_STRING)
		if sites is None:
			sites = []
	except gobject.GError, e:
		print e
		sites = []

	#print "tabs sites: " + str (sites)
	return (sites)


    def remove_html_tags(self, data):
        p = re.compile(r'<.*?>')
        return p.sub('', data)

    def remove_par(self, data):
        p = re.compile(r'(.*?)')
        return p.sub('', data)


    def playing_changed_cb (self, playing, user_data) :
        playing_entry = None
        if self.sp:
            playing_entry = self.sp.get_playing_entry ()
        if playing_entry is None :
            return

        playing_artist = self.db.entry_get (playing_entry, rhythmdb.PROP_ARTIST)
        playing_title = self.db.entry_get (playing_entry, rhythmdb.PROP_TITLE)

        playing_artist = self.remove_accents(playing_artist)
        playing_title = self.remove_accents(playing_title)   

        if playing_artist.upper() == "UNKNOWN":
            playing_artist = ""
        if not(playing_artist == ""):     
	    self.vbox.remove(self.notebook)
	    self.vbox.show_all()
	    self.notebook = None
	    self.notebook = gtk.Notebook()
	    self.notebook.set_scrollable(True)

            self.vbox.pack_start(self.notebook, expand = True)        
	    self.vbox.show_all()

	    self.sites = self.get_sites()
	    self.tab_list = []		
	
	    gtk.gdk.threads_enter()
	    for s in self.sites:
		site_id = s
		if s == 'gt':
			gt = GuitareTabParser(playing_artist, playing_title, self.tab_list)
		elif s == 'ug':
			ug = UltimateGuitarParser(playing_artist, playing_title, self.tab_list)
		elif s == 'az':
			az = AZChordsParser(playing_artist, playing_title, self.tab_list)

	    fail=0
            for i in self.tab_list:
		if i.label == 'Not Found':
			fail += 1		

	    if fail == len(self.tab_list):
		tabWebview = webkit.WebView()
		if len(self.tab_list) == 0:
			tabWebview.load_string ("No tab site selected!\nGo to Plugin->Tab Plugin and click on the \"Configure\" button.", 'text/plain', 'utf-8', self.basepath)
		else :
			tabWebview.load_string ("Sorry! \""+playing_title+"\" not found...", 'text/plain', 'utf-8', self.basepath)
		scroll = gtk.ScrolledWindow()
		scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		scroll.set_shadow_type(gtk.SHADOW_IN)
		scroll.add(tabWebview) 
		scroll.show()
		self.notebook.append_page(scroll, gtk.Label("Tab Not Found!"))
	    else:
	        for l in self.tab_list:
			if not(l.label == "Not Found"): 
				tabWebview = webkit.WebView()
				tabWebview.load_string (l.content, 'text/plain', 'utf-8', self.basepath)
				scroll = gtk.ScrolledWindow()
				scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
				scroll.set_shadow_type(gtk.SHADOW_IN)
				scroll.add(tabWebview) 
				scroll.show()
				self.notebook.append_page(scroll, gtk.Label(l.label))	


	    self.notebook.show()
 	    self.vbox.show_all()
  	    gtk.gdk.threads_leave()


    def deactivate (self, shell) :
        self.shell = None
        self.sp = None
        self.db = None
        self.plugin = None
        shell.remove_widget (self.vbox, rb.SHELL_UI_LOCATION_RIGHT_SIDEBAR)
        uim = shell.get_ui_manager ()
        uim.remove_ui (self.ui_id)
        uim.remove_action_group (self.action_group)

    def toggle_visibility (self, action) :
        if not self.visible :
            self.shell.add_widget (self.vbox, rb.SHELL_UI_LOCATION_RIGHT_SIDEBAR, expand=True)
            self.visible = True
        else :
            self.shell.remove_widget (self.vbox, rb.SHELL_UI_LOCATION_RIGHT_SIDEBAR)
            self.visible = False

    def remove_accents(self, str) :
	nkfd_form = unicodedata.normalize('NFKD', unicode(str))
	only_ascii = nkfd_form.encode('ASCII', 'ignore')
	return only_ascii

    def init_gui(self) :	
        self.vbox = gtk.VBox()
	self.notebook = gtk.Notebook()
	self.notebook.set_scrollable(True)
       
        self.vbox.set_size_request(650, -1)
        self.shell.add_widget (self.vbox, rb.SHELL_UI_LOCATION_RIGHT_SIDEBAR, expand=True)
	self.vbox.show_all()




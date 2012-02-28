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


import os
from gi.repository import GObject, Gtk, Gdk, Pango, Gio, Peas, PeasGtk
from gi.repository import RB
from gi.repository import WebKit
from gi._glib import GError
import re
from parser.GuitareTabParser import GuitareTabParser
from parser.UltimateGuitarParser import UltimateGuitarParser
from parser.AZChordsParser import AZChordsParser
from parser.LacuerdaParser import LacuerdaParser
from Tab import Tab
from TabSites import tab_sites
from Helper import remove_accents

tab_search_ui = """
<ui>
	<toolbar name="ToolBar">
		<toolitem name="TabSearch-1" action="ToggleTabSearch" />
	</toolbar>
</ui>
"""

from TabConfigureDialog import TabConfigureDialog

# this class represents the tab search plugin
class TabSearchPlugin(GObject.Object, Peas.Activatable, PeasGtk.Configurable):
	__gtype_name__ = 'TabSearchPlugin'
	object = GObject.property(type=GObject.Object)

	def __init__ (self):
		GObject.Object.__init__ (self)

	def do_activate (self):
		self.context_view = TabSearch (self.object, self)

	def do_deactivate(self):
		self.context_view.deactivate(self.object)
		del self.context_view

class TabSearch(GObject.Object):
	def __init__(self, shell, plugin):
		GObject.Object.__init__(self)
		self.shell = shell
		self.sp = shell.get_player()
		self.db = shell.get_property('db')
		self.plugin = plugin

		self.settings = Gio.Settings("org.gnome.rhythmbox.plugins.tabsearch")
		self.sites = self.get_sites()
		self.tab_list = []
		self.info_tab = Tab('Info', 'Infos\n=====')

		self.visible = True

		self.init_gui()
		self.connect_signals()
		
		self.action_toggle = ('ToggleTabSearch', Gtk.STOCK_INFO, _('TabSearch'),
				None, _('Change the visibility of the tab search pane'),
				self.toggle_visibility, True)
		self.action_group = Gtk.ActionGroup('TabSearchActions')
		self.action_group.add_toggle_actions([self.action_toggle])
		
		# since the visibility toggle is per default set to TRUE,
		# click it once, if visibility in gconf is set to false!
		if self.settings.get_boolean('visible') == False:
			action = self.action_group.get_action('ToggleTabSearch')
			action.activate();
		
		uim = self.shell.get_ui_manager()
		uim.insert_action_group (self.action_group, 0)
		self.ui_id = uim.add_ui_from_string(tab_search_ui)
		uim.ensure_update()


	def init_gui(self) :
		print "TabSearch->init_gui"
		self.vbox = Gtk.VBox()
		
		self.toolbar = Gtk.Toolbar()
		self.toolitemSave = Gtk.ToolButton()
		self.toolitemSave.set_label('Save')
		self.toolitemSave.set_stock_id(Gtk.STOCK_SAVE)
		self.toolitemSave.connect('clicked', self.save_tabs)
		self.toolitemSave.set_sensitive(False)
		self.toolbar.add(self.toolitemSave)
		self.toolitemEdit = Gtk.ToolButton()
		self.toolitemEdit.set_label('Edit')
		self.toolitemEdit.set_stock_id(Gtk.STOCK_EDIT)
		self.toolitemEdit.connect('clicked', self.edit_tabs)
		self.toolitemEdit.set_sensitive(False)
		self.toolbar.add(self.toolitemEdit)
		self.toolitemLoad = Gtk.ToolButton()
		self.toolitemLoad.set_label('Load From Web')
		self.toolitemLoad.set_stock_id(Gtk.STOCK_REFRESH)
		self.toolitemLoad.connect('clicked', self.load_tabs_from_web)
		self.toolitemLoad.set_sensitive(False)
		self.toolbar.add(self.toolitemLoad)
		self.vbox.pack_start(self.toolbar, expand = False, fill = True, padding = 0)
		
		self.notebook = Gtk.Notebook()
		self.notebook.set_scrollable(True)
		
		self.vbox.set_size_request(250, -1)
		self.shell.add_widget(self.vbox, RB.ShellUILocation.RIGHT_SIDEBAR, expand=True, fill=True)
		self.vbox.show_all()

	# set the callback function 'playing_changed_cb'
	def connect_signals(self):
		self.player_cb_ids = (self.sp.connect('playing-changed', self.playing_changed_cb))

	# which sites did the user check in the configuration dialog?
	def get_sites(self):
		try:
			sites = self.settings['sites']
			if sites is None:
				sites = []
		except:
			print "Error: can't load the sites from configuration"
			sites = []
		print "tabs sites: " + str(sites)
		return sites
		
	# which folder did the user specify in the configuration dialog?
	# TODO: what's happening when the path is not valid?
	def get_tabfolder(self):
		try:
#			folder = gconf.client_get_default().get_string(self.gconf_keys['folder'])
			folder = self.settings.get_string('folder')
		except:
			print "Error: can't load the tab folder path from configuration"
		print "tabs folder: " + folder
		return folder

	def load_tabs_from_web(self, action):
		return self.load_tabs('web')

	# callback function that is triggered whenever there's 
	# a change in played song title
	def playing_changed_cb (self, playing, user_data):
		print "There's been a change in playback ..."
		self.info_tab.set_content('Infos\n=====')
		return self.load_tabs('hdd')

	def load_tabs(self, source):
		if self.visible is False:
			print "no visibility -> no need to look for tabs"
			return
		
		playing_entry = None
		if self.sp:
			playing_entry = self.sp.get_playing_entry()
		if playing_entry is None :
			return

#		playing_artist = self.db.entry_get (playing_entry, rhythmdb.PROP_ARTIST)
#		playing_title = self.db.entry_get (playing_entry, rhythmdb.PROP_TITLE)
		playing_artist = playing_entry.get_string(RB.RhythmDBPropType.ARTIST)
		playing_title = playing_entry.get_string(RB.RhythmDBPropType.TITLE)
		
		print "looking for '" + playing_artist + "' and the song '" + playing_title + "'"
		
		# passing the song info to the tab site parser
		# without removing the é and è from it.
		playing_artist = remove_accents(playing_artist)
		playing_title = remove_accents(playing_title)

		if playing_artist.upper() == "UNKNOWN":
			playing_artist = ""
			
		# resetting notebook
		if self.notebook in self.vbox.get_children():
			self.vbox.remove(self.notebook)
		self.vbox.show_all()
		self.notebook = None
		self.notebook = Gtk.Notebook()
		self.notebook.set_scrollable(True)
		self.notebook.connect('switch-page', self.update_toolbar)

		self.vbox.pack_start(self.notebook, expand = True, fill = True, padding=0)
		self.vbox.show_all()
		
		# Remove tabs from notebook
		self.tab_list = []
		self.info_tab.set_meta('artist', playing_artist)
		self.info_tab.set_meta('title', playing_title)
		
		if source == 'hdd':
			self.update_info_tab("\nchecking hdd for '" + playing_artist + "' and the song '" + playing_title + "'")
			self.open_tabs_from_hdd(playing_artist, playing_title)
		if source == 'web':
			self.update_info_tab("\nchecking web for '" + playing_artist + "' and the song '" + playing_title + "'")
			if not(playing_artist == ""):
				self.sites = self.get_sites()
				for s in self.sites:
					site_id = s
					if s == 'gt':
						gt = GuitareTabParser(self.add_tab_to_notebook, self.update_info_tab)
						gt.tabs_finder(playing_artist, playing_title)
					elif s == 'ug':
						ug = UltimateGuitarParser(self.add_tab_to_notebook, self.update_info_tab)
						ug.tabs_finder(playing_artist, playing_title)
					elif s == 'az':
						az = AZChordsParser(self.add_tab_to_notebook, self.update_info_tab)
						az.tabs_finder(playing_artist, playing_title)
					elif s == 'lc':
						lc = LacuerdaParser(self.add_tab_to_notebook, self.update_info_tab)
						lc.tabs_finder(playing_artist, playing_title)

	def deactivate (self, shell):
		print "Plugin deactivated."
		self.shell = None
		self.sp = None
		self.db = None
		self.plugin = None
		shell.remove_widget(self.vbox, RB.ShellUILocation.RIGHT_SIDEBAR)
		uim = shell.get_ui_manager()
		uim.remove_ui(self.ui_id)
		uim.remove_action_group(self.action_group)

	# toggles the visibility of the tab widget
	def toggle_visibility(self, action):
		print "Visibility set to " + str(not self.visible)
		if not self.visible:
			self.shell.add_widget(self.vbox, RB.ShellUILocation.RIGHT_SIDEBAR, expand=True, fill=True)
			self.visible = True
			self.load_tabs('hdd')
		else:
			self.shell.remove_widget(self.vbox, RB.ShellUILocation.RIGHT_SIDEBAR)
			self.visible = False
#		gconf.client_get_default().set_bool(self.gconf_keys['visible'], self.visible)
		self.settings.set_boolean('visible', self.visible)

	def edit_tabs(self, action):
		self.toolitemEdit.set_sensitive(False)
		self.get_current_tab().set_editable(True)
		self.toolitemSave.set_sensitive(True)

	# (de)activates the buttons on the toolbar depending on whether
	# they're useful in the current situation
	def update_toolbar(self, notebook, page, page_num):
		self.toolitemEdit.set_sensitive(False)
		self.toolitemSave.set_sensitive(False)
		self.toolitemLoad.set_sensitive(False)
		if page_num == 0:
			self.toolitemLoad.set_sensitive(True)
		if page_num > 0:
			self.toolitemEdit.set_sensitive(True)

	# returns the currently selected tab content
	def get_current_tab(self):
		currentTab = self.notebook.get_current_page()
		return self.notebook.get_nth_page(currentTab).get_child()
		
	# returns the currently selected tab content
	def get_current_tab_title(self):
		currentTab = self.notebook.get_current_page()
		currentTab = self.notebook.get_nth_page(currentTab)
		return self.notebook.get_tab_label(currentTab).get_text()

	# copies currently selected tabs to the hard disk
	def save_tabs(self, action):
		print 'saving tabs to hdd ...'
		self.toolitemSave.set_sensitive(False)
		self.toolitemEdit.set_sensitive(True)
		self.get_current_tab().set_editable(False)
		
		textbuffer = ""
		try:
			textbuffer = self.get_current_tab().get_buffer()
			textbuffer = textbuffer.get_text(textbuffer.get_start_iter() , textbuffer.get_end_iter(), 0)
		except:
			print 'Error: can\'t read current\'s tabs content'
		
		if textbuffer is None:
			print 'Error: loading current tabs failed'
			return
		
		directory = self.get_tabfolder() + '/' + self.info_tab.meta['artist'] + '/'
		
		try:
			os.makedirs(directory)
		except os.error:
			print 'Notice: directory\'s already existing'
		
		filename = directory + self.info_tab.meta['title'] + '.txt'
		
		try:
			file = open(filename, 'w')
		except:
			print "Error: can't open file"
			return
		
		file.write(textbuffer)
		file.close()
		print "-> saved successfully to hdd"
		self.load_tabs('hdd')


	def open_tabs_from_hdd(self, artist, title):
		filename = self.get_tabfolder() + '/' + artist + '/' + title + '.txt'
		print filename
		self.file_res = Gio.File.new_for_path(filename)
		self.file_res.load_contents_async(None, self.open_tabs_from_hdd_cb, {'source': 'hdd', 'artist': artist, 'title': title})

	def open_tabs_from_hdd_cb(self, gdaemonfile, result, params):
		try:
			result = self.file_res.load_contents_finish(result)
		except GError:
			print "Error: can't open file, maybe it's not there at all..."
			return
		successful = result[0]
		data = result[1]
		
		self.add_tab_to_notebook(data, params)

	def add_tab_to_notebook(self, data, params):
		#print data
		#print "add_tab_to_notebook !!!!"
		doAutoLookup = False
		if data is None:
			data = 'Illegal source selected...this shouldn\'t happen! Please contact plugin author!';
			if params['source'] == 'hdd':
				if not self.settings.get_boolean('preventautoweblookup'):
					doAutoLookup = True
				data = "\t   No tabs found on your hard disk.\n\t   Try checking the tab sites on the internet\n\t   by clicking on the 'load from web' button above."
			else:
				data = "you should not see this, check source code!"
				#data = "\t   Sorry! \""+title+"\" not found on selected tab sites.\n\t   Try checking other tab sites on the internet\n\t   by selecting other tab sites in the configuration dialog."
			self.update_info_tab('\t-> Nothing found!\n' + data)
		else:
			# inform user on info tab about success at fetching data
			self.update_info_tab('\t-> tabs found on ' + params['source'] + ' for \'' + params['artist'] + '\' - \'' + params['title'] + '\'.')
			tab = Tab('#' + str(len(self.notebook.get_children())) + ' ' + params['source'], data)
			tab.set_meta('artist', params['artist'])
			tab.set_meta('title', params['title'])
			self.tab_list.append(tab)
			self.update_notebook(params['source'], params['artist'], params['title'])
		if doAutoLookup:
			self.load_tabs('web')

	def update_info_tab(self, new_content):
		self.info_tab.add_content(new_content)
		
		if len(self.notebook.get_children()) == 0:
			# create info tab for the first time
			scroll = self.create_page(self.info_tab.content)
			self.notebook.prepend_page(scroll, Gtk.Label(self.info_tab.label))
		else:
			# update existing info tab
			infoTab = self.notebook.get_nth_page(0).get_child()
			textbuffer = infoTab.get_buffer()
			textbuffer.set_text(self.info_tab.content)
		self.notebook.show()
		self.vbox.show_all()

	def update_notebook(self, source, artist, title):
		""" Update notebook """
		if len(self.tab_list) == 0:
			print 'no tabs in tab_list !'
		else:
			# data tabs
			for tab in self.tab_list:
				if not(tab.label == "Not Found"): 
					scroll = self.create_page(tab.content)
					self.notebook.append_page(scroll, Gtk.Label(tab.label))
		self.tab_list = []
		self.notebook.show()
		self.vbox.show_all()

	def create_page(self, text):
		fontdesc = Pango.FontDescription("Courier New 8")
		textbuffer = Gtk.TextBuffer()
		textbuffer.set_text(text)
		textview = Gtk.TextView()
		textview.set_buffer(textbuffer)
		textview.set_editable(False)
		textview.modify_font(fontdesc)
		scroll = Gtk.ScrolledWindow()
		scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		scroll.set_shadow_type(Gtk.ShadowType.IN)
		scroll.add(textview) 
		scroll.show()
		return scroll


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

from TabSites import tab_sites
import rb
from gi.repository import Gtk, Gio, GObject, PeasGtk
from os import system, path

class TabConfigureDialog(GObject.Object, PeasGtk.Configurable):
	__gtype_name__ = 'TabConfigureDialog'
	object = GObject.property(type=GObject.Object)

	def __init__(self):
		GObject.Object.__init__(self)
		self.settings = Gio.Settings("org.gnome.rhythmbox.plugins.tabsearch")

	def do_create_configure_widget(self):
		builder = Gtk.Builder()
		print rb.find_plugin_file(self, "tab-prefs.ui")
		builder.add_from_file(rb.find_plugin_file(self, "tab-prefs.ui"))

		self.dialog = builder.get_object("preferences_dialog")

		self.path_display = builder.get_object("path_display")

		self.dialog.connect("response", self.dialog_response)

		preferences = self.get_prefs()

		site_box = builder.get_object("sites")
		self.site_checks = {}
		for s in tab_sites:
			site_id = s['id']
			checkbutton = Gtk.CheckButton(label = s['name'])
			checkbutton.set_active(s['id'] in preferences['sites'])
			self.site_checks[site_id] = checkbutton
			site_box.pack_start(checkbutton, expand=False, fill=True, padding=0)
		
		self.filechooser = builder.get_object('filechooser')
		self.filechooser.set_current_folder(preferences['folder'])
		
		self.preventAutoWebLookup_checkbutton = builder.get_object('preventAutoWebLookup_checkbutton')
		self.preventAutoWebLookup_checkbutton.set_active(preferences['preventAutoWebLookup'])
		
		self.default_folder_button = builder.get_object('default_folder_button')
		self.default_folder_button.connect('clicked', self.set_folderchooser_to_default)
		
		site_box.show_all()

	def set_folderchooser_to_default(self, param1):
		self.filechooser.set_current_folder(path.expanduser('~') + '/.cache/rhythmbox/tabs/')


	def dialog_response(self, dialog, response):
		if response == Gtk.ResponseType.OK:
			self.set_values()
			self.dialog.hide()
		elif response == Gtk.ResponseType.CANCEL or response == Gtk.ResponseType.DELETE_EVENT:
			self.dialog.hide()


	def set_values(self):
		# loading the preferences from dialog
		sites = []
		for s in tab_sites:
			check = self.site_checks[s['id']]
			if check is None:
				continue
			if check.get_active():
				sites.append(s['id'])
		folder = self.filechooser.get_current_folder()
		preventAutoWebLookup = self.preventAutoWebLookup_checkbutton.get_active()
		
		# storing the preferences into Gio.Settings
#		self.gconf.set_list(self.gconf_keys['sites'], gconf.VALUE_STRING, sites)
#		self.gconf.set_string(self.gconf_keys['folder'], folder)
#		self.gconf.set_bool(self.gconf_keys['preventAutoWebLookup'], preventAutoWebLookup)
		self.settings['sites'] = sites
		self.settings.set_string('folder', folder)
		self.settings.set_boolean('preventautoweblookup', preventAutoWebLookup)


	def get_dialog(self):
		return self.dialog
	
	def get_prefs(self):
		try:
#			sites = gconf.client_get_default().get_list(self.gconf_keys['sites'], gconf.VALUE_STRING)
			sites = self.settings['sites']
			if sites is None:
				sites = []
		except GObject.GError, e:
			print e
			sites = []
		try:
#			folder = gconf.client_get_default().get_string(self.gconf_keys['folder'])
			folder = self.settings.get_string('folder')
			if folder is None:
				folder = path.expanduser('~') + '/.cache/rhythmbox/tabs/'
		except GObject.GError, e:
			print e
			folder = path.expanduser('~') + '/.cache/rhythmbox/tabs/'
		try:
#			preventAutoWebLookup = gconf.client_get_default().get_bool(self.gconf_keys['preventAutoWebLookup'])
			preventAutoWebLookup = self.settings.get_boolean('preventautoweblookup')
		except GObject.GError, e:
			print e
			preventAutoWebLookup = False
		return {'sites': (sites), 'folder': folder, 'preventAutoWebLookup': preventAutoWebLookup}


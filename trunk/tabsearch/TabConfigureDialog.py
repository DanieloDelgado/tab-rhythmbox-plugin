
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

import gobject, gtk
import gconf
from os import system, path

class TabConfigureDialog (object):
	def __init__(self, builder_file, gconf_keys):
		self.gconf = gconf.client_get_default()
		self.gconf_keys = gconf_keys

		builder = gtk.Builder()
		builder.add_from_file(builder_file)
			
		self.dialog = builder.get_object("preferences_dialog")

		self.path_display = builder.get_object("path_display")

		self.dialog.connect("response", self.dialog_response)

		sites = self.get_prefs()

		site_box = builder.get_object("sites")
		self.site_checks = {}
		for s in tab_sites:
			site_id = s['id']
			checkbutton = gtk.CheckButton(label = s['name'])
			checkbutton.set_active(s['id'] in sites)
			self.site_checks[site_id] = checkbutton
			site_box.pack_start(checkbutton)

		site_box.show_all()

	def dialog_response(self, dialog, response):
		if response == gtk.RESPONSE_OK:
			self.set_values()
			self.dialog.hide()
		elif response == gtk.RESPONSE_CANCEL or response == gtk.RESPONSE_DELETE_EVENT:
			self.dialog.hide()


	def set_values(self):
		sites = []
		for s in tab_sites:
			check = self.site_checks[s['id']]
			if check is None:
				continue

			if check.get_active():
				sites.append(s['id'])


		self.gconf.set_list(self.gconf_keys['sites'], gconf.VALUE_STRING, sites)


	def get_dialog (self):
		return self.dialog
	
	def get_prefs (self):
		try:
			sites = gconf.client_get_default().get_list(self.gconf_keys['sites'], gconf.VALUE_STRING)
			if sites is None:
				sites = []
		except gobject.GError, e:
			print e
			sites = []

		print "tabs sites: " + str (sites)
		return (sites)


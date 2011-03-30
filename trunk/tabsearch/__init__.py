
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


import rb, rhythmdb
import TabSearch as tp
from TabConfigureDialog import TabConfigureDialog

gconf_keys = {
	'sites': '/apps/rhythmbox/plugins/tabsearch/sites',
	'folder': '/apps/rhythmbox/plugins/tabsearch/folder',
	'visible': '/apps/rhythmbox/plugins/tabsearch/visible',
	'preventAutoWebLookup': '/apps/rhythmbox/plugins/tabsearch/preventAutoWebLookup'
}

# this class represents the tab search plugin
class TabSearchPlugin(rb.Plugin):
	def __init__ (self):
		rb.Plugin.__init__ (self)

	def activate (self, shell):
		self.context_view = tp.TabSearch (shell, self, gconf_keys)

	def deactivate(self, shell):
		self.context_view.deactivate(shell)
		del self.context_view

	def create_configure_dialog(self, dialog=None):
		if not dialog:
			builder_file = self.find_file("tab-prefs.ui")
			dialog = TabConfigureDialog (builder_file, gconf_keys).get_dialog()
		dialog.present()
		return dialog


## Rhythmbox 3 ##

The users that have Rhythmbox 0.13 or later must install the SVN version (or the 0.5\_beta deb package) with the following commands:

  1. wget http://tab-rhythmbox-plugin.googlecode.com/svn/trunk/svn_install.sh
  1. sudo chmod +x svn\_install.sh
  1. sudo ./svn\_install.sh

Or manually enter:

  1. $ svn checkout http://tab-rhythmbox-plugin.googlecode.com/svn/trunk tab-rhythmbox-plugin-read-only
  1. $ cd tab-rhythmbox-plugin-read-only
  1. $ sudo cp -r tabsearch /usr/lib/rhythmbox/plugins/
  1. $ sudo cp tabsearch/tab-prefs.ui /usr/share/rhythmbox/plugins/tabsearch
  1. $ sudo cp tab-rhythmbox.svg /usr/share/rhythmbox/plugins/tabsearch
  1. $ sudo cp org.gnome.rhythmbox.plugins.tabsearch.gschema.xml /usr/share/glib-2.0/schemas/
  1. $ glib-compile-schemas /usr/share/glib-2.0/schemas/
  1. Launch Rhythmbox and activate the plugin


## Rhythmbox < 0.13 ##

For Rhythmbox 0.12 (no gtk3) must install the 0.4.1 version with the following commands or installing the deb package:
  1. $ sudo apt-get install python-lxml
  1. $ tar -xvzf tabsearch-0.4.1.tar.gz
  1. $ cp -r tabsearch/ $HOME/.gnome2/rhythmbox/plugins/
  1. Launch Rhythmbox and activate the plugin

## Installation from deb package ##
  1. Download the package from the downloads section
  1. $ sudo apt-get install python-lxml
  1. $ sudo dpkg -i <path + deb package filename>


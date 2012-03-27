#!/bin/sh
################################################
# Shell script to install tab-rhythmbox-plugin # 
# for rhythmbox > 0.12.9                       #
# Tested on Ubuntu 11.10                       #
################################################

if [ "$(id -u)" != "0" ]; then
	echo "This script must be run as root" 2>&1
else
	svn checkout http://tab-rhythmbox-plugin.googlecode.com/svn/trunk tab-rhythmbox-plugin-read-only
	cd tab-rhythmbox-plugin-read-only
	echo "Copying plugin files in /usr/lib/rhythmbox/plugins/"
	cp -r tabsearch /usr/lib/rhythmbox/plugins/

	echo "Copying plugin files in /usr/share/rhythmbox/plugins/"
	mkdir /usr/share/rhythmbox/plugins/tabsearch
	cp tabsearch/tab-prefs.ui /usr/share/rhythmbox/plugins/tabsearch
	cp tab-rhythmbox.svg /usr/share/rhythmbox/plugins/tabsearch
	
	echo "Copying schemas..."
	cp org.gnome.rhythmbox.plugins.tabsearch.gschema.xml /usr/share/glib-2.0/schemas/
	cd ..
	echo "Compiling schemas..."
	glib-compile-schemas /usr/share/glib-2.0/schemas/

	echo "Delete temporary files..."
	rm -rf tab-rhythmbox-plugin-read-only
fi
exit 1

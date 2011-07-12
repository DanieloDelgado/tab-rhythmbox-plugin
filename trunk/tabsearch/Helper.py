# -*- coding: utf-8 -*-

import unicodedata
import re

def remove_accents(str, strict = False):
	str = str.replace('Ä', 'Ae')	# Ärzte
	str = str.replace('Ü', 'Ue')
	str = str.replace('Ö', 'Oe')
	str = str.replace('ä', 'ae')
	str = str.replace('ü', 'ue')
	str = str.replace('ö', 'oe')
	str = str.replace('ß', 'ss')
	str = str.replace('`', '\'')
	str = str.replace('´', '\'')
	str = str.replace('"', '')
	if strict:
		str = str.replace('é', 'e')
		str = str.replace('è', 'e')
	#print type(str)
	nkfd_form = unicodedata.normalize('NFKD', str.decode('utf-8'))
	only_ascii = nkfd_form.encode('ASCII', 'ignore')
	#print str
	return str

def remove_html_tags(data):
	p = re.compile(r'<.*?>')
	return p.sub('', data)

def remove_par(data):
	p = re.compile(r'\(.*?\)')
	return p.sub('', data).strip()


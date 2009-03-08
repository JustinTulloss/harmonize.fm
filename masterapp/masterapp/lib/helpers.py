"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to both as 'h'.
"""
from webhelpers import *

import webhelpers.html.tags as tags

def javascript_link(path):
	return tags.javascript_link('/javascripts/' + path)

#A "potential" image tag
def p_image_tag(src, alt=None):
	if src not in [None, '']:
		return tags.image(src, alt)
	else: return ''

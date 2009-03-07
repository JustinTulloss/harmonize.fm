"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to both as 'h'.
"""
from webhelpers import *

import webhelpers.html.tags as tags

#A "potential" image tag
def p_image_tag(src):
	if src not in [None, '']:
		return tags.image(src)
	else: return ''

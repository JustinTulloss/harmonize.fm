"""Stolen from django"""

"""HTML utilities suitable for global use."""

import re
import string

from urllib import quote as urlquote

# Configuration for urlize() function.
LEADING_PUNCTUATION  = ['(', '<', '&lt;']
TRAILING_PUNCTUATION = ['.', ',', ')', '>', '\n', '&gt;']

# List of possible strings used for bullets in bulleted lists.
DOTS = ['&middot;', '*', '\xe2\x80\xa2', '&#149;', '&bull;', '&#8226;']

unencoded_ampersands_re = re.compile(r'&(?!(\w+|#\d+);)')
word_split_re = re.compile(r'(\s+)')
punctuation_re = re.compile('^(?P<lead>(?:%s)*)(?P<middle>.*?)(?P<trail>(?:%s)*)$' % \
    ('|'.join([re.escape(x) for x in LEADING_PUNCTUATION]),
    '|'.join([re.escape(x) for x in TRAILING_PUNCTUATION])))
simple_email_re = re.compile(r'^\S+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+$')
link_target_attribute_re = re.compile(r'(<a [^>]*?)target=[^\s>]+')
html_gunk_re = re.compile(r'(?:<br clear="all">|<i><\/i>|<b><\/b>|<em><\/em>|<strong><\/strong>|<\/?smallcaps>|<\/?uppercase>)', re.IGNORECASE)
hard_coded_bullets_re = re.compile(r'((?:<p>(?:%s).*?[a-zA-Z].*?</p>\s*)+)' % '|'.join([re.escape(x) for x in DOTS]), re.DOTALL)
trailing_empty_content_re = re.compile(r'(?:<p>(?:&nbsp;|\s|<br \/>)*?</p>\s*)+\Z')
del x # Temporary variable

def linebreaks(value, autoescape=False):
    """Converts newlines into <p> and <br />s."""
    value = re.sub(r'\r\n|\r|\n', '\n', unicode(value)) # normalize newlines
    paras = re.split('\n{2,}', value)
    if autoescape:
        paras = [u'<p>%s</p>' % escape(p.strip()).replace('\n', '<br />') for p in paras]
    else:
        paras = [u'<p>%s</p>' % p.strip().replace('\n', '<br />') for p in paras]
    return u'\n\n'.join(paras)
    #return value.strip().replace('\n', '<br />')

def strip_tags(value):
    """Returns the given HTML with all tags stripped."""
    return re.sub(r'<[^>]*?>', '', unicode(value))

def strip_spaces_between_tags(value):
    """Returns the given HTML with spaces between tags removed."""
    return re.sub(r'>\s+<', '><', unicode(value))

def strip_entities(value):
    """Returns the given HTML with all entities (&something;) stripped."""
    return re.sub(r'&(?:\w+|#\d+);', '', unicode(value))

def fix_ampersands(value):
    """Returns the given HTML with all unencoded ampersands encoded correctly."""
    return unencoded_ampersands_re.sub('&amp;', unicode(value))

def urlize(text, trim_url_limit=None, nofollow=False, autoescape=False):
    """
    Converts any URLs in text into clickable links.

    Works on http://, https://, www. links and links ending in .org, .net or
    .com. Links can have trailing punctuation (periods, commas, close-parens)
    and leading punctuation (opening parens) and it'll still do the right
    thing.

    If trim_url_limit is not None, the URLs in link text longer than this limit
    will truncated to trim_url_limit-3 characters and appended with an elipsis.

    If nofollow is True, the URLs in link text will get a rel="nofollow"
    attribute.

    If autoescape is True, the link text and URLs will get autoescaped.
    """
    trim_url = lambda x, limit=trim_url_limit: limit is not None and (len(x) > limit and ('%s...' % x[:max(0, limit - 3)])) or x
    words = word_split_re.split(unicode(text))
    nofollow_attr = nofollow and ' rel="nofollow"' or ''
    for i, word in enumerate(words):
        match = None
        if '.' in word or '@' in word or ':' in word:
            match = punctuation_re.match(word)
        if match:
            lead, middle, trail = match.groups()
            # Make URL we want to point to.
            url = None
            if middle.startswith('http://') or middle.startswith('https://'):
                url = urlquote(middle, safe='/&=:;#?+*')
            elif middle.startswith('www.') or ('@' not in middle and \
                    middle and middle[0] in string.ascii_letters + string.digits and \
                    (middle.endswith('.org') or middle.endswith('.net') or middle.endswith('.com'))):
                url = urlquote('http://%s' % middle, safe='/&=:;#?+*')
            elif '@' in middle and not ':' in middle and simple_email_re.match(middle):
                url = 'mailto:%s' % middle
                nofollow_attr = ''
            # Make link.
            if url:
                trimmed = trim_url(middle)
                if autoescape:
                    lead, trail = escape(lead), escape(trail)
                    url, trimmed = escape(url), escape(trimmed)
                middle = '<a href="%s"%s>%s</a>' % (url, nofollow_attr, trimmed)
                words[i] = '%s%s%s' % (lead, middle, trail)
            else:
                if autoescape:
                    words[i] = escape(word)
        elif autoescape:
            words[i] = escape(word)
    return u''.join(words)

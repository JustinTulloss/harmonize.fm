# -*- coding: utf-8 -*-
#
# Picard, the next-generation MusicBrainz tagger
# Copyright (C) 2004 Robert Kaye
# Copyright (C) 2006 Lukáš Lalinský
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import os.path
import re
import sys
import unicodedata
from astrcmp import astrcmp

def needs_read_lock(func):
    """Adds a read lock around ``func``.
    
    This decorator should be used only on ``LockableObject`` methods."""
    def locked(self, *args, **kwargs):
        self.lock_for_read()
        try:
            return func(self, *args, **kwargs)
        finally:
            self.unlock()
    locked.__doc__ = func.__doc__
    locked.__name__ = func.__name__
    return locked


def needs_write_lock(func):
    """Adds a write lock around ``func``.
    
    This decorator should be used only on ``LockableObject`` methods."""
    def locked(self, *args, **kwargs):
        self.lock_for_write()
        try:
            return func(self, *args, **kwargs)
        finally:
            self.unlock()
    locked.__doc__ = func.__doc__
    locked.__name__ = func.__name__
    return locked

_io_encoding = sys.getfilesystemencoding() 

def set_io_encoding(encoding):
    """Sets the encoding used in file names."""
    _io_encoding = encoding

def encode_filename(filename):
    """Encode unicode strings to filesystem encoding."""
    if isinstance(filename, unicode):
        if os.path.supports_unicode_filenames:
            return filename
        else:
            return filename.encode(_io_encoding, 'replace')
    else:
        return filename

def decode_filename(filename):
    """Decode strings from filesystem encoding to unicode."""
    if isinstance(filename, unicode):
        return filename
    else:
        return filename.decode(_io_encoding)

def pathcmp(a, b):
    return os.path.normcase(a) == os.path.normcase(b)

def format_time(ms):
    """Formats time in milliseconds to a string representation."""
    if ms == 0:
        return "?:??"
    else:
        return "%d:%02d" % (ms / 60000, (ms / 1000) % 60)

def sanitize_date(datestr):
    """Sanitize date format.
    
    e.g.: "YYYY-00-00" -> "YYYY"
          "YYYY-  -  " -> "YYYY"
          ...
    """
    date = []
    for num in datestr.split("-"):
        try:
            num = int(num.strip())
        except ValueError:
            break
        if num:
            date.append(num)
    return ("", "%04d", "%04d-%02d", "%04d-%02d-%02d")[len(date)] % tuple(date)

_unaccent_dict = {u'Æ': u'AE', u'æ': u'ae', u'Œ': u'OE', u'œ': u'oe', u'ß': 'ss'}
_re_latin_letter = re.compile(r"^(LATIN [A-Z]+ LETTER [A-Z]+) WITH")
def unaccent(string):
    """Remove accents ``string``."""
    result = []
    for char in string:
        if char in _unaccent_dict:
            char = _unaccent_dict[char]
        else:
            try:
                name = unicodedata.name(char)
                match = _re_latin_letter.search(name)
                if match:
                    char = unicodedata.lookup(match.group(1))
            except:
                pass
        result.append(char)
    return "".join(result)

_re_non_ascii = re.compile(r'[^\x00-\x7F]', re.UNICODE)
def replace_non_ascii(string, repl="_"):
    """Replace non-ASCII characters from ``string`` by ``repl``."""
    return _re_non_ascii.sub(repl, string)

_re_win32_incompat = re.compile(r'[\\"*/:<>?|]', re.UNICODE)
def replace_win32_incompat(string, repl=u"_"):
    """Replace win32 filename incompatible characters from ``string`` by
       ``repl``."""
    return _re_win32_incompat.sub(repl, string)

_re_non_alphanum = re.compile(r'\W+', re.UNICODE)
def strip_non_alnum(string):
    """Remove all non-alphanumeric characters from ``string``."""
    return _re_non_alphanum.sub(u" ", string)

_re_slashes = re.compile(r'[\\/]', re.UNICODE)
def sanitize_filename(string, repl="_"):
    return _re_slashes.sub(repl, string)

def make_short_filename(prefix, filename, length=240, max_length=200,
                        mid_length=32, min_length=2):
    parts = [part.strip() for part in _re_slashes.split(filename)]
    parts.reverse()
    filename = os.path.join(*parts)
    left = len(prefix) + len(filename) + 1 - length

    for i in range(len(parts)):
        left -= max(0, len(parts[i]) - max_length)
        parts[i] = parts[i][:max_length]

    if left > 0:
        for i in range(len(parts)):
            length = len(parts[i]) - mid_length
            if length > 0:
                length = min(left, length)
                parts[i] = parts[i][:-length]
                left -= length
                if left <= 0:
                    break

        if left > 0:
            for i in range(len(parts)):
                length = len(parts[i]) - min_length
                if length > 0:
                    length = min(left, length)
                    parts[i] = parts[i][:-length]
                    left -= length
                    if left <= 0:
                        break

            if left > 0:
                raise IOError, "File name is too long."

    return os.path.join(*[a.strip() for a in reversed(parts)])


def _reverse_sortname(sortname):
    """Reverse sortnames."""
    chunks = [a.strip() for a in sortname.split(",")]
    if len(chunks) == 2:
        return "%s %s" % (chunks[1], chunks[0])
    elif len(chunks) == 3:
        return "%s %s %s" % (chunks[2], chunks[1], chunks[0])
    elif len(chunks) == 4:
        return "%s %s, %s %s" % (chunks[1], chunks[0], chunks[3], chunks[2])
    else:
        return sortname.strip()


def translate_artist(name, sortname):
    """'Translate' the artist name by reversing the sortname."""
    for c in name:
        ctg = unicodedata.category(c)
        if ctg[0] not in ("P", "Z") and ctg != "Nd" and unicodedata.name(c).find("LATIN") == -1:
            return " & ".join(map(_reverse_sortname, sortname.split("&")))
    return name


try:
    from functools import partial
except ImportError:
    def partial(func, *args, **keywords):
        def newfunc(*fargs, **fkeywords):
            newkeywords = keywords.copy()
            newkeywords.update(fkeywords)
            return func(*(args + fargs), **newkeywords)
        newfunc.func = func
        newfunc.args = args
        newfunc.keywords = keywords
        return newfunc


def find_existing_path(path):
    path = encode_filename(path)
    while path and not os.path.isdir(path):
        head, tail = os.path.split(path)
        if head == path:
            break
        path = head
    return decode_filename(path)


def call_next(func):
    def func_wrapper(self, *args, **kwargs):
        next = args[0]
        result = None
        try:
            result = func(self, *args, **kwargs)
        except:
            import traceback
            self.log.error(traceback.format_exc())
            next(error=sys.exc_info()[1])
        else:
            next(result=result)
    func_wrapper.__name__ = func.__name__
    return func_wrapper

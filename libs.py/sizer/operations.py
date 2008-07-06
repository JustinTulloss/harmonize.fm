"""Simple operations (filtering, and so on) on groups of objects.
You must call cut or fix on the results of these before trying any annotations."""

from wrapper import *
from rules import ZeroObject
from cpython import utils
import scanner

def bytype(sizes):
    """Collect objects into types, returning a dictionary from type to
    (type, total size, sample object).

    Can be printed using formatting.printsizesop."""
    
    types = ignoredict()
    for i in sizes.values():
        if not types.has_key(id(i.type)):
            val = (i.type, 0, i)
            types[id(i.type)] = val
        else:
            val = types[id(i.type)]
            
        types[id(i.type)] = (val[0], val[1] + i.size, val[2])

    return types

def bysize(wrappers):
    """Collect objects into sizes, returning a dictionary from size to
    (size, total size, sample object).
    
    Can be printed using formatting.printsizesop."""
    
    sizes = ignoredict()
    for w in wrappers.values():
        if not sizes.has_key(w.size):
            val = (w.size, 0, w)
            sizes[w.size] = val
        else:
            val = sizes[w.size]
            
        sizes[w.size] = (val[0], val[1] + w.size, val[2])
            
    return sizes

def byframe(wrappers):
    """Collect objects according to the file name and line number of code where
    they were created.

    Can be printed using formatting.printsizesop."""

    frames = ignoredict()
    for w in wrappers.values():
        frame = utils.objframe(w.obj)

        if not frames.has_key(frame):
            val = (frame, 0, w)
            frames[frame] = val
        else:
            val = frames[frame]

        frames[frame] = (val[0], val[1] + w.size, val[2])

    return frames

def filterd(dict, pred):
    """Filter a dictionary of wrappers. Returns a dictionary of wrappers
    containing the wrappers w such that pred(w) is true."""
    
    try:
        result = scanner.Objects(objs = {}, head = dict.head, flags = {})
    except AttributeError:
        result = ignoredict()

    for i in dict:
        if pred(dict[i]):
            result[i] = dict[i]
    return result

def filtertype(dict, atype):
    """Filter a dictionary of wrappers by type. Returns a dictionary
    giving only those wrappers whose object's type is atype."""
    
    return filterd(dict, lambda w: w.type is atype)

def filtersize(dict, asize):
    """Filter a dictionary of wrappers by size. Returns a dictionary
    giving only those wrappers whose object's size is asize."""
    
    return filterd(dict, lambda w: w.size == asize)

def filterouttype(dict, atype):
    """Filter out a dictionary by type. Returns a dictionary giving all
    wrappers except those whose object's type is atype."""
    
    return filterd(dict, lambda w: w.type is not atype)

def sorted(sizes):
    """Takes a dictionary of wrappers, and returns a sorted list of wrappers,
    with the largest first."""
    
    l = [ (w.size, id(w.obj)) for w in sizes.values() ]
    l.sort()
    l.reverse()

    return ignorelist([ sizes[i[1]] for i in l ])

def toplist(n, sizes):
    """Takes a dictionary of wrappers, and returns a sorted list containing the
    biggest n in descending order (largest first)."""
    
    return ignorelist(sorted(sizes)[:n])

def top(n, sizes):
    """Takes a dictionary of wrappers, and returns a dictionary containing only
    the biggest n."""
    
    result = ignoredict()
    for w in toplist(n, sizes):
        result[id(w.obj)] = w
    return result

def pos(n, sizes):
    """Takes a dictionary of wrappers, and returns the nth biggest one.
    If there are less than n wrappers, returns the smallest."""
    
    l = toplist(n, sizes)

    if n >= len(l):
        return l[len(l) - 1]
    else:
        return l[n]

def diff(sizes1, sizes2):
    """Takes two dictionaries sizes1 and sizes2 of wrappers, and returns
    sizes2 \ sizes1 - i.e. the objects found in sizes2 but not sizes1."""
    
    newsizes = ignoredict()
    for i in sizes2:
        if i not in sizes1:
            newsizes[i] = sizes2[i]
    return newsizes

def cut(wrappers):
    """Takes a dictionary of wrappers, and removes all references to wrappers
    not in the dictionary from it. This will make the dictionary valid for
    functions in annotate.
    
    You should call this on anything you get from operations before you call
    the functions from annotate on them.

    This function changes the wrappers in-place."""
    
    #if id(None) not in wrappers:
        #wrappers[id(None)] = ZeroObject(None)
    
    #for w in wrappers:
        #for l in wrappers[w].update:
            #i = 0
            #length = len(l)
            #while i < length:
                #if id(l[i].obj) not in wrappers:
                    #del l[i]
                    #length -= 1
                #else:
                    #i += 1
        #for d in wrappers[w].updatedict:
            #for l in d.keys():
                #if id(d[l].obj) not in wrappers:
                    #del d[l]

    assert id(wrappers.head.obj) in wrappers, \
           "Cannot fix wrappers because head has been removed"
    
    for w in wrappers:
        wrappers[w].cut(wrappers)
        
def fix(wrappers):
    """Takes a dictionary of wrappers, and removes all references to wrappers
    not in the dictionary from it. This will make the dictionary valid for
    functions in annotate.
    
    You should call this on anything you get from operations before you call
    the functions from annotate on them.

    This function returns a new set of wrappers."""
    
    new = wrappers.copy()
    cut(new)
    return new

#
# Find as many objects as possible, for the rest of the system to deal with
#

import sizes
import rules
import wrapper
import warnings
import sys

class UnknownType(Warning):
    pass

def _replacetype(t, dict):
    # Some of the entries in sizes are indexed by string, since there's no good
    # prototype object to use.
    # Search for this object as a string in there and replace the entry if it's
    # found.
    # Also search for keys which are of the form type rather than id(type).
    
    if t in dict:
        dict[id(t)] = dict[t]
    elif rules.getname(t) in dict:
        dict[id(t)] = dict[rules.getname(t)]

    return dict
    
# This class can wrap an object which has used multiple inheritance.
# It will make a wrapper for each of its supertypes in turn and then
# try to combine them.
def multiplewrapper(constructors):
    # Make a new type inheriting from all the object's parts.
    # Name clashes should be avoided as long as the wrapper structure
    # mirrors the object structure - for example, a class inheriting
    # from dict and dictproxy is not valid, so DictObject will only
    # appear once in an object.
    
    wrapper = type("MultipleWrapper", tuple(constructors), {})
    
    # Hopefully, this is all we need...it looks much better than join.
    # Faster, too :-)
    return wrapper

def _findwrapper(obj, t, unknown, guess):
    # Find or make an appropriate wrapper class for an object.
    # If guess is false, will return None if it couldn't count the object
    # very well.
    
    # Check for an object with a specific rule
    if id(obj) in sizes.object:
        return sizes.object[id(obj)]
            
    # Check for a type with a specific rule
    if id(t) in sizes.wholetype:
        return sizes.wholetype[id(t)]

    # Check sizes.instance.
    try:
        mro = type.mro(t)
        
        for super in mro:
            if id(super) in sizes.instance or \
               id(super) in _replacetype(super, sizes.instance):
                return sizes.instance[id(super)]
    except TypeError:
        # Without an MRO we can't tell what this object is made of
        # (Zope extension classes, for example, have their own type
        # which is completely unrelated to __builtins__.type :( )
        if guess:
            unknown(default, obj)
            return rules.UnknownObject
        else:
            return None

    # Try to make a wrapper class using the MRO.
    constructors = []
    
    mro = type.mro(t)
        
    for super in mro:
        if id(super) in sizes.type or \
           id(super) in _replacetype(super, sizes.type):
            constructors.append(sizes.type[id(super)])

    # The constructor list will be in a bad order, with duplicates.
    # Make a proper order. We do this (assuming that the wrapper classes
    # can be combined) by only adding a class if it has not appeared
    # (directly or as a subclass of something else) yet.
    # This algorithm is inefficient, but is only called once for each
    # type.
    
    # Make the class list in reverse order
    classes = []
    while len(constructors) > 0:
        cls = constructors.pop()
        # If this type has not been counted...
        if cls not in classes:
            clsmro = cls.mro()
            clsmro.reverse()
            for cls2 in clsmro:
                # Include subclasses only if not counted to avoid duplicates
                if cls2 not in classes:
                    classes.append(cls2)
    classes.reverse()
                    
    # Now we have a list of types we can use.
    # Combine their wrappers into a wrapper for the whole
    # type.
    constructor = multiplewrapper(classes)
    
    # Decide whether to give out a warning.

    # Verbose: produce a warning unless all parts of MRO were recognised.
    if len(constructors) < len(mro):
        unknown(verbose, obj)
    
    # Default: produce a warning if __getattribute__ is not recognised.
    for super in mro:
        if id(t) in sizes.type or (t is not super and
           _findwrapper(obj, super, lambda level, obj: None, False) is not None
           and t.__getattribute__ is super.__getattribute__):
            break
    else:
        if guess:
            unknown(default, obj)
        else:
            return None

    return constructor

# Verbosity levels.
# verbose produces warnings for all unknown types, even completely ordinary
# user-defined ones.
# default produces warnings for objects which seem to be weird and are
# unknown (in particular ones which override __getattribute__ and can
# only be counted as an instance of object).
# silent produces no warnings.
verbose = 2
default = 1
silent = 0

try:
    import gc
    _gc_collect = gc.collect
except ImportError:
    def _gc_collect():
        pass

def scan(obj, verbosity = default):
    # The number of objects counted so far
    count = 0
    
    sys.stdout.write("Scanning..")
    sys.stdout.flush()
    
    # Give out a warning about an unknown object if verbosity >= level.
    def unknown(level, obj):
        if verbosity >= level:
            warnings.warn("Size of %s not known" % type(obj), UnknownType)
    
    # Annotations leave lots of cyclic references, so clean them up if we can
    _gc_collect()
    
    wrappers = wrapper.ignoredict()
    queue = wrapper.ignorelist([None, obj])
    
    while len(queue) > 0:
        obj = queue.pop()
        
        # Check for an already-counted object
        if id(obj) in wrappers:
            continue
        
        count += 1
        if count % 1000 == 0:
            sys.stdout.write(".")
            sys.stdout.flush()
        
        t = type(obj)
        
        # Check for an object with a specific rule
        if id(obj) in sizes.object:
            constructor = sizes.object[id(obj)]
            
        # Check for a type with a specific rule
        elif id(t) in sizes.wholetype:
            constructor = sizes.wholetype[id(t)]
            
        # Go through the slow code to find or make a wrapper class
        else:
            constructor = _findwrapper(obj, t, unknown, True)
            sizes.wholetype[id(t)] = constructor
            sizes.samples[id(t)] = obj
            
        # Now generate a wrapper.
        w = constructor(obj)
        queue += w.children
        wrappers[id(obj)] = w

    # Change object IDs to wrapper references
    print
    sys.stdout.write("Lifting..")
    count = 0
    for w in wrappers:
        count += 1
        if count % 1000 == 0:
            sys.stdout.write(".")
            sys.stdout.flush()

        wrappers[w].scanfinished(wrappers)
        wrappers[w].liftrefs(wrappers)

    print

    return wrappers

class Objects(dict, wrapper.ignored):
    """The set of object wrappers returned by scanner.
    
    Instantiate this to get a dictionary of wrappers."""

    def __init__(self, obj = rules.roots(), objs = None, head = None,
                 verbosity = default, flags = None):
        if objs is None:
            objs = scan(obj, verbosity)
        if head is None:
            head = objs[id(obj)]
        if flags is None:
            flags = {}
            
        wrapper.ignored.__init__(self)        
        dict.__init__(self, objs)
        self.head = head
        self.flags = {}

    def copy(self):
        """Return a copy of this set of wrappers."""
        
        return self.map(lambda w: w.copy())

    def shallowcopy(self, flags = None):
        """Return a copy of this object, containing the original
        wrappers."""
        
        if flags is None:
            flags = {}
        
        return Objects(objs = self, head = self.head, flags = dict(flags))
    
    def map(self, f, flags = None):       
        """Return this object with each wrapper mapped through f."""
        
        # Make a copy of the original wrappers
        new = self.shallowcopy(flags)
        head = id(self.head.obj)
        
        # Replace each wrapper with its image in f.
        for w in new:
            mapped = f(new[w])
            new[w] = mapped
            if head == w:
                self.head = mapped
                
        # Wrapper references in the new set will be pointing into this
        # set, so reconstruct them
        for w in new:
            new[w].wrappers = new
        for w in new:
            new[w].droprefs(new)
            new[w].liftrefs(new)
            
        return new

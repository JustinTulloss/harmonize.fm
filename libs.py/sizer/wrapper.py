import sizes
import copy

from set import *

class ignored(object):
    """Any subtype of this is ignored by the scanner."""
    pass

class ignoredict(dict, ignored):
    pass
class ignorelist(list, ignored):
    pass
class ignoretuple(tuple, ignored):
    pass

class ObjectWrapper(ignored):
    """A wrapper which contains as much useful information as we can find about
    a single object. Defined by this class:

    obj - the object being counted.

    type - the class of the object, not necessarily type(obj).
    
    size - the size of the object on its own.
    
    children - a list of all objects referenced by this one.
    
    times - a list of update times, which can be used to decide
    when child objects first appeared in their parent objects.
    The time for children[i] is at times[i].
    
    wrappers - a reference back to the wrapper dictionary.

    Annotations may add other fields - this might be changed soon, though."""
    
    # This might save a bit of space in each wrapper...
    __slots__ = ["obj", "type", "size", "children", "times", "wrappers",
                 "parents", "group", "contained", "parent", "depth", "time",
                 "_reached"]
    
    def __init__(self, obj):
        """Constructor. Does not fill out much because it will only
        be called once."""
        
        self.obj = obj
        self.size = 0
        self.children = ignorelist()
        self.times = ignorelist()
        self.type = type(obj)
        #self.addchild(type(obj), 0)
        
    def addchildren(self, children, times):
        """Record more children of this object.
        
        children is a sequence of objects (not wrappers).
        The update time for children[i] is taken from times[i]."""

        # Note: children is implicitly copied. The original list
        # must not be kept by this code.
        for (c, t) in zip(children, times):
            self.addchild(c, t)
            
    def addchild(self, child, time):
        """Record another child of this object (see addchildren)."""
        self.children.append(child)
        self.times.append(time)
        
    def scanfinished(self, wrappers):
        """Called once all objects have been scanned, but before
        liftrefs has been called."""
        
        # Remove duplicate children and take times with them.
        # If there are not many children, don't bother constructing a set.
        if len(self.children) < 50:
            childid = map(id, self.children)
            for (i, c) in enumerate(self.children):
                if id(c) in childid[:i]:
                    self.children[i] = None
        
        else:
            children = set()
            for (i, c) in enumerate(self.children):
                if id(c) in children:
                    self.children[i] = None
                else:
                    children.add(id(c))

        self.wrappers = wrappers
    
    def liftrefs(self, wrappers):
        """Transform object references into wrapper references.
        It's called by the scanner, and must not be called again."""
        
        # It would perhaps be cleaner to construct a new wrapper with a
        # different type instead, but that could be very slow.
        
        for (i, c) in enumerate(self.children):
            try:
                self.children[i] = wrappers[id(c)]
            except KeyError:
                # Profiling the scanner seems to cause this...
                self.children[i] = wrappers[id(None)]

        self.children = ignoretuple(self.children)
        self.times = ignoretuple(self.times)
        
    def droprefs(self, wrappers):
        """The opposite of liftrefs: transform wrapper references into
        direct object references."""
        
        self.children = ignorelist([ w.obj for w in self.children ])
        
    def copy(self):
        """Return a copy of this wrapper.
        
        This shouldn't be used directly - call copy on the set of
        wrappers instead (i.e. objs.copy() instead of objs[w].copy())."""
        
        ret = ObjectWrapper.__new__(type(self))
        ret.obj = self.obj
        ret.size = self.size
        ret.children = ignoretuple(self.children)
        ret.times = ignoretuple(self.times)
        ret.type = self.type
        return ret

    def cut(self, wrappers):
        """Remove any wrapper references which are not found in wrappers.

        This will make the wrapper valid after removing other wrappers.
        It's called by operations.cut."""

        ct = [ (c, t) for (c, t) in zip(self.children, self.times)
               if id(c.obj) in wrappers ]
        
        self.children = ignoretuple([ c for (c, t) in ct ])
        self.times = ignoretuple([t for (c, t) in ct ])
    
    def __str__(self):
        return "wrap " + self.show()

    def __repr__(self):
        return "wrap " + self.show()
    
    def show(self, default = True):
        """Return a string representation of the object.
        
        If default is false, will not include information from the
        default implementation (type, address and so on)."""
        if default:
            return type(self.obj).__name__ + " at " + hex(id(self.obj))
        else:
            return ""

ZeroObject = ObjectWrapper
sizes.instance[ignored] = ZeroObject

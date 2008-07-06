"""Various functions to add information to the wrapper objects.

The information might be lost when you copy the wrappers (using
wrappers.copy() or operations.fix(wrappers). This is a bug."""

import rules
import wrapper
import warnings
import operations
import types
import scanner
import heapq
import sys

from set import *

def _toset(l):
    """Turns a list into a set. If it's already a set, returns the input
    (not even a shallow copy)."""
    
    if isinstance(l, set) or isinstance(l, frozenset):
        return l
    elif isinstance(l, dict):
        # Assume this is a mapping from object ID to wrapper
        return set(l.values())
    else:
        return set(l)

pre = 0
post = 1

def flatten(wrappers, order = pre, head = None, cycle = lambda w, p: None):
    """Iterate through wrappers, yielding a pre-order traversal of the
    form (wrapper, parent), where parent is None for head.
    
    In case of a cycle (which just about every set of objects will have),
    the function "cycle" is called on the wrapper, which by default does
    nothing."""
    
    if head is None:
        head = wrappers.head
    
    reached = set()
    
    def flattenfrom(wrapper, parent):
        if id(wrapper) in reached:
            cycle(wrapper, parent)
        else:
            reached.add(id(wrapper))
            
            if order == pre:
                yield (wrapper, parent)
            
            for child in wrapper.children:
                for w in flattenfrom(child, wrapper):
                    yield w
                    
            if order == post:
                yield (wrapper, parent)
    
                for w in flattenfrom(head, None):
                    yield w
                    
    return flattenfrom(head, None)

def markparents(wrappers):
    """Add a field "parents" to each wrapper, containing the objects which
    reference the child object."""
    
    if hasattr(wrappers, "markedparents"):
        return
    
    # First add no parents
    for w in wrappers.values():
        w.parents = []

    # Now add every parent we can
    for w in wrappers.values():
        for child in w.children:
            child.parents.append(w)
            
    wrappers.markedparents = True

def addcontained(wrappers):
    """If an object has only one parent, include it in the size of the parent.
    This should go some way towards making sizes accurate.
    
    Note: this won't include any cyclic references."""
    
    markparents(wrappers)
    toremove = []
    
    for w in wrappers.values():
        w.contained = []

    # Collapse children into parents
    for (w, p) in flatten(wrappers, post):
        if len(w.parents) == 1:
            p.size += w.size
            p.contained.append(w)
            p.children += w.children
            toremove.append(w)
            
    # Remove any wrappers which are now contained
    for w in toremove:
        del wrappers[id(w.obj)]
        
    # Fix the set of wrappers after we've grotesquely mutated it :-)
    operations.cut(wrappers)
    
    # Hack: markparents will not be fixed by cutting. Do that again
    # by hand.
    del wrappers.markedparents
    markparents(wrappers)
        
# This is used to collect groupless objects
class NoGroup(wrapper.ignored):
    pass
nogroup = NoGroup()
del NoGroup
class NoGroupWrapper(wrapper.ObjectWrapper):
    def show(self, default = True):
        return "<unknown>"
class GroupWrapper(wrapper.ObjectWrapper):
    def show(self, default = True):
        return self.main.show(default)

def groupby(wrappers, groups, split = None):
    """Assign each object in wrappers to a member of groups.
    Returns a dictionary which maps from object id to ObjectWrapper.
    Objects which can't be put in a group are put in noGroup.
    
    Also sets group, time and parent for each object, and members and
    totalSize for each group.
    
    For example, setting groups to a list of modules will assign
    each object to a module.

    split is a set of objects which mark the end of a group - once they're
    reached they're not looked at further. By default it's the set of
    groups so, for example, if module A contains module B objects that
    can only be reached via B will not be grouped under A."""
    
    # We do yet another depth-first search from each object in groups.
    # It's probably not very efficient but should do for now -
    # with lots of references, it becomes O(length(wrappers)^2) :-(
    # We put each object in noGroup initially and move it if we find somewhere
    # better to put it.
    
    # For the moment, information about each object's group is stored in the
    # object itself. This means that only one grouping is available at any time.
    
    # Turn groups and split into sets, for efficient membership testing
    groups = _toset(groups)
    
    if split is None:
        split = groups
    else:
        split = _toset(split)
    
    # Now set up the group dictionary
    mynogroup = NoGroupWrapper(nogroup)
    groupdict = scanner.Objects(None, {}, mynogroup)
    for g in groups:
        groupdict[id(g.obj)] = GroupWrapper(g.obj)
        groupdict[id(g.obj)].main = g
        groupdict[id(g.obj)].samples = {}
    groupdict[id(nogroup)] = mynogroup
    groupdict[id(nogroup)].main = mynogroup
    groupdict[id(nogroup)].samples = {}

    # Reset group information in objects and mark all as unreached
    for w in wrappers.values():
        if hasattr(w, "group"):
            warnings.warn("Deleting old group information from wrappers")
        
        if w in groups:
            w.group = groupdict[id(w.obj)]
            w.parent = w
            w.depth = 0
            w.time = 0 # Very old
        else:
            w.group = groupdict[id(nogroup)]
            w.parent = None
            w.depth = sys.maxint
            w.time = sys.maxint # Very new :-)
            
        w._reached = False
        
    # Work out the depth of each object from a group, using Dijkstra's 
    # algorithm.

    # counted is a heap of (depth, wrapper) pairs for all wrappers
    # whose depth is known but whose childrens' depth is not.
    # Comparison on tuples will return (d1, w1) < (d2, w2) if d1 < d2,
    # so this will work as a heap.
    counted = [ (0, w) for w in groups ]
    heapq.heapify(counted)
    
    while len(counted) != 0:
        # Remove the wrapper with the shortest depth from the heap
        (depth, w) = heapq.heappop(counted)
        
        # But...depth might have changed since it was put in the heap.
        if depth != w.depth:
            heapq.heappush(counted, (w.depth, w))
        
        # Update the depths of all children.
        for c in w.children:
            if w.depth + 1 < c.depth:
                c.depth = w.depth + 1
                heapq.heappush(counted, (c.depth, c))
        
    # Enumerate objects from each group.
    for g in groups:
        for (c, t) in zip(g.children, g.times):
            _groupfrom(wrappers, groupdict[id(g.obj)], c, g, t, groups, split)
            
    # Remove junk _reached attribute
    for w in wrappers.values():
        del w._reached
        
    # Build a dict of members for each group
    for g in groups:
        groupdict[id(g.obj)].members = {}
        groupdict[id(g.obj)].size = 0
    groupdict[id(nogroup)].members = {}
    groupdict[id(nogroup)].size = 0

    # Work out the size of the group, and make child links to other groups
    for w in wrappers.values():
        w.group.members[id(w.obj)] = w
        w.group.size += w.size
        
        for (c, t) in zip(w.children, w.times):
            if c.group is not w.group:
                # Hopefully there shouldn't be too many groups...
                try:
                    index = w.group.times.index(c.group)
                
                    # Find the earliest time at which the group was contained
                    if w.group.times[index] > t:
                        w.group.times[index] = t
                except ValueError:
                    w.group.times.append(t)
                    w.group.children.append(c.group)
                    w.group.samples[id(c.group.obj)] = c
            
    groupdict.head = wrappers.head.group
    return groupdict
    
def _groupfrom(wrappers, g, w, parent, childtime, groups, split):
    assert parent.group is g
    assert isinstance(groups, set) or isinstance(groups, frozenset)
    assert isinstance(split, set) or isinstance(split, frozenset)
    
    # Stop if we've reached a split or the w's already been reached
    if w in split or w._reached:
        return
      
    # This marks that w has been reached, to prevent infinite recursion    
    w._reached = True
    
    # w's time relative to this group is max(w's time relative to parent,
    # parent's time relative to group).
    time = max(childtime, parent.time)
    
    if time < w.time:
        w.time = time
        w.group = parent.group
        w.parent = parent
        
        for (c, t) in zip(w.children, w.times):
            _groupfrom(wrappers, g, c, w, t, groups, split)
    elif time == w.time and id(w.parent.obj) != id(parent.obj):
        # Use depth to break ties
        if parent.depth < w.parent.depth:
            w.time = time
            w.group = parent.group
            w.parent = parent
            for (c, t) in zip(w.children, w.times):
                _groupfrom(wrappers, g, c, w, t, groups, split)
        
    w._reached = False

def simplegroupby(wrappers, modules = False, threads = False, classes = False):
    """Assign each object in wrappers to a module, thread or class.
    The values of "modules", "threads" and "classes" control whether those are
    included (for example, having modules = True, threads = classes = False
    will assign each object to a module only).
    
    Returns a dictionary mapping from module ID or id(noGroup)
    to module object.
    
    Also sets "group" and "time" fields for each object, and "members" for 
    each module."""

    def constfalse(w):
        return False
    
    if modules:
        def ismodule(w):
            return type(w.obj) is types.ModuleType
    else:
        ismodule = constfalse
        
    if threads:
        # threadlist is a list of id(thread)
        threadlist = map(id, rules.roots())
        def isthread(w):
            return id(w) in threadlist
    else:
        isthread = constfalse
        
    if classes:
        def isclass(w):
            # Check for old-style classes, modules and frames
            if type(w.obj) is types.InstanceType or type(w.obj) is types.ClassType \
            or type(w.obj) is types.ModuleType or type(w.obj) is types.FrameType:
                return True
    
            # This is the code that scanner.py uses to check for new-style classes
            try:
                attr_obj = w.obj.__getattribute__
                attr = type(w.obj).__getattribute__
                if attr == object.__getattribute__ or attr == type.__getattribute__:
                    return True
            except AttributeError:
                return False
            
            return False
    else:
        isclass = constfalse
        
    def isgroup(w):
        return ismodule(w) or isthread(w) or isclass(w)
    
    return groupby(wrappers, operations.filterd(wrappers, isgroup))

def findcycles(wrappers):
    """Yields all cycles in the wrappers."""
    
    # Should probably be done as a topological sort, as that would get extra
    # interesting information.

    cycles = wrapper.ignorelist()
    for w in wrappers:
        wrappers[w]._reached = False

    for c in findcyclesfrom(wrappers.head, cycles, []):
        # Skip cycles with types or classes in (there are cycles everywhere
        # there), and ones with functions (e.g. f->f.func_globals->f)
        # Is there any use for finding cycles, really?
        for w in c:
            if w.type is type or w.type is types.FunctionType or \
               w.type is types.BuiltinFunctionType:
                break
        else:
            yield c

    for w in wrappers:
        del wrappers[w]._reached
        
    #return cycles
    
def findcyclesfrom(w, cycles, path):
    """Yields all cycles that can be found from w."""
    
    if w._reached:
        # Search for the beginning of the cycle
        for i in xrange(len(path)):
            if path[i] is w:
                yield path[i:]
                break
        else:
            assert False, "Can't find start of cycle"

        #cycles.append(path[:])
        return

    path.append(w)
    w._reached = True
    for c in w.children:
        for cy in findcyclesfrom(c, cycles, path):
            yield cy
    path.pop()
    w._reached = False

def findcreators(wrappers):
    """Given a set of wrappers, returns a structure which can be used to
    find what objects each line of code created.
    
    The structure it returns has a "members" field, which contains all
    scanned objects, a "size" field, which gives the total size of all objects,
    and a "back" field, which contains a dictionary with a structure for each
    function that created an object. The dict maps from (file name, line number)
    or None to structure. None is used when there are no functions to go
    back to - i.e. it was this function that started the sequence of calls
    that led to the creation of the object.
    
    Following a member of "back" will give a structure with "filename" and
    "line" fields. In this structure, the "members" field contains the
    objects that were created on this file/line, and the "size" field the size
    of those objects.
    
    The "back" field contains a dictionary with a structure for each function
    that had called this function to make an object.
    
    You can print these using formatting.printsizes(creators.back)
    where creators is the value returned by this function.
    """
    
    try:
        from cpython.utils import objframe
    except ImportError:
        raise Exception, "Couldn't find cpython.utils.objframe - " + \
              "you need a patched copy of Python, and you need to " \
              "build the profiler using that copy."

    # First, collect all objects with the same frame traceback together.
    objects = {}
    for w in wrappers.itervalues():
        traceback = objframe(w.obj)
        val = objects.setdefault(traceback, [])
        val.append(w)
        
    # Now make the structure (a trie).
    return _Creator(wrappers, objects, "<interpreter>", 0)

class _Creator(object):
    """A structure representing a particular series of calls to
    create an object."""
    
    def __init__(self, wrappers, objects, filename, line):
        self.filename = filename
        self.line = line
        self.description = ""
        
        # This should probably use properties and iterators to avoid
        # having to make the whole structure at once.
        self.members = []
        self.size = 0
        for ws in objects.itervalues():
            for w in ws:
                self.members.append(w)
                self.size += w.size
            
        # Again, this is inefficient.
        # The results should be the same, though - if it turns out to be useful
        # I'll rewrite it.
        # Split the objects by last frame
        frames = {}
        noframe = []
        for (fr, val) in objects.iteritems():
            # fr is the frame traceback, val the list of objects associated
            # with it.
            # framedesc is the (filename, line number) of the frame.
            
            # Treat None specially, since it indicates the end of the
            # traceback.
            if fr is None:
                noframe.append(val)
            else:
                framedesc = (fr[0], fr[1])
            
                # Put the frame description's back reference into the dictionary
                frames.setdefault(framedesc, {})
                frames[framedesc][fr[2]] = val
        
        # Now make the back-references
        self.back = {}
        for fr in frames:
            self.back[fr] = _Creator(wrappers, frames[fr], fr[0], fr[1])

        # Put the end-of-frame objects in too.
        nocreator = _Creator.__new__(_Creator)
        nocreator.back = {}
        nocreator.members = []
        nocreator.size = 0
        # Err, there can only be one member of noframe (a big long list,
        # created when objects was). So this exercise is pointless :-)
        for ws in noframe:
            nocreator.members += ws
            nocreator.size += sum([w.size for w in ws])
        
        nocreator.filename = self.filename
        nocreator.line = self.line
        self.back[None] = nocreator
        
        # ...and that appears to be that :-)

    # These are here mostly for formatting.printsizes.
    def __str__(self):
        return self.show()

    def __repr__(self):
        return self.show()        

    def show(self, default = True):
        return self.filename + ":" + str(self.line)
    

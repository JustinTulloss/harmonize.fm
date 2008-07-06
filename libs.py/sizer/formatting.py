"""Functions to print object information."""

import wrapper

unsorted = 0
ascending = 1
descending = -1

def printsizes(wrappers, sorted = descending, threshold = 0, count = None,
               size = lambda w: w.size, show = lambda w: w.show()):
    """Print all objects in wrappers with size above threshold, sorted as
    specified.

    size is optionally a function that takes a wrapper and returns
    its size, by default w.size. 
    
    show is optionally a function that takes a wrapper and returns
    a string representation of it, by default str(w.obj)"""

    vals = wrappers.values()
    if sorted != unsorted:
        vals.sort(lambda w1, w2: sorted * (size(w1) - size(w2)))

    print "Size".rjust(8), "Total".rjust(8), "Object"
    total = 0
    for w in vals[:count]:
        if size(w) >= threshold:
            total += size(w)
            print str(size(w)).rjust(8), str(total).rjust(8), show(w)

def printsizesop(wrappers, sorted = descending, threshold = 0, count = None):
    """Print wrappers from operations.byType or operations.bySize.
    If showobjects is true the objects themselves will be shown instead of
    their wrappers."""
    
    def size(t):
        return t[1]
    
    def show(t):
        return str(t[0])
        
    printsizes(wrappers, sorted, threshold, count, size, show)
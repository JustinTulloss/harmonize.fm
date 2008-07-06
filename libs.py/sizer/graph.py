"""Functions to print pretty pictures of wrappers."""

import pydot
import os
import annotate
import operations

from set import *

# This controls the output format of the graph.
format = {
    "extension": ".ps",
    "command": "ggv",
    "format": "ps",
    "scale": 1.0
}

def makegraph(wrappers, proportional = False, count = None,
              show = lambda w: w.show()):
    """Make a graph showing all objects in the wrappers. If proportional is
    true, objects which take up more space will have bigger nodes.

    Returns the filename of a generated postscript file."""
    
    graph = pydot.Dot()
    edges = set()
    ncount = 0
    ecount = [0]
    if count is None:
        members = wrappers
    else:
        members = operations.top(count, wrappers)
        
    if proportional:
        totalsize = sum([members[w].size for w in members])
    
    # Add in depth-first order, to (hopefully) make the graph look nicer.
    
    # In the case of a cycle, add one last edge to the graph.
    def makeedge(child, parent):
        cname = str(id(child))
        pname = str(id(parent))
        ename = cname + " " + pname
        
        if ename not in edges:
            if id(child.obj) in members and \
                (parent is not None and id(parent.obj) in members):
                edge = pydot.Edge(pname, cname)
                graph.add_edge(edge)
                ecount[0] += 1
            edges.add(ename)
    
    for (child, parent) in annotate.flatten(wrappers, cycle = makeedge):
        name = str(id(child))
        node = pydot.Node(name)
        
        if proportional:
            # Make area proportional to object size
            size = (format["scale"] * 
                    child.size * len(members) / totalsize) ** 0.5
            node.set("height", size)
            node.set("width", size)
            
        node.set("label", show(child))
            
        if id(child.obj) in members:
            graph.add_node(node)
            ncount += 1
        makeedge(child, parent)
    
    print ncount, "nodes,", ecount[0], "edges"
    print "Invoking dot"
    name = os.tempnam() + format["extension"]
    graph.write(name, format = format["format"])
    return name
        
def showgraph(wrappers, proportional = False, count = None, 
              show = lambda w: w.show()):
    """Display a graph showing all objects in the wrappers.

    If proportional is true, objects which take up more space will have bigger
    nodes."""

    print "Make graph"
    graph = makegraph(wrappers, proportional, count, show)
    print "Show graph", graph
    os.system(format["command"] + " " + graph)
    

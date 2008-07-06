"""Code to count various built-in objects. It isn't comprehensive yet."""

pointersize = 4

import warnings
import gc
import itertools

from sizer import sizes

class Missing(Warning):
    pass

class NotYetImplemented(Warning):
    pass

try:
    from sizer.cpython.utils import _getframes
except ImportError:
    warnings.warn(
        "Using sys._getframe because cpython.utils._getframes was not found",
        Missing)
    import sys
    def _getframes():
        return [sys._getframe()]

from types import *
from sizer.wrapper import *

def getname(t):
    """Produce a name for a type."""
    try:
        mod = t.__module__
    except AttributeError:
        mod = "unknown"

    try:
        name = t.__name__
    except AttributeError:
        name = "unknown"
        
    return mod + "." + name

def roots():
    """Return a list of roots for scanning."""
    return _getframes()

class BaseObject(ObjectWrapper):
        pass

class SimpleObject(BaseObject):
    def show(self, default = True):
        next = super(SimpleObject, self).show(False)
        res = str(self.obj) + " " + next
        return res.strip()
        
class GCObject(BaseObject):
    """Wraps an object, trying to find its children using the GC."""
    def __init__(self, obj):       
        super(GCObject, self).__init__(obj)
        self.addchildren(gc.get_referents(obj), itertools.repeat(0))
        
class Object(GCObject):
    """Wraps object."""
    def __init__(self, obj):
        super(Object, self).__init__(obj)
        try:
            self.size += type(obj).__basicsize__
        except AttributeError:
            warnings.warn("Size of %s not known - can't even guess" %
                          getname(type(obj)), Missing)
            
UnknownObject = Object

class SimpleGCObject(SimpleObject, GCObject):
    """A GCed object which can safely be printed."""
    pass

class ListObject(BaseObject):
    """Wraps a list."""
    warnings.warn("ListObject should use gettime", NotYetImplemented)
    
    def __init__(self, obj):
        super(ListObject, self).__init__(obj)
        self.size += pointersize * len(obj)       
        self.addchildren(obj, itertools.repeat(0))

    def show(self, default = True):
        next = super(ListObject, self).show(False)
        
        try:
            if len(self.obj) <= 3:
                res = "[" + \
                    ", ".join([self.wrappers[id(obj)].show() for obj in self.obj]) + \
                    "] " + next
                return res.strip()
            else:
                return super(ListObject, self).show()
        except:
            return super(ListObject, self).show()

class TupleObject(BaseObject):
    """Wraps a tuple."""
    def __init__(self, obj):
        super(TupleObject, self).__init__(obj)
        self.size += type(obj).__itemsize__ * len(obj)
        self.addchildren(obj, itertools.repeat(0))
        
    def show(self, default = True):
        next = super(TupleObject, self).show(False)
        
        try:
            if len(self.obj) == 1:
                res = "(" + self.wrappers[id(self.obj[0])].show() + ",) " + next
                return res.strip()
            elif len(self.obj) <= 3:
                res = "(" + \
                    ", ".join([self.wrappers[id(obj)].show() for obj in self.obj]) + \
                    ") " + next
                return res.strip()
            else:
                return super(TupleObject, self).show()
        except:
            return super(TupleObject, self).show()

class StringObject(BaseObject):
    """Wraps a string."""
    def __init__(self, obj):
        super(StringObject, self).__init__(obj)
        self.size += type(obj).__itemsize__ * len(obj)
        
    def show(self, default = True):
        next = super(StringObject, self).show(False)
        
        if len(self.obj) <= 20:
            return (repr(self.obj) + " " + next).strip()
        else:
            return super(StringObject, self).show()

try:
    from sizer.cpython.utils import unicodedefenc
except ImportError:
    warnings.warn("Not counting unicode default encodings because " + \
                "cpython.utils.unicodedefenc was not found", Missing)
    def unicodedefenc(obj):
        return None
    
unicodesize = 2
class UnicodeObject(BaseObject):
    """Wraps a unicode string."""
    def __init__(self, obj):
        super(UnicodeObject, self).__init__(obj)
        self.size += unicodesize * len(obj)
        
        enc = unicodedefenc(unicode(obj))
        if enc is not None:
            self.addchild(enc, 0)
        
    def show(self, default = True):
        next = super(UnicodeObject, self).show(False)
        
        if len(self.obj) <= 20:
            return (repr(self.obj) + " " + next).strip()
        else:
            return super(UnicodeObject, self).show()

_havegettime = hasattr({}, "gettime")
if not _havegettime:
    warnings.warn(
        "Unpatched CPython found so annotate.groupby will be inaccurate",
        Missing)

dictminsize = 8
class DictObject(BaseObject):
    """Wraps a dictionary."""
    
    def __init__(self, obj):
        super(DictObject, self).__init__(obj)
        if len(obj) > dictminsize:
                self.size += 3 * len(obj) * pointersize

        keys = []
        values = []
        if _havegettime:
            # Don't count the time information in the smalltable.
            self.size -= 2 * dictminsize * pointersize
            
            for k in obj:
                (value, keytime, valuetime) = obj.gettime(k)
                self.addchild(k, keytime)
                self.addchild(value, valuetime)
                keys.append(k)
                values.append(value)
        else:
            for k in obj:
                self.addchild(k, 0)
                self.addchild(obj[k], 0)
                keys.append(k)
                values.append(obj[k])
                    
        self.keys = keys
        self.values = values
        
    def liftrefs(self, wrappers):
        super(DictObject, self).liftrefs(wrappers)
        
        for (i, k) in enumerate(self.keys):
            try:
                self.keys[i] = wrappers[id(k)]
            except KeyError:
                self.keys[i] = wrappers[id(None)]
                
        for (i, v) in enumerate(self.values):
            try:
                self.values[i] = wrappers[id(v)]
            except KeyError:
                self.values[i] = wrappers[id(None)]
                
        self.keys = ignoretuple(self.keys)
        self.values = ignoretuple(self.values)
        
    def droprefs(self, wrappers):
        super(DictObject, self).droprefs(wrappers)
        
        self.keys = [ k.obj for k in self.keys ]
        self.values = [ v.obj for v in self.values ]
        
    def copy(self):
        ret = super(DictObject, self).copy()
        ret.keys = self.keys[:]
        ret.values = self.values[:]
        return ret
    
    def cut(self, wrappers):
        super(DictObject, self).cut(wrappers)
        
        self.keys = [ k for k in self.keys if id(k.obj) in wrappers ]
        self.values = [ v for v in self.values if id(v.obj) in wrappers ]
        
    def show(self, default = True):
        next = super(DictObject, self).show(False)
        
        try:
            if len(self.keys) == 0:
                return ("{} " + next).strip()
            elif len(self.keys) <= 3:
                return "".join(
                    ["{", self.keys[0].show() + ": " + self.values[0].show() ] + \
                    [", " + k.show() + ": " + v.show() for (k, v) in 
                     zip(self.keys[1:], self.values[1:])] + \
                    ["} ", next]).strip()
            else:
                return super(DictObject, self).show()
        except:
            return super(DictObject, self).show()

setminsize = 8
class SetObject(BaseObject):
    """Wraps a set or frozenset."""
    
    def __init__(self, obj):
        super(SetObject, self).__init__(obj)
        if len(obj) > setminsize:
            self.size += 2 * len(obj) * pointersize
        self.addchildren(obj, itertools.repeat(0))

    def show(self, default = True):
        next = super(SetObject, self).show(False)
        name = type(self.obj).__name__
        
        try:
            if len(self.obj) <= 3:
                res = name + "([" + \
                    ", ".join([self.wrappers[id(obj)].show() for obj in self.obj]) + \
                    "]) " + next
                return res.strip()
            else:
                return super(SetObject, self).show()
        except:
            return super(SetObject, self).show()

class FrameObject(GCObject):
    """Wraps a frame. Used to set size accurately."""
    def __init__(self, obj):
        super(FrameObject, self).__init__(obj)
        if obj.f_code is not None:
            self.size += obj.f_code.co_stacksize * pointersize

class SliceObject(GCObject):
    """Wraps a slice object."""
    def __init__(self, obj):
        super(SliceObject, self).__init__(obj)
        self.addchild(obj.start, 0)
        self.addchild(obj.stop, 0)
        self.addchild(obj.step, 0)

class InstanceObject(GCObject):
    """Wraps an old-style instance."""
    def __init__(self, obj):
        super(InstanceObject, self).__init__(obj)
        self.type = obj.__class__
    
    def show(self, default = True):
        next = super(InstanceObject, self).show(False)
        res = "instance of " + self.wrappers[id(self.obj.__class__)].show(False) + " " + next
        return res.strip()
    
class ModuleObject(GCObject):
    """Wraps a module."""
    def show(self, default = True):
        next = super(ModuleObject, self).show(False)
        res = "module " + self.obj.__name__ + " " + next
        return res.strip()

try:
    from sizer.cpython.utils import dictitersize
    
    class DictIterObject(GCObject):
        """Wraps a dictionary iterator."""

        def __init__(self, obj):
            super(DictIterObject, self).__init__(obj)
            children = dictitersize(obj)

            for c in children:
                if c is not None:
                    self.addchild(c, 0)
                    
except ImportError:
    warnings.warn("Not counting dictionary iterators because " + \
                "cpython.utils.dictitersize was not found", Missing)
    DictIterObject = GCObject
    
try:
    from sizer.cpython.utils import longsize
    
    class LongObject(BaseObject):
        """Wraps a long."""
        
        def __init__(self, obj):
            super(LongObject, self).__init__(obj)
            self.size += longsize(obj)

except ImportError:
    warnings.warn("Not counting longs properly because " + \
                "cpython.utils.longsize was not found", Missing)
    LongObject = BaseObject

class CodeObject(BaseObject):
        """Wraps a code object."""

        def __init__(self, obj):
                super(CodeObject, self).__init__(obj)
                self.addchild(obj.co_code, 0)
                self.addchild(obj.co_consts, 0)
                self.addchild(obj.co_names, 0)
                self.addchild(obj.co_varnames, 0)
                self.addchild(obj.co_freevars, 0)
                self.addchild(obj.co_cellvars, 0)
                self.addchild(obj.co_filename, 0)
                self.addchild(obj.co_name, 0)
                self.addchild(obj.co_lnotab, 0)
      
# Default thing to use
sizes.type[object] = Object

# See doc/types.html for details.
sizes.type[BooleanType] = SimpleObject
sizes.type[BufferType] = GCObject
sizes.type["__builtin__.cell"] = GCObject
sizes.type[ClassType] = SimpleGCObject
sizes.type[InstanceType] = InstanceObject
sizes.type[MethodType] = SimpleGCObject
sizes.type[ComplexType] = SimpleObject
sizes.type[DictProxyType] = GCObject
sizes.type["__builtin__.method-wrapper"] = GCObject
sizes.type[property] = GCObject
sizes.type[DictType] = DictObject
sizes.type["__builtin__.dictionary-keyiterator"] = DictIterObject
sizes.type["__builtin__.dictionary-valueiterator"] = DictIterObject
sizes.type["__builtin__.dictionary-itemiterator"] = DictIterObject
sizes.type[enumerate] = SimpleGCObject
sizes.type[FloatType] = SimpleObject
sizes.type[FrameType] = FrameObject
sizes.type[FunctionType] = SimpleGCObject
sizes.type[classmethod] = SimpleGCObject
sizes.type[staticmethod] = SimpleGCObject
sizes.type[GeneratorType] = SimpleGCObject
sizes.type[IntType] = SimpleObject
sizes.type["__builtin__.iterator"] = GCObject
sizes.type["__builtin__.callable-iterator"] = GCObject
sizes.type[ListType] = ListObject
sizes.type["__builtin__.listiterator"] = GCObject
sizes.type["__builtin__.listreverseiterator"] = GCObject
sizes.type[long] = LongObject
sizes.type[ModuleType] = ModuleObject
sizes.type[NoneType] = SimpleObject
sizes.type[NotImplementedType] = SimpleObject
sizes.type[xrange] = SimpleObject
sizes.type[EllipsisType] = SimpleObject
sizes.type[slice] = SliceObject
sizes.type[basestring] = BaseObject
sizes.type[str] = StringObject
sizes.type[tuple] = TupleObject
sizes.type["__builtin__.tupleiterator"] = GCObject
sizes.type[super] = GCObject
sizes.type[unicode] = UnicodeObject
sizes.type["__builtin__.weakref"] = GCObject
sizes.type["__builtin__.weakproxy"] = GCObject
sizes.type["__builtin__.weakcallableproxy"] = GCObject
sizes.type[CodeType] = GCObject
sizes.type["__builtin__.symtable entry"] = GCObject
sizes.type[TracebackType] = GCObject
sizes.type[type] = GCObject

# Add more types for Python >= 2.4
import sys
if sys.version_info[0] == 2 and sys.version_info[1] >= 4:
    sizes.type[set] = SetObject
    sizes.type[frozenset] = SetObject

# Try to get code for more types.
try:
    import sizer.cpython.crules
except ImportError:
    warnings.warn("sizer.cpython.crules pyrex module not found")


#
# Wrappers for objects which can't be counted easily using plain python code.
#

import sizer.wrapper, sizer.sizes

cdef extern from "object.h":
    ctypedef struct _typeobject:
        int tp_basicsize
        int tp_itemsize

cdef extern from "fileobject.h":
    ctypedef class __builtin__.file[object PyFileObject]:
        cdef object f_name
        cdef object f_mode
        cdef object f_encoding
        cdef char * f_buf
        cdef char * f_bufend
        cdef _typeobject * ob_type

class FileWrapper(sizer.wrapper.ObjectWrapper):
    def __init__(self, file obj not None):
        sizer.wrapper.ObjectWrapper.__init__(self, obj)
        self.addchild(obj.f_name, 0)
        self.addchild(obj.f_mode, 0)
        self.addchild(obj.f_encoding, 0)
        diff = obj.f_bufend - obj.f_buf
        self.size = self.size + diff + obj.ob_type.tp_basicsize
        
sizer.sizes.type[file] = FileWrapper

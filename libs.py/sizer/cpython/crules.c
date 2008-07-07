/* Generated by Pyrex 0.9.8.4 on Sat Jul  5 19:23:57 2008 */

#define PY_SSIZE_T_CLEAN
#include "Python.h"
#include "structmember.h"
#ifndef PY_LONG_LONG
  #define PY_LONG_LONG LONG_LONG
#endif
#if PY_VERSION_HEX < 0x02050000
  typedef int Py_ssize_t;
  #define PY_SSIZE_T_MAX INT_MAX
  #define PY_SSIZE_T_MIN INT_MIN
  #define PyInt_FromSsize_t(z) PyInt_FromLong(z)
  #define PyInt_AsSsize_t(o)	PyInt_AsLong(o)
#endif
#ifndef WIN32
  #ifndef __stdcall
    #define __stdcall
  #endif
  #ifndef __cdecl
    #define __cdecl
  #endif
#endif
#ifdef __cplusplus
#define __PYX_EXTERN_C extern "C"
#else
#define __PYX_EXTERN_C extern
#endif
#include <math.h>
#include "object.h"
#include "fileobject.h"


typedef struct {PyObject **p; int i; char *s; long n;} __Pyx_StringTabEntry; /*proto*/

static PyObject *__pyx_m;
static PyObject *__pyx_b;
static int __pyx_lineno;
static char *__pyx_filename;
static char **__pyx_f;

static int __Pyx_ArgTypeTest(PyObject *obj, PyTypeObject *type, int none_allowed, char *name); /*proto*/

static PyObject *__Pyx_GetName(PyObject *dict, PyObject *name); /*proto*/

static int __Pyx_InitStrings(__Pyx_StringTabEntry *t); /*proto*/

static PyTypeObject *__Pyx_ImportType(char *module_name, char *class_name, long size);  /*proto*/

static PyObject *__Pyx_ImportModule(char *name); /*proto*/

static PyObject *__Pyx_Import(PyObject *name, PyObject *from_list); /*proto*/

static PyObject *__Pyx_CreateClass(PyObject *bases, PyObject *dict, PyObject *name, char *modname); /*proto*/

static void __Pyx_AddTraceback(char *funcname); /*proto*/

/* Declarations from src.cpython.crules */


/* Declarations from implementation of src.cpython.crules */

static PyTypeObject *__pyx_ptype_3src_7cpython_6crules_file = 0;

static char __pyx_k1[] = "sizer";
static char __pyx_k2[] = "wrapper";
static char __pyx_k3[] = "ObjectWrapper";
static char __pyx_k4[] = "__init__";
static char __pyx_k5[] = "addchild";
static char __pyx_k6[] = "size";
static char __pyx_k7[] = "sizer.wrapper";
static char __pyx_k8[] = "sizer.sizes";
static char __pyx_k9[] = "FileWrapper";
static char __pyx_k10[] = "sizes";
static char __pyx_k11[] = "type";

static PyObject *__pyx_n_FileWrapper;
static PyObject *__pyx_n_ObjectWrapper;
static PyObject *__pyx_n___init__;
static PyObject *__pyx_n_addchild;
static PyObject *__pyx_n_size;
static PyObject *__pyx_n_sizer;
static PyObject *__pyx_n_sizes;
static PyObject *__pyx_n_type;
static PyObject *__pyx_n_wrapper;

static PyObject *__pyx_k7p;
static PyObject *__pyx_k8p;

static __Pyx_StringTabEntry __pyx_string_tab[] = {
  {&__pyx_n_FileWrapper, 1, __pyx_k9, sizeof(__pyx_k9)},
  {&__pyx_n_ObjectWrapper, 1, __pyx_k3, sizeof(__pyx_k3)},
  {&__pyx_n___init__, 1, __pyx_k4, sizeof(__pyx_k4)},
  {&__pyx_n_addchild, 1, __pyx_k5, sizeof(__pyx_k5)},
  {&__pyx_n_size, 1, __pyx_k6, sizeof(__pyx_k6)},
  {&__pyx_n_sizer, 1, __pyx_k1, sizeof(__pyx_k1)},
  {&__pyx_n_sizes, 1, __pyx_k10, sizeof(__pyx_k10)},
  {&__pyx_n_type, 1, __pyx_k11, sizeof(__pyx_k11)},
  {&__pyx_n_wrapper, 1, __pyx_k2, sizeof(__pyx_k2)},
  {&__pyx_k7p, 0, __pyx_k7, sizeof(__pyx_k7)},
  {&__pyx_k8p, 0, __pyx_k8, sizeof(__pyx_k8)},
  {0, 0, 0, 0}
};



/* Implementation of src.cpython.crules */

static PyObject *__pyx_f_3src_7cpython_6crules_11FileWrapper___init__(PyObject *__pyx_self, PyObject *__pyx_args, PyObject *__pyx_kwds); /*proto*/
static PyMethodDef __pyx_mdef_3src_7cpython_6crules_11FileWrapper___init__ = {"__init__", (PyCFunction)__pyx_f_3src_7cpython_6crules_11FileWrapper___init__, METH_VARARGS|METH_KEYWORDS, 0};
static PyObject *__pyx_f_3src_7cpython_6crules_11FileWrapper___init__(PyObject *__pyx_self, PyObject *__pyx_args, PyObject *__pyx_kwds) {
  PyObject *__pyx_v_self = 0;
  PyFileObject *__pyx_v_obj = 0;
  PyObject *__pyx_v_diff;
  PyObject *__pyx_r;
  PyObject *__pyx_1 = 0;
  PyObject *__pyx_2 = 0;
  PyObject *__pyx_3 = 0;
  static char *__pyx_argnames[] = {"self","obj",0};
  if (!PyArg_ParseTupleAndKeywords(__pyx_args, __pyx_kwds, "OO", __pyx_argnames, &__pyx_v_self, &__pyx_v_obj)) return 0;
  Py_INCREF(__pyx_v_self);
  Py_INCREF(__pyx_v_obj);
  __pyx_v_diff = Py_None; Py_INCREF(Py_None);
  if (!__Pyx_ArgTypeTest(((PyObject *)__pyx_v_obj), __pyx_ptype_3src_7cpython_6crules_file, 0, "obj")) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 22; goto __pyx_L1;}

  /* "/mnt/data/Users/justin/devel/sizer-0.1.1/src/cpython/crules.pyx":23 */
  __pyx_1 = __Pyx_GetName(__pyx_m, __pyx_n_sizer); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 23; goto __pyx_L1;}
  __pyx_2 = PyObject_GetAttr(__pyx_1, __pyx_n_wrapper); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 23; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  __pyx_1 = PyObject_GetAttr(__pyx_2, __pyx_n_ObjectWrapper); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 23; goto __pyx_L1;}
  Py_DECREF(__pyx_2); __pyx_2 = 0;
  __pyx_2 = PyObject_GetAttr(__pyx_1, __pyx_n___init__); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 23; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  __pyx_1 = PyTuple_New(2); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 23; goto __pyx_L1;}
  Py_INCREF(__pyx_v_self);
  PyTuple_SET_ITEM(__pyx_1, 0, __pyx_v_self);
  Py_INCREF(((PyObject *)__pyx_v_obj));
  PyTuple_SET_ITEM(__pyx_1, 1, ((PyObject *)__pyx_v_obj));
  __pyx_3 = PyObject_CallObject(__pyx_2, __pyx_1); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 23; goto __pyx_L1;}
  Py_DECREF(__pyx_2); __pyx_2 = 0;
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  Py_DECREF(__pyx_3); __pyx_3 = 0;

  /* "/mnt/data/Users/justin/devel/sizer-0.1.1/src/cpython/crules.pyx":24 */
  __pyx_2 = PyObject_GetAttr(__pyx_v_self, __pyx_n_addchild); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 24; goto __pyx_L1;}
  __pyx_1 = PyInt_FromLong(0); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 24; goto __pyx_L1;}
  __pyx_3 = PyTuple_New(2); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 24; goto __pyx_L1;}
  Py_INCREF(__pyx_v_obj->f_name);
  PyTuple_SET_ITEM(__pyx_3, 0, __pyx_v_obj->f_name);
  PyTuple_SET_ITEM(__pyx_3, 1, __pyx_1);
  __pyx_1 = 0;
  __pyx_1 = PyObject_CallObject(__pyx_2, __pyx_3); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 24; goto __pyx_L1;}
  Py_DECREF(__pyx_2); __pyx_2 = 0;
  Py_DECREF(__pyx_3); __pyx_3 = 0;
  Py_DECREF(__pyx_1); __pyx_1 = 0;

  /* "/mnt/data/Users/justin/devel/sizer-0.1.1/src/cpython/crules.pyx":25 */
  __pyx_2 = PyObject_GetAttr(__pyx_v_self, __pyx_n_addchild); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 25; goto __pyx_L1;}
  __pyx_3 = PyInt_FromLong(0); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 25; goto __pyx_L1;}
  __pyx_1 = PyTuple_New(2); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 25; goto __pyx_L1;}
  Py_INCREF(__pyx_v_obj->f_mode);
  PyTuple_SET_ITEM(__pyx_1, 0, __pyx_v_obj->f_mode);
  PyTuple_SET_ITEM(__pyx_1, 1, __pyx_3);
  __pyx_3 = 0;
  __pyx_3 = PyObject_CallObject(__pyx_2, __pyx_1); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 25; goto __pyx_L1;}
  Py_DECREF(__pyx_2); __pyx_2 = 0;
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  Py_DECREF(__pyx_3); __pyx_3 = 0;

  /* "/mnt/data/Users/justin/devel/sizer-0.1.1/src/cpython/crules.pyx":26 */
  __pyx_2 = PyObject_GetAttr(__pyx_v_self, __pyx_n_addchild); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 26; goto __pyx_L1;}
  __pyx_1 = PyInt_FromLong(0); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 26; goto __pyx_L1;}
  __pyx_3 = PyTuple_New(2); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 26; goto __pyx_L1;}
  Py_INCREF(__pyx_v_obj->f_encoding);
  PyTuple_SET_ITEM(__pyx_3, 0, __pyx_v_obj->f_encoding);
  PyTuple_SET_ITEM(__pyx_3, 1, __pyx_1);
  __pyx_1 = 0;
  __pyx_1 = PyObject_CallObject(__pyx_2, __pyx_3); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 26; goto __pyx_L1;}
  Py_DECREF(__pyx_2); __pyx_2 = 0;
  Py_DECREF(__pyx_3); __pyx_3 = 0;
  Py_DECREF(__pyx_1); __pyx_1 = 0;

  /* "/mnt/data/Users/justin/devel/sizer-0.1.1/src/cpython/crules.pyx":27 */
  __pyx_2 = PyInt_FromLong((__pyx_v_obj->f_bufend - __pyx_v_obj->f_buf)); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 27; goto __pyx_L1;}
  Py_DECREF(__pyx_v_diff);
  __pyx_v_diff = __pyx_2;
  __pyx_2 = 0;

  /* "/mnt/data/Users/justin/devel/sizer-0.1.1/src/cpython/crules.pyx":28 */
  __pyx_3 = PyObject_GetAttr(__pyx_v_self, __pyx_n_size); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 28; goto __pyx_L1;}
  __pyx_1 = PyNumber_Add(__pyx_3, __pyx_v_diff); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 28; goto __pyx_L1;}
  Py_DECREF(__pyx_3); __pyx_3 = 0;
  __pyx_2 = PyInt_FromLong(__pyx_v_obj->ob_type->tp_basicsize); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 28; goto __pyx_L1;}
  __pyx_3 = PyNumber_Add(__pyx_1, __pyx_2); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 28; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  Py_DECREF(__pyx_2); __pyx_2 = 0;
  if (PyObject_SetAttr(__pyx_v_self, __pyx_n_size, __pyx_3) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 28; goto __pyx_L1;}
  Py_DECREF(__pyx_3); __pyx_3 = 0;

  __pyx_r = Py_None; Py_INCREF(Py_None);
  goto __pyx_L0;
  __pyx_L1:;
  Py_XDECREF(__pyx_1);
  Py_XDECREF(__pyx_2);
  Py_XDECREF(__pyx_3);
  __Pyx_AddTraceback("src.cpython.crules.FileWrapper.__init__");
  __pyx_r = 0;
  __pyx_L0:;
  Py_DECREF(__pyx_v_diff);
  Py_DECREF(__pyx_v_self);
  Py_DECREF(__pyx_v_obj);
  return __pyx_r;
}

static struct PyMethodDef __pyx_methods[] = {
  {0, 0, 0, 0}
};

static void __pyx_init_filenames(void); /*proto*/

PyMODINIT_FUNC initcrules(void); /*proto*/
PyMODINIT_FUNC initcrules(void) {
  PyObject *__pyx_1 = 0;
  PyObject *__pyx_2 = 0;
  PyObject *__pyx_3 = 0;
  PyObject *__pyx_4 = 0;
  __pyx_init_filenames();
  __pyx_m = Py_InitModule4("crules", __pyx_methods, 0, 0, PYTHON_API_VERSION);
  if (!__pyx_m) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 5; goto __pyx_L1;};
  Py_INCREF(__pyx_m);
  __pyx_b = PyImport_AddModule("__builtin__");
  if (!__pyx_b) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 5; goto __pyx_L1;};
  if (PyObject_SetAttrString(__pyx_m, "__builtins__", __pyx_b) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 5; goto __pyx_L1;};
  if (__Pyx_InitStrings(__pyx_string_tab) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 5; goto __pyx_L1;};
  __pyx_ptype_3src_7cpython_6crules_file = __Pyx_ImportType("__builtin__", "file", sizeof(PyFileObject)); if (!__pyx_ptype_3src_7cpython_6crules_file) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 13; goto __pyx_L1;}

  /* "/mnt/data/Users/justin/devel/sizer-0.1.1/src/cpython/crules.pyx":5 */
  __pyx_1 = __Pyx_Import(__pyx_k7p, 0); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 5; goto __pyx_L1;}
  if (PyObject_SetAttr(__pyx_m, __pyx_n_sizer, __pyx_1) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 5; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;

  /* "/mnt/data/Users/justin/devel/sizer-0.1.1/src/cpython/crules.pyx":5 */
  __pyx_1 = __Pyx_Import(__pyx_k8p, 0); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 5; goto __pyx_L1;}
  if (PyObject_SetAttr(__pyx_m, __pyx_n_sizer, __pyx_1) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 5; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;

  /* "/mnt/data/Users/justin/devel/sizer-0.1.1/src/cpython/crules.pyx":21 */
  __pyx_1 = PyDict_New(); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 21; goto __pyx_L1;}
  __pyx_2 = __Pyx_GetName(__pyx_m, __pyx_n_sizer); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 21; goto __pyx_L1;}
  __pyx_3 = PyObject_GetAttr(__pyx_2, __pyx_n_wrapper); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 21; goto __pyx_L1;}
  Py_DECREF(__pyx_2); __pyx_2 = 0;
  __pyx_2 = PyObject_GetAttr(__pyx_3, __pyx_n_ObjectWrapper); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 21; goto __pyx_L1;}
  Py_DECREF(__pyx_3); __pyx_3 = 0;
  __pyx_3 = PyTuple_New(1); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 21; goto __pyx_L1;}
  PyTuple_SET_ITEM(__pyx_3, 0, __pyx_2);
  __pyx_2 = 0;
  __pyx_2 = __Pyx_CreateClass(__pyx_3, __pyx_1, __pyx_n_FileWrapper, "src.cpython.crules"); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 21; goto __pyx_L1;}
  Py_DECREF(__pyx_3); __pyx_3 = 0;
  __pyx_3 = PyCFunction_New(&__pyx_mdef_3src_7cpython_6crules_11FileWrapper___init__, 0); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 22; goto __pyx_L1;}
  __pyx_4 = PyMethod_New(__pyx_3, 0, __pyx_2); if (!__pyx_4) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 22; goto __pyx_L1;}
  Py_DECREF(__pyx_3); __pyx_3 = 0;
  if (PyObject_SetAttr(__pyx_2, __pyx_n___init__, __pyx_4) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 22; goto __pyx_L1;}
  Py_DECREF(__pyx_4); __pyx_4 = 0;
  if (PyObject_SetAttr(__pyx_m, __pyx_n_FileWrapper, __pyx_2) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 21; goto __pyx_L1;}
  Py_DECREF(__pyx_2); __pyx_2 = 0;
  Py_DECREF(__pyx_1); __pyx_1 = 0;

  /* "/mnt/data/Users/justin/devel/sizer-0.1.1/src/cpython/crules.pyx":30 */
  __pyx_3 = __Pyx_GetName(__pyx_m, __pyx_n_FileWrapper); if (!__pyx_3) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 30; goto __pyx_L1;}
  __pyx_4 = __Pyx_GetName(__pyx_m, __pyx_n_sizer); if (!__pyx_4) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 30; goto __pyx_L1;}
  __pyx_2 = PyObject_GetAttr(__pyx_4, __pyx_n_sizes); if (!__pyx_2) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 30; goto __pyx_L1;}
  Py_DECREF(__pyx_4); __pyx_4 = 0;
  __pyx_1 = PyObject_GetAttr(__pyx_2, __pyx_n_type); if (!__pyx_1) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 30; goto __pyx_L1;}
  Py_DECREF(__pyx_2); __pyx_2 = 0;
  if (PyObject_SetItem(__pyx_1, ((PyObject *)__pyx_ptype_3src_7cpython_6crules_file), __pyx_3) < 0) {__pyx_filename = __pyx_f[0]; __pyx_lineno = 30; goto __pyx_L1;}
  Py_DECREF(__pyx_1); __pyx_1 = 0;
  Py_DECREF(__pyx_3); __pyx_3 = 0;
  return;
  __pyx_L1:;
  Py_XDECREF(__pyx_1);
  Py_XDECREF(__pyx_2);
  Py_XDECREF(__pyx_3);
  Py_XDECREF(__pyx_4);
  __Pyx_AddTraceback("src.cpython.crules");
}

static char *__pyx_filenames[] = {
  "crules.pyx",
};

/* Runtime support code */

static void __pyx_init_filenames(void) {
  __pyx_f = __pyx_filenames;
}

static int __Pyx_ArgTypeTest(PyObject *obj, PyTypeObject *type, int none_allowed, char *name) {
    if (!type) {
        PyErr_Format(PyExc_SystemError, "Missing type object");
        return 0;
    }
    if ((none_allowed && obj == Py_None) || PyObject_TypeCheck(obj, type))
        return 1;
    PyErr_Format(PyExc_TypeError,
        "Argument '%s' has incorrect type (expected %s, got %s)",
        name, type->tp_name, obj->ob_type->tp_name);
    return 0;
}

static PyObject *__Pyx_GetName(PyObject *dict, PyObject *name) {
    PyObject *result;
    result = PyObject_GetAttr(dict, name);
    if (!result)
        PyErr_SetObject(PyExc_NameError, name);
    return result;
}

static int __Pyx_InitStrings(__Pyx_StringTabEntry *t) {
    while (t->p) {
        *t->p = PyString_FromStringAndSize(t->s, t->n - 1);
        if (!*t->p)
            return -1;
        if (t->i)
            PyString_InternInPlace(t->p);
        ++t;
    }
    return 0;
}

#ifndef __PYX_HAVE_RT_ImportType
#define __PYX_HAVE_RT_ImportType
static PyTypeObject *__Pyx_ImportType(char *module_name, char *class_name, 
    long size) 
{
    PyObject *py_module = 0;
    PyObject *result = 0;
    
    py_module = __Pyx_ImportModule(module_name);
    if (!py_module)
        goto bad;
    result = PyObject_GetAttrString(py_module, class_name);
    if (!result)
        goto bad;
    if (!PyType_Check(result)) {
        PyErr_Format(PyExc_TypeError, 
            "%s.%s is not a type object",
            module_name, class_name);
        goto bad;
    }
    if (((PyTypeObject *)result)->tp_basicsize != size) {
        PyErr_Format(PyExc_ValueError, 
            "%s.%s does not appear to be the correct type object",
            module_name, class_name);
        goto bad;
    }
    return (PyTypeObject *)result;
bad:
    Py_XDECREF(result);
    return 0;
}
#endif

#ifndef __PYX_HAVE_RT_ImportModule
#define __PYX_HAVE_RT_ImportModule
static PyObject *__Pyx_ImportModule(char *name) {
    PyObject *py_name = 0;
    
    py_name = PyString_FromString(name);
    if (!py_name)
        goto bad;
    return PyImport_Import(py_name);
bad:
    Py_XDECREF(py_name);
    return 0;
}
#endif

static PyObject *__Pyx_Import(PyObject *name, PyObject *from_list) {
    PyObject *__import__ = 0;
    PyObject *empty_list = 0;
    PyObject *module = 0;
    PyObject *global_dict = 0;
    PyObject *empty_dict = 0;
    PyObject *list;
    __import__ = PyObject_GetAttrString(__pyx_b, "__import__");
    if (!__import__)
        goto bad;
    if (from_list)
        list = from_list;
    else {
        empty_list = PyList_New(0);
        if (!empty_list)
            goto bad;
        list = empty_list;
    }
    global_dict = PyModule_GetDict(__pyx_m);
    if (!global_dict)
        goto bad;
    empty_dict = PyDict_New();
    if (!empty_dict)
        goto bad;
    module = PyObject_CallFunction(__import__, "OOOO",
        name, global_dict, empty_dict, list);
bad:
    Py_XDECREF(empty_list);
    Py_XDECREF(__import__);
    Py_XDECREF(empty_dict);
    return module;
}

static PyObject *__Pyx_CreateClass(
    PyObject *bases, PyObject *dict, PyObject *name, char *modname)
{
    PyObject *py_modname;
    PyObject *result = 0;
    
    py_modname = PyString_FromString(modname);
    if (!py_modname)
        goto bad;
    if (PyDict_SetItemString(dict, "__module__", py_modname) < 0)
        goto bad;
    result = PyClass_New(bases, dict, name);
bad:
    Py_XDECREF(py_modname);
    return result;
}

#include "compile.h"
#include "frameobject.h"
#include "traceback.h"

static void __Pyx_AddTraceback(char *funcname) {
    PyObject *py_srcfile = 0;
    PyObject *py_funcname = 0;
    PyObject *py_globals = 0;
    PyObject *empty_tuple = 0;
    PyObject *empty_string = 0;
    PyCodeObject *py_code = 0;
    PyFrameObject *py_frame = 0;
    
    py_srcfile = PyString_FromString(__pyx_filename);
    if (!py_srcfile) goto bad;
    py_funcname = PyString_FromString(funcname);
    if (!py_funcname) goto bad;
    py_globals = PyModule_GetDict(__pyx_m);
    if (!py_globals) goto bad;
    empty_tuple = PyTuple_New(0);
    if (!empty_tuple) goto bad;
    empty_string = PyString_FromString("");
    if (!empty_string) goto bad;
    py_code = PyCode_New(
        0,            /*int argcount,*/
        0,            /*int nlocals,*/
        0,            /*int stacksize,*/
        0,            /*int flags,*/
        empty_string, /*PyObject *code,*/
        empty_tuple,  /*PyObject *consts,*/
        empty_tuple,  /*PyObject *names,*/
        empty_tuple,  /*PyObject *varnames,*/
        empty_tuple,  /*PyObject *freevars,*/
        empty_tuple,  /*PyObject *cellvars,*/
        py_srcfile,   /*PyObject *filename,*/
        py_funcname,  /*PyObject *name,*/
        __pyx_lineno,   /*int firstlineno,*/
        empty_string  /*PyObject *lnotab*/
    );
    if (!py_code) goto bad;
    py_frame = PyFrame_New(
        PyThreadState_Get(), /*PyThreadState *tstate,*/
        py_code,             /*PyCodeObject *code,*/
        py_globals,          /*PyObject *globals,*/
        0                    /*PyObject *locals*/
    );
    if (!py_frame) goto bad;
    py_frame->f_lineno = __pyx_lineno;
    PyTraceBack_Here(py_frame);
bad:
    Py_XDECREF(py_srcfile);
    Py_XDECREF(py_funcname);
    Py_XDECREF(empty_tuple);
    Py_XDECREF(empty_string);
    Py_XDECREF(py_code);
    Py_XDECREF(py_frame);
}
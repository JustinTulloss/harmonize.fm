#include "Python.h"
#include "longintrepr.h"

// Get a list of all top-level frames.
static PyObject * _getframes(PyObject * self, PyObject * args)
{
	PyObject * frames;

	PyThreadState * current;

	if (!PyArg_ParseTuple(args, ""))
		return NULL;

	// Try to allocate a list to store the frames.
	frames = PyList_New(0);

	if (!frames) {
		PyErr_SetString(PyExc_SystemError, "Out of memory\n");
		return NULL;
	}

	// Find the first thread.
	current = PyInterpreterState_ThreadHead(PyThreadState_GET()->interp);

	// Now walk through the thread list, adding frames as we go.
	while(current) {
		if (PyList_Append(frames, (PyObject *)current->frame) == -1) {
			Py_DECREF(frames);
			return NULL;
		}
		current = PyThreadState_Next(current);
	}

	// We have a reference on this list already
	return frames;
}

#if PY_MAJOR_VERSION == 2 && PY_MINOR_VERSION >= 4
#ifndef WIN32
// This structure is copied from dictobject.c...
typedef PyDictObject dictobject;
typedef struct {
	PyObject_HEAD
	dictobject *di_dict; /* Set to NULL when iterator is exhausted */
	int di_used;
	int di_pos;
	PyObject* di_result; /* reusable result tuple for iteritems */
	long len;
} dictiterobject;

// ...and these types are exported from it.
PyAPI_DATA(PyTypeObject) PyDictIterKey_Type;
PyAPI_DATA(PyTypeObject) PyDictIterValue_Type;
PyAPI_DATA(PyTypeObject) PyDictIterItem_Type;

// Return a tuple of children for a dict iterator.
PyObject * dictitersize(PyObject * self, PyObject * args)
{
	PyObject * iter;
	PyObject * dict;
	PyObject * result;

	if (!PyArg_ParseTuple(args, "O", &iter))
		return NULL;

	// Check the object is of the right type.
	if (iter->ob_type != &PyDictIterKey_Type &&
		iter->ob_type != &PyDictIterValue_Type &&
		iter->ob_type != &PyDictIterItem_Type) {
			PyErr_SetString(PyExc_TypeError, "expected a dictionary iterator");
			return NULL;
		}

	// Now return the information.
	dict = (PyObject *)(((dictiterobject *)iter)->di_dict);
	result = ((dictiterobject *)iter)->di_result;
	if (!dict) dict = Py_None;
	if (!result) result = Py_None;
	Py_INCREF(dict);
	Py_INCREF(result);
	return Py_BuildValue("OO", dict, result);
}
#endif
#endif

PyObject * unicodedefenc(PyObject * self, PyObject * args)
{
	PyObject * obj;
	PyUnicodeObject * unicode;
	if (!PyArg_ParseTuple(args, "O", &obj))
		return NULL;

	if (obj->ob_type == &PyUnicode_Type) {
		unicode = (PyUnicodeObject *)obj;
	} else {
		PyErr_SetString(PyExc_TypeError, "expected a unicode string");
		return NULL;
	}

	if (unicode->defenc) {
		Py_INCREF(unicode->defenc);
		return unicode->defenc;
	} else {
		Py_INCREF(Py_None);
		return Py_None;
	}
}

PyObject * longsize(PyObject * self, PyObject * args)
{
	PyObject * obj;
	struct _longobject * l;

	if (!PyArg_ParseTuple(args, "O", &obj))
		return NULL;

	if (PyObject_IsInstance(obj, (PyObject *)&PyLong_Type)) {
		l = (struct _longobject *)obj;
	} else {
		PyErr_SetString(PyExc_TypeError, "expected a long");
		return NULL;
	}

	return Py_BuildValue("i", abs(l->ob_size) * l->ob_type->tp_itemsize);
}

// Return the frame and line number associated with an object
#ifdef HAVE_OBJECT_FRAME_INFORMATION
PyObject * objframe(PyObject * self, PyObject * args)
{
	PyObject * obj;
	if (!PyArg_ParseTuple(args, "O", &obj))
		return NULL;
		
	if (obj->__ob_frame_description) {
		Py_INCREF((PyObject *)obj->__ob_frame_description);
		return (PyObject *)obj->__ob_frame_description;
	} else {
		Py_INCREF(Py_None);
		return Py_None;
	}
}
#endif

PyDoc_STRVAR(_getframes_doc,
"_getframes() -> [frame]\n\
\n\
Return a list of all frames in the system.");

PyDoc_STRVAR(dictitersize_doc,
"dictitersize(iter) -> (size, (children))\n\
\n\
Return the children of a dictionary key, value or item iterator.");

PyDoc_STRVAR(unicodedefenc_doc,
"unicodedefenc(unicode) -> string\n\
\n\
Return the default encoded version of a unicode string, or None.");

PyDoc_STRVAR(longsize_doc,
"longsize(long) -> int\n\
\n\
Return the size of a long object.");

#ifdef HAVE_OBJECT_FRAME_INFORMATION
PyDoc_STRVAR(objframe_doc,
"objframe(obj) -> (frame, line, prev)\n\
\n\
Return the frame and line of code that created an object.");
#endif

static PyMethodDef utils_methods[] = {
	{"_getframes",	_getframes, METH_VARARGS, _getframes_doc },
#if PY_MAJOR_VERSION == 2 && PY_MINOR_VERSION >= 4
	{"dictitersize", dictitersize, METH_VARARGS, dictitersize_doc },
#endif
	{"unicodedefenc", unicodedefenc, METH_VARARGS, unicodedefenc_doc },
	{"longsize", longsize, METH_VARARGS, longsize_doc },
#ifdef HAVE_OBJECT_FRAME_INFORMATION
	{"objframe", objframe, METH_VARARGS, objframe_doc },
#endif
	{NULL,		NULL},
};

PyMODINIT_FUNC initutils(void) {
	Py_InitModule("utils", utils_methods);
}


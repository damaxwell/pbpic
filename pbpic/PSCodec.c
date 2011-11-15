#include "Python.h"
#include "engine.h"

static PyObject *matlabsin( PyObject *self, PyObject *args )
{
  return PyNone;
}


PyMethodDef methods[] = {
    {"matlabsin", matlabsin, METH_VARARGS, "Matlab's sin function."},
    {NULL, NULL, 0, NULL}
};

Engine *matlab;

PyMODINIT_FUNC 
initpscodec()
{
  matlab = engOpen("");
  if(matlab == 0)
  {
    printf("Open matlab failed.\n");
  }
  (void) Py_InitModule("pscodec", methods);   
}

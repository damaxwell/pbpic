#include "Python.h"

static PyObject *t1_decrypt( PyObject *self, PyObject *args )
{

	int R;
	PyObject *bufferObj;

	if( !PyArg_ParseTuple( args, "Oi", &bufferObj, &R ) )
	{
		return NULL;
	}

	void *buf;
	Py_ssize_t len;
	if( PyObject_AsWriteBuffer( bufferObj, &buf, &len) )
	{
		return NULL;
	}
	
	unsigned char *c = buf;
	unsigned char *end = c+len;

	unsigned short int r = R; 
	unsigned short int c1 = 52845; 
	unsigned short int c2 = 22719; 
	unsigned char plain, cipher;
	int i = 0;
	while( c < end )
	{
		cipher = *c;
		plain = (cipher ^ (r>>8)); 
		r = (cipher + r) * c1 + c2; 
		*c++ = plain;
	}
	Py_INCREF( bufferObj );
	return bufferObj;
}

static PyObject *t1_encrypt( PyObject *self, PyObject *args )
{

	int R;
	PyObject *bufferObj;

	if( !PyArg_ParseTuple( args, "Oi", &bufferObj, &R ) )
	{
		return NULL;
	}

	void *buf;
	Py_ssize_t len;
	if( PyObject_AsWriteBuffer( bufferObj, &buf, &len) )
	{
		return NULL;
	}
	
	unsigned char *c = buf;
	unsigned char *end = c+len;

	unsigned short int r = R; 
	unsigned short int c1 = 52845; 
	unsigned short int c2 = 22719; 
	unsigned char plain, cipher;
	int i = 0;
	while( c < end )
	{
		plain = *c;
		cipher = (plain ^ (r>>8)); 
		r = (cipher + r) * c1 + c2; 
		*c++ = cipher;
	}

	Py_INCREF( bufferObj );
	return bufferObj;
}

PyMethodDef methods[] = {
    {"t1_decrypt", t1_decrypt, METH_VARARGS, "Decyrpts a byte array using the T1 font scheme."},
    {"t1_encrypt", t1_encrypt, METH_VARARGS, "Encyrpts a byte array using the T1 font scheme."},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC 
initpscodec()
{
  (void) Py_InitModule("pscodec", methods);   
}

#include "Python.h"
#include <ApplicationServices/ApplicationServices.h>
#include <CoreServices/CoreServices.h>
#include <stdio.h>

#define FONT_NOT_FOUND 1
#define FONT_OK 0


#define PSMAX 256
#define PATHMAX 2048
typedef struct
{
	char psName[PSMAX];
  char path[PATHMAX];
  int fontNum;
} FontData;

int font_data_for_name(const char *fontName,FontData *f);

static PyObject *py_find_font_for_name( PyObject *self, PyObject *args )
{
 char *fontName = NULL;
 // int typeIndex;
 if( !PyArg_ParseTuple( args, "s", &fontName ) )
 {
   return NULL;
 }

 FontData theFont;
 if( font_data_for_name( fontName, &theFont ) != FONT_OK )
 {
   Py_RETURN_NONE;
 }

 PyObject *pyFontPath = PyString_FromString( theFont.path );
 PyObject *pyPSName = PyString_FromString( theFont.psName );

 // Build a tuple to return.
 PyObject *rv = PyTuple_New( 2 );
 PyTuple_SET_ITEM( rv, 0, pyFontPath );
 PyTuple_SET_ITEM( rv, 1, pyPSName );
 return rv;
}

PyMethodDef methods[] = {
    {"find_font", py_find_font_for_name, METH_VARARGS, "Returns a font from the system matching the given name.\nReturns a tuple of two strings (path,psName)."},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC 
initsysfont_mac()
{
  PyObject *module = Py_InitModule("sysfont_mac", methods);   
}


int font_data_for_name(const char *fontName,FontData *f)
{
  CFStringRef fontname = CFStringCreateWithCString( NULL, fontName, kCFStringEncodingUTF8 );
  CTFontDescriptorRef fontdescriptor = CTFontDescriptorCreateWithNameAndSize(fontname,0.0);
  CFRelease(fontname);

  CFURLRef url = CTFontDescriptorCopyAttribute(fontdescriptor,kCTFontURLAttribute);
  if(url == NULL)
  {
    CFRelease(fontdescriptor);
    return FONT_NOT_FOUND;
  }
  
  CFURLGetFileSystemRepresentation( url, true, (unsigned char *) f->path, PATHMAX);
  CFRelease(url);

  CFStringRef psname = CTFontDescriptorCopyAttribute(fontdescriptor,kCTFontNameAttribute);
  CFStringGetCString(psname,f->psName,PSMAX,kCFStringEncodingUTF8);
  CFRelease(psname);

  CFRelease(fontdescriptor);

  return FONT_OK;
}


int main (int argc, const char * argv[]) 
{
	if( argc < 2 )
	{
		printf("Usage: %s FontName\n", argv[0] );
		return -1;
	}

  const char *fontName = argv[1];
  
  FontData theFont;
  
  if( font_data_for_name(fontName,&theFont) != FONT_OK )
  {
    printf("Font %s not found.\n",fontName);
    return 1;
  }
  
  printf("PS name: %s\nPath: %s\n",theFont.psName,theFont.path);
  return 0;
}

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

void show(CFStringRef formatString, ...) {
  CFStringRef resultString;
  CFDataRef data;
  va_list argList;

  va_start(argList, formatString);
  resultString = CFStringCreateWithFormatAndArguments(NULL, NULL, 
  formatString, argList);
  va_end(argList);

  data = CFStringCreateExternalRepresentation(NULL, resultString, CFStringGetSystemEncoding(), '?');

  if (data != NULL) {
    printf ("%.*s\n\n", (int)CFDataGetLength(data), CFDataGetBytePtr(data));
    CFRelease(data);
  }
  CFRelease(resultString);
}


// Returns the resource index of the sfnt matching the postscript name of the font f.
// Returns 0 if no match is found in this fond.
void print_names_in_FOND( Byte *pFOND )
{
  UInt16 numFontRecords = CFSwapInt16BigToHost(*((UInt16 *)(pFOND+52))) + 1;
  FontTableRecord *pFontAssociationTable = (FontTableRecord *)(pFOND+54);
  UInt32 styleTableOffset = CFSwapInt32BigToHost(*((UInt32 *)(pFOND+24)));

  if( sytleTableOffset == 0 )
  {
    printf("not handling single font FOND\n")
  }

  Byte * pSuffixTable = pFOND+styleTableOffset+58;
  UInt16 numStrings = CFSwapInt16ToHost(*( (UInt16 *) pSuffixTable));
  Byte *suffixStrings[64];
  if( numStrings > 64 )
  {
    printf("bailing due to excess strings %d\n", numStrings);
    return NULL;
  }

  // Go find where the strings are in the suffix table
  Byte *pSuffix = pSuffixTable+2;
  for( i = 0; i < numStrings; i++ )
  {
    suffixStrings[i] = pSuffix;
    pSuffix += *pSuffix;
    pSuffix++;
  }

  Byte *suffixMap = pFOND+StyleTableOffset+10;
  int i;
  FontTableRecord *pFontRec = pFontAssociationTable;
  for( i = 0; i<numFontRecords; i++ )
  {

    CFMutableStringRef fName = CFStringCreateMutable(NULL,0);
    CFMutableStringAppendPascalString(suffixStrings[0]);

    int suffixListIndex = *(suffixMap+(pFontRec[i].style) );
    if(suffixListIndex > 1)
    {
      suffixList = suffixStrings[ suffixListIndex - 1 ];
      suffixListEnd = suffixList + *suffixList++ + 1;
      while(suffixList < suffixListEnd)
      {
        CFMutableStringAppendPascalString(suffixStrings[*suffixList++]);
      }
    }
    show(fName);
    CFRelease(fName)
  }
}

void print_resource_based_font( FontData *f )
{
	// Try opening either a data or resource fork based resource based font.
	ResFileRefNum res;
    OSStatus status = FSOpenResourceFile( &(f->fileRef), 0, NULL, fsRdPerm, &res );
    if ( status == noErr  )
	{
		printf("Font in data fork.\n");
	}
	else
	{
		res = FSOpenResFile( &(f->fileRef), fsRdPerm );
		status  = ResError();
		if( status != noErr )
		{
			// Doesn't look like a resource based font.
			return 0;
		}
		printf("Font in resource fork.\n");
	}
	
	// Run through the FOND resources.
	int nFONDs = Count1Resources( 'FOND' );
	int fond_index;
	Handle sfnt = NULL;
	for( fond_index = 0; fond_index < nFONDs; fond_index++ )
	{
		printf("looking in FOND %d\n", fond_index );
		Handle h = Get1IndResource('FOND', fond_index+1);
		printf("loaded!\n");
		print_names_in_fond(h)
	}
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

  print_resource_based_font(&theFont)
  
  return 0;
}

#include "Python.h"
#include <ApplicationServices/ApplicationServices.h>
#include <CoreServices/CoreServices.h>
#include <stdio.h>

#define FONT_NOT_SCALABLE 4
#define FONT_NOT_RESOURCE 3
#define FONT_NOT_IMPLEMENTED 2
#define FONT_NOT_FOUND 1
#define FONT_OK 0

typedef struct
{
  CFStringRef psName;
  CFURLRef url;
  int fontIndex;
  Boolean isResource;
} FontData;

typedef struct
{
	UInt16 size;
	UInt16 style;
	UInt16 id;	
} FontTableRecord;

int font_data_for_name( const char *fontName, FontData *f);
int open_resource_based_font(CFURLRef url, ResFileRefNum *res);
int find_font_in_resource_file(CFStringRef fontName,int*fontIndex);
int count_fonts_in_FOND(Byte*pFOND);
int get_resource_based_font(CFURLRef url, int fontIndex, Handle *sfnt, UInt32 *fsize );

PyObject *PyString_FromCFStringRef(CFStringRef string)
{
  char buf[256];
  char *longBuf;
  if( CFStringGetCString(string,buf,256,kCFStringEncodingUTF8) )
  {
    return PyString_FromString(buf);
  }
  CFIndex longLength = CFStringGetMaximumSizeForEncoding(CFStringGetLength(string),kCFStringEncodingUTF8);
  longBuf = malloc(longLength);
  CFStringGetCString(string,longBuf,longLength,kCFStringEncodingUTF8);
  return PyString_FromString(longBuf);
}

static PyObject *py_find_font_for_name( PyObject *self, PyObject *args )
{
 char *fontName = NULL;
 if( !PyArg_ParseTuple( args, "s", &fontName ) )
 {
   return NULL;
 }

 FontData theFont;
 if( font_data_for_name( fontName, &theFont ) != FONT_OK )
 {
   Py_RETURN_NONE;
 }

 CFStringRef path = CFURLCopyFileSystemPath(theFont.url,kCFURLPOSIXPathStyle); 
 PyObject *pyPath = PyString_FromCFStringRef( path );
 CFRelease(path);

 // Build a tuple to return.
 PyObject *rv = PyTuple_New( 4 );
 PyTuple_SET_ITEM( rv, 0,  pyPath );
 PyTuple_SET_ITEM( rv, 1, PyString_FromCFStringRef( theFont.psName ) );
 PyTuple_SET_ITEM( rv, 2, PyInt_FromLong(theFont.fontIndex) );
 if(theFont.isResource)
 {
   PyTuple_SET_ITEM( rv, 3, Py_True );   
 }
 else
 {
   PyTuple_SET_ITEM( rv, 3, Py_False );      
 }

 CFRelease(theFont.psName);
 CFRelease(theFont.url);
 return rv;
}

static PyObject *py_is_resource_font( PyObject *self, PyObject *args )
{  
  char *fontPath = NULL;
  if( !PyArg_ParseTuple( args, "s", &fontPath) )
  {
    return NULL;
  }

  CFStringRef path = CFStringCreateWithCString( NULL, fontPath, kCFStringEncodingUTF8 );
  CFURLRef url = CFURLCreateWithFileSystemPath(NULL,path, kCFURLPOSIXPathStyle,false);
  CFRelease(path);

  ResFileRefNum res;
  PyObject *rv = Py_False;
  if( open_resource_based_font(url,&res) == FONT_OK )
  {
    rv = Py_True;
    CloseResFile(res);
  }

  return rv;
}

static PyObject *py_load_resource_font( PyObject *self, PyObject *args )
{
  char *fontPath = NULL;
  int fontPathLength = 0;
  int fontIndex = 0;
  if( !PyArg_ParseTuple( args, "s#i", &fontPath,&fontPathLength,&fontIndex ) )
  {
    return NULL;
  }

  CFStringRef path = CFStringCreateWithCString( NULL, fontPath, kCFStringEncodingUTF8 );
  CFURLRef url = CFURLCreateWithFileSystemPath(NULL,path, kCFURLPOSIXPathStyle,false);
  CFRelease(path);
  ResFileRefNum res;
  if( open_resource_based_font(url,&res) != FONT_OK )
  {
    CFRelease(url);
    Py_RETURN_NONE;    
  }

  Handle sfnt;
  UInt32 fsize;
  if( get_resource_based_font(url, fontIndex, &sfnt, &fsize ) != FONT_OK )
  {
    CloseResFile(res);
    CFRelease(url);
    Py_RETURN_NONE;
  }
  CFRelease(url);
  
  PyObject *fontContents = PyString_FromStringAndSize( *sfnt, fsize);
  return fontContents;
}


PyMethodDef methods[] = {
    {"find_font", py_find_font_for_name, METH_VARARGS, "Returns a font from the system matching the given name.\nReturns a tuple of two strings, an int, and a boolean (path,psName,index,isResource)."},
    {"load_resource_font",py_load_resource_font,METH_VARARGS,"Loads a resource based font from the system."},
    {"is_resource_font",py_is_resource_font,METH_VARARGS,"Determines if a font is a resource based font."},
    {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC 
init_sysfont_mac()
{
  PyObject *module = Py_InitModule("_sysfont_mac", methods);   
}


/*
int font_data_for_name(const char *fontName,FontData *f)
{
  f->psName = NULL;
  f->url = NULL;
  f->fontNum = -1;
  f->isResource = false;

  CFStringRef fontname = CFStringCreateWithCString( NULL, fontName, kCFStringEncodingUTF8 );
  CTFontDescriptorRef fontdescriptor = CTFontDescriptorCreateWithNameAndSize(fontname,0.0);
  CFRelease(fontname);

  f->url = CTFontDescriptorCopyAttribute(fontdescriptor,kCTFontURLAttribute);
  if(f->url == NULL)
  {
    CFRelease(fontdescriptor);
    return FONT_NOT_FOUND;
  }

  CTFontRef font = CTFontCreateWithFontDescriptor(fontdescriptor,0.0,NULL);
  f->psName = CTFontCopyPostScriptName(font);
  CFRelease(font);

  CFRelease(fontdescriptor);

  ResFileRefNum res;
  if(open_resource_based_font(f,&res)==FONT_OK)
  {
    int status = find_font_in_resource_file(f->psName,&(f->fontIndex));
    CloseResFile(res);
    if(status!=FONT_OK)
    {
      return FONT_NOT_FOUND;
    }
    f->isResource = true;
  }
  return FONT_OK;

  return FONT_OK;
}
*/

int font_data_for_name( const char *fontName, FontData *f)
{
  f->psName = NULL;
  f->url = NULL;
  f->fontIndex = -1;
  f->isResource = false;

  CFStringRef fontname = CFStringCreateWithCString( NULL, fontName, kCFStringEncodingMacRoman );
  ATSFontRef font = ATSFontFindFromName( fontname, kATSOptionFlagsDefault);
  if( font == 0 )
  {
    font = ATSFontFindFromPostScriptName( fontname, kATSOptionFlagsDefault);
  }
  CFRelease(fontname);
  
  if (font == 0) 
  {
    return FONT_NOT_FOUND;
  }

  FSRef fsref;
  OSStatus status;
  if( ATSFontGetFileReference != NULL)
  {
    status = ATSFontGetFileReference( font, &fsref );    
  }
#if !__LP64__
  else
  {
    ATSFSSpec fsSpec;
    status = ATSFontGetFileSpecification(font,&fsSpec);
    if(status!=noErr)
    {
      return FONT_NOT_FOUND;
    }
    status = FSpMakeFSRef(&fsSpec,&fsref);    
  }
#endif
  if(status!=noErr)
  {
    return FONT_NOT_FOUND;
  }
  f->url = CFURLCreateFromFSRef(  kCFAllocatorDefault, &fsref);
  if(f->url == NULL)
  {
    return FONT_NOT_FOUND;
  }

  ATSFontGetPostScriptName( font, kATSOptionFlagsDefault, &(f->psName) );


  ResFileRefNum res;
  if(open_resource_based_font(f->url,&res)==FONT_OK)
  {
    int status = find_font_in_resource_file(f->psName,&(f->fontIndex));
    CloseResFile(res);
    if(status!=FONT_OK)
    {
      return FONT_NOT_FOUND;
    }
    f->isResource = true;
  }

  return FONT_OK;
}

int open_resource_based_font(CFURLRef url, ResFileRefNum *res)
{
  FSRef fileRef;
  CFURLGetFSRef(url, &fileRef);

  OSStatus status = FSOpenResourceFile( &fileRef, 0, NULL, fsRdPerm, res );
  if ( status != noErr  )
  {
    *res = FSOpenResFile( &fileRef, fsRdPerm );
    status  = ResError();
    if( status != noErr )
    {
      return FONT_NOT_RESOURCE;
    }
  }
  return FONT_OK;
}

int get_resource_based_font(CFURLRef url, int fontIndex, Handle *sfnt, UInt32 *fsize )
{
  ResFileRefNum res;
  if(open_resource_based_font(url,&res)!=FONT_OK)
  {
    return FONT_NOT_RESOURCE;
  }

  int nFONDs = Count1Resources('FOND');
  int FOND_index;
  for( FOND_index = 0; FOND_index<nFONDs; FOND_index++)
  {
    Handle h = Get1IndResource('FOND', FOND_index+1);
    Byte *pFOND = (Byte *) *h;
    int fonts_in_FOND = count_fonts_in_FOND(pFOND);
    if(fontIndex < fonts_in_FOND)
    {
      FontTableRecord *pFontRec = (FontTableRecord *)(pFOND+54) + fontIndex;
      int size = CFSwapInt16BigToHost(pFontRec->size);
      if(size != 0)
      {
        CloseResFile(res);
        return FONT_NOT_SCALABLE;
      }
      *sfnt = Get1Resource( 'sfnt', CFSwapInt16BigToHost(pFontRec->id) );
      if( *sfnt == NULL)
      {
        CloseResFile(res);
        return FONT_NOT_FOUND;
      }
      *fsize = GetResourceSizeOnDisk(*sfnt);
      DetachResource( *sfnt );	
      CloseResFile(res);
      return FONT_OK;
    }
    fontIndex -= fonts_in_FOND;
  }
  CloseResFile(res);
  return FONT_NOT_FOUND;
}

int count_fonts_in_FOND(Byte*pFOND)
{
  return CFSwapInt16BigToHost(*((UInt16 *)(pFOND+52))) + 1;
}

int find_font_in_FOND( Byte *pFOND, char *fontName, int *fontNum)
{
  UInt16 numFontRecords = count_fonts_in_FOND(pFOND);
  FontTableRecord *pFontAssociationTable = (FontTableRecord *)(pFOND+54);
  UInt32 styleTableOffset = CFSwapInt32BigToHost(*((UInt32 *)(pFOND+24)));

  if( styleTableOffset == 0 )
  {
    return FONT_NOT_IMPLEMENTED;
  }

  Byte * pSuffixTable = pFOND+styleTableOffset+58;
  UInt16 numStrings = CFSwapInt16BigToHost(*( (UInt16 *) pSuffixTable));
  Byte *suffixStrings[64];
  if( numStrings > 64 )
  {
    return FONT_NOT_IMPLEMENTED;
  }

  // Go find where the strings are in the suffix table
  Byte *pSuffix = pSuffixTable+2;
  int i;
  for( i = 0; i < numStrings; i++ )
  {
    suffixStrings[i] = pSuffix;
    pSuffix += *pSuffix;
    pSuffix++;
  }

  // Match the basename
  Byte *pBase = suffixStrings[0];
  int nBase = *pBase++;
  Byte *pBaseEnd = pBase + nBase;
  while( pBase < pBaseEnd )
  {
    if(*fontName++ != *pBase++)
    {
      return FONT_NOT_FOUND;
    }
  }

  Byte *suffixMap = pFOND+styleTableOffset+10;
  FontTableRecord *pFontRec = pFontAssociationTable;
  for( i=0; i<numFontRecords; i++)
  {
    int size =  CFSwapInt16BigToHost(pFontRec[i].size);
    // Skip non-scalable fonts.
    if( size != 0 )
    {
      continue;
    }

    int style = CFSwapInt16BigToHost(pFontRec[i].style);
    int suffixListIndex = *(suffixMap+style);

    // A suffix index of 1 means just match the basename.
    if( suffixListIndex == 1)
    {
      if(*fontName==0)
      {
        *fontNum = i;
        return FONT_OK;
      }
      continue;
    }

    Byte *suffixList = suffixStrings[suffixListIndex-1];
    int numSuffixes = *suffixList++;
    char *tailStart = fontName;

    int k;
    for(k=0;k<numSuffixes;k++)
    {
      int sIndex = *suffixList++;
      Byte *suffix = suffixStrings[sIndex-1];
      int sLength = *suffix++;
      int l;
      for(l=0;l<sLength;l++)
      {
        if(*tailStart++!=*suffix++)
        {
          goto nextFont;
        }
      }
    }
    // If we get here, we have checked all suffixes and all characters matched so far.
    // Hence, if we are at the end of the font name, we have a match.
    if( *tailStart == 0)
    { 
      *fontNum = i;
      return FONT_OK;
    }
    nextFont: ;
  }
  return FONT_NOT_FOUND;
}
  
int find_font_in_resource_file(CFStringRef fontName, int*fontIndex)
{
  char psFontName[256];
  CFStringGetCString(fontName,psFontName,255,kCFStringEncodingMacRoman);

  int nFONDs = Count1Resources( 'FOND' );
  int fond_index;
  int fontsThisFile = 0;
  for( fond_index = 0; fond_index < nFONDs; fond_index++ )
  {
    Handle h = Get1IndResource('FOND', fond_index+1);
    int error = find_font_in_FOND((Byte*) *h, psFontName, fontIndex);
    if( error == FONT_OK)
    {
      *fontIndex += fontsThisFile; 
      return FONT_OK;
    }
    fontsThisFile += count_fonts_in_FOND((Byte*) *h);
  }
  return FONT_NOT_FOUND;
}

int find_scalable_fonts_in_FOND( Byte *pFOND, CFMutableArrayRef fontList)
{
  UInt16 numFontRecords = count_fonts_in_FOND(pFOND);
  FontTableRecord *pFontAssociationTable = (FontTableRecord *)(pFOND+54);
  UInt32 styleTableOffset = CFSwapInt32BigToHost(*((UInt32 *)(pFOND+24)));

  if( styleTableOffset == 0 )
  {
    return FONT_NOT_IMPLEMENTED;
  }

  Byte * pSuffixTable = pFOND+styleTableOffset+58;
  UInt16 numStrings = CFSwapInt16BigToHost(*( (UInt16 *) pSuffixTable));
  Byte *suffixStrings[64];
  if( numStrings > 64 )
  {
    return FONT_NOT_IMPLEMENTED;
  }

  // Go find where the strings are in the suffix table
  Byte *pSuffix = pSuffixTable+2;
  int i;
  for( i = 0; i < numStrings; i++ )
  {
    suffixStrings[i] = pSuffix;
    pSuffix += *pSuffix;
    pSuffix++;
  }
  
  Byte *suffixMap = pFOND+styleTableOffset+10;
  FontTableRecord *pFontRec = pFontAssociationTable;
  for( i = 0; i<numFontRecords; i++ )
  {
    int size =  CFSwapInt16BigToHost(pFontRec[i].size);
    if( size != 0 )
    {
      CFArrayAppendValue(fontList,kCFNull);
      continue;
    }

    int style = CFSwapInt16BigToHost(pFontRec[i].style);

    CFMutableStringRef fName = CFStringCreateMutable(NULL,0);
    CFStringAppendPascalString(fName,suffixStrings[0],kCFStringEncodingMacRoman);

    int suffixListIndex = *(suffixMap+style);
    if(suffixListIndex > 1)
    {
      Byte *suffixList = suffixStrings[ suffixListIndex - 1 ];
      Byte *suffixListEnd = suffixList + *suffixList++ + 1;
      while(suffixList < suffixListEnd)
      {
        CFStringAppendPascalString(fName,suffixStrings[*suffixList++-1],kCFStringEncodingMacRoman);
        
      }
    }
    CFArrayAppendValue(fontList,fName);
    CFRelease(fName);
  }
  return FONT_OK;
}


int find_scalable_fonts_in_resource_font( CFMutableArrayRef fontList )
{
  int nFONDs = Count1Resources( 'FOND' );
  int fond_index;
  for( fond_index = 0; fond_index < nFONDs; fond_index++ )
  {
    Handle h = Get1IndResource('FOND', fond_index+1);
    int error = find_scalable_fonts_in_FOND((Byte*) *h, fontList);
    if( error != FONT_OK)
    {
      return error;
    }
  }
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

  CFStringRef path = CFURLCopyFileSystemPath(theFont.url, kCFURLPOSIXPathStyle);
  
  // show(theFont.psName);
  // show(path);
  CFRelease(path);

  ResFileRefNum res;
  if( open_resource_based_font(theFont.url,&res) == FONT_OK)
  {
    // char buf[256];
    // CFStringGetCString(theFont.psName,buf,256,kCFStringEncodingMacRoman);
    
    int fontIndex;
    int error = find_font_in_resource_file(theFont.psName,&fontIndex);
    if(error == FONT_OK)
    {
      printf("Found resource font at index %d.\n",fontIndex);
      Handle sfnt; UInt32 fsize;
      get_resource_based_font(theFont.url, theFont.fontIndex, &sfnt, &fsize);
      printf("Data of size %d\n",fsize);
    }
    else
    {
      printf("Did not find font in resource font.\n");
    }
    
    // CFMutableArrayRef fontList = CFArrayCreateMutable(NULL,0,&kCFTypeArrayCallBacks);
    // if( find_scalable_fonts_in_resource_font(fontList) == FONT_OK)
    // {
    //   int k;
    //   CFIndex numFonts = CFArrayGetCount(fontList);
    //   for( k=0;k<numFonts;k++)
    //   {
    //     CFStringRef fontName = CFArrayGetValueAtIndex(fontList,k);
    //     if(fontName == (CFStringRef) kCFNull)
    //     {
    //       printf("Font %d: Non-scalable\n",k);
    //     }
    //     else
    //     {
    //       char buf[256];
    //       if( CFStringGetCString(fontName, buf, 256, kCFStringEncodingMacRoman) )
    //       {            
    //         printf("Font %d: %s\n",k,buf);
    //       }
    //       else
    //       {
    //         printf("Font %d: <Long Name>\n",k);
    //       }
    //     }
    //   }
    // }
    // CFRelease(fontList);
    CloseResFile(res);
  }
  else
  {
    printf("Not a resource based font.\n");
  }

  return 0;
}

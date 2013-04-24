#define FONT_NOT_SCALABLE 4
#define FONT_NOT_RESOURCE 3
#define FONT_NOT_IMPLEMENTED 2
#define FONT_NOT_FOUND 1
#define FONT_OK 0

#include <CoreServices/CoreServices.h>

char *p_to_c(Byte *p) {
  static char buffer[257];
  int n = *p++;
  memcpy(buffer,p,n);
  buffer[n]=0;
  return buffer;
}

int main (int argc, const char * argv[]) 
{
  if( argc < 2 )
  {
    printf("Usage: %s path\n", argv[0] );
    return -1;
  }

  const char *fontName = argv[1];

  CFAllocatorRef allocator = NULL;

  CFStringRef fontpath = CFStringCreateWithCString( allocator, argv[1], kCFStringEncodingMacRoman );

  Boolean isDirectory = false;
  CFURLRef fonturl = CFURLCreateWithFileSystemPath (allocator, fontpath, kCFURLPOSIXPathStyle, isDirectory);


  ResFileRefNum res;
  FSRef fileRef;
  CFURLGetFSRef(fonturl, &fileRef);

  OSStatus status = FSOpenResourceFile( &fileRef, 0, NULL, fsRdPerm, &res );

  if ( status != noErr  )
  {
    res = FSOpenResFile( &fileRef, fsRdPerm );
    status  = ResError();
    if( status != noErr )
    {
      printf("Font not resource\n");
      return FONT_NOT_RESOURCE;
    }
  }

  int nFONDs = Count1Resources('FOND');
  printf("Suitcase contains %d FONDs\n",nFONDs);
  int FOND_index;
  for( FOND_index = 0; FOND_index<nFONDs; FOND_index++)
  {
    Handle h = Get1IndResource('FOND', FOND_index+1);
    Byte *pFOND = (Byte *) *h;

    printf("Font family id %2x%2x\n",pFOND[2],pFOND[3]);

    UInt32 styleTableOffset = CFSwapInt32BigToHost(*((UInt32 *) (pFOND+2*8+2*4)));
    printf("style table at %d\n",styleTableOffset);
    Byte * styleTable = pFOND + styleTableOffset;

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


    int tableOffset = 52;//2*8+3*4+18+4+2;
    UInt16 *pTable = (UInt16 *) (pFOND+tableOffset);
    int n_fonts = CFSwapInt16BigToHost(*pTable)+1;
    printf("Table contains %d fonts.\n",n_fonts);
    for(int i=0;i<n_fonts;i++) {
      int size = CFSwapInt16BigToHost(pTable[1+i*3+0]);
      int style = CFSwapInt16BigToHost(pTable[1+i*3+1]);
      int resnumber = CFSwapInt16BigToHost(pTable[1+i*3+2]);
      printf("Font %d: size: %d style: %d resource number: %d\n",i,size,style,resnumber);

      int styleIndex = *(styleTable+10+style)-1;
      printf("Style index for %d is %d\n",style,styleIndex);
      printf("Font is %s",p_to_c(suffixStrings[0]));
      if(styleIndex!=0) {
        Byte *suffixList = suffixStrings[styleIndex];
        int n_suffixes = *suffixList;
        for(int k=0; k<n_suffixes; k++) {
          printf("%s",p_to_c(suffixStrings[suffixList[k+1]-1]));
        }
      }
      printf("\n");
    }
  }

  CloseResFile(res);

  CFRelease(fontpath);
  
  CFRelease(fonturl);

  return 0;
}

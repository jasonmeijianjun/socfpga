#include<stdio.h>
#include <stdlib.h>

int main()
{
	int i,j;
	int size;
	FILE * infile, *outfile_odd,* outfile_even;
	char * inbuf, * outbuf_odd,* outbuf_even; 	

	infile = fopen("BOOT.bin","rb");
	if ( !infile ) {
		printf("Unable to open input file!");
		return 1;
	}
	
	outfile_odd = fopen("outfile_odd.bin","wb");
	if ( !outfile_odd ) {
		printf("Unable to open output odd file!");
		return 1;
	}
	
	outfile_even = fopen("outfile_even.bin","wb");
	if ( !outfile_even ) {
		printf("Unable to open output even file!");
		return 1;
	}
	/*Get the input file size*/
	fseek(infile,0,SEEK_END );
	size = ftell(infile);
	if (size % 4096 )
		size = (size / 4096) * 4096 + 4096 ;
	printf("In file size %d\n",size);
	
	/*malloc the in buffer, out buffer*/
	inbuf = malloc(size);
	outbuf_odd  = malloc( size/2 );
	outbuf_even = malloc( size/2 );

	fseek(infile,0,SEEK_SET);	
	fread(inbuf,size,1,infile);
	fclose(infile);

	/*manipulan the output buffer*/
	for(i = 0;i <  size/2 ; i++) {
                j = 2 * i; 
		outbuf_odd[i]  = inbuf[j + 1]; 
		outbuf_even[i] = inbuf[j]; 
	}

	fseek(outfile_odd,0,SEEK_SET);	
	fwrite(outbuf_odd, size/2 ,1,outfile_odd);
	fclose(outfile_odd);


	fseek(outfile_even,0,SEEK_SET);	
	fwrite(outbuf_even, size/2 ,1,outfile_even);
	fclose(outfile_even);
	free(inbuf);
	free(outbuf_odd);
	free(outbuf_even);

	return 0;
}

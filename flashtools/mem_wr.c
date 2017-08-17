#include<stdio.h>  
#include<unistd.h>  
#include<sys/mman.h>  
#include<sys/types.h>  
#include<sys/stat.h>  
#include<fcntl.h> 
#include <stdlib.h>
 
int main(int argc,char *argv[])  
{  
	unsigned char * map_base;  
	FILE *f;  
	int n, fd;  
	int i;
	unsigned long PHY_BASE;
	unsigned long size;
									  
	unsigned long addr;  
	unsigned char content;  

	FILE * infile;
	char * inbuf; 	
	char *stop;
        if (argc < 3) {
            fprintf(stderr, "Usage: %s str [base]  str [size]\n", argv[0]);
            exit(-1);
        }

	/*Get the base address of the flash*/
//	PHY_BASE = strtoul(argv[1], &stop, 16);
	PHY_BASE = strtoul(argv[1], 0,  0);
	printf("ori---0x%lx---\n", PHY_BASE);

	/*open the flash image */
	infile = fopen(argv[2],"rb");
	if ( !infile ) {
		printf("Unable to open input file!");
		return 1;
	}
	
	/*Get the input file size*/
	fseek(infile,0,SEEK_END );
	size = ftell(infile);
	if (size % 4096 )
		size = (size / 4096) * 4096 + 4096 ;
	printf("In file size %d\n",size);
	
	/*malloc the in buffer and read infile */
	inbuf = malloc(size);
	fseek(infile,0,SEEK_SET);	
	fread(inbuf,size,1,infile);
	fclose(infile);

	fd = open("/dev/mem", O_RDWR| O_SYNC);  
	if (fd == -1)  {  
		return (-1);  
	}  
				  
	map_base = mmap(NULL, size, PROT_READ|PROT_WRITE,\
			 MAP_SHARED, fd, PHY_BASE);  
					  
	if (map_base == 0) {  
			printf("NULL pointer!\n");  
	}   else  {  
			printf("Successfull! map_base=%lx\n", map_base);  
	}

	/*write the image to flash*/					
	for (i = 0;i < size; i+=0x10)  {  
		*(volatile int*)(map_base + i)       = *(int*)(inbuf + i); 
		*(volatile int*)(map_base + i + 4)   = *(int*)(inbuf + i + 4);
		*(volatile int*)(map_base + i + 8)   = *(int*)(inbuf + i + 8);
		*(volatile int*)(map_base + i + 0xc) = *(int*)(inbuf + i + 0xc);  
	}  
#if 0	
	for (i = 0;i < size; i+=0x10)  {  
		printf("0x%lx: %8x %8x %8x %8x\n", PHY_BASE+i,\
			*(volatile int*)(map_base+i),\
			*(volatile int*)(map_base+i+4),\
			*(volatile int*)(map_base+i+8),\
			*(volatile int*)(map_base+i+0xc));  
	}  
#endif											  
	free(inbuf);
												  
	munmap(map_base, size);  
	close(fd);  
													  
	return (1);  
}  

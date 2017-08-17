#include<stdio.h>  
#include<unistd.h>  
#include<sys/mman.h>  
#include<sys/types.h>  
#include<sys/stat.h>  
#include<fcntl.h> 
#include <stdlib.h>
 
//#define PHY_BASE 0x171d4a000 
#define SIZE 0x40000
int main(int argc,char *argv[])  
{  
	unsigned char * map_base;  
	FILE *f;  
	int n, fd;  
	int i;
	unsigned long PHY_BASE;
	FILE  *outfile;
	char  * outbuf; 	
									  
	unsigned long addr;  
	unsigned char content;  

	char *stop;
        if (argc < 2) {
            fprintf(stderr, "Usage: %s str [base]\n", argv[0]);
            exit(-1);
        }


	PHY_BASE = strtoul(argv[1], 0,0);
	printf("ori---0x%lx---\n", PHY_BASE);

	fd = open("/dev/mem", O_RDWR);  
	if (fd == -1)  {  
			return (-1);  
	}  
				  
	map_base = mmap(NULL, SIZE, PROT_READ|PROT_WRITE, MAP_SHARED, fd, PHY_BASE);  
					  
	if (map_base == 0) {  
			printf("NULL pointer!\n");  
	}   else  {  
			printf("Successfull! map_base=0x%lx\n", map_base);  
	} 

	outfile = fopen("outfile.bin","wb");

	if ( !outfile ) {
		printf("unable to open output  file!");
		return 1;
	}
	outbuf  = malloc( SIZE );
	for (i = 0;i < SIZE; i+=0x10)  {  
		
		*(volatile int*)(outbuf+i)     = *(int*)(map_base+i);
		*(volatile int*)(outbuf+i+4)   = *(int*)(map_base+i+4);
		*(volatile int*)(outbuf+i+8)   = *(int*)(map_base+i+8);
		*(volatile int*)(outbuf+i+0xc) = *(int*)(map_base+i+0xc);  
	}

	fseek(outfile,0,SEEK_SET);	
	fwrite(outbuf, SIZE/2 ,1,outfile);
	fclose(outfile);
										  
	close(fd);  
														  
	munmap(map_base, SIZE);  
															  
	return (1);  
}  

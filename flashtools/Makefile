#Makefile for building soc flash related tools.
#binary_op.c
#Makefile
#mem_rd.c
#mem_wr.c
all: binary_operate flash_read flash_write
binary_operate : binary_op.c
	gcc -o  $@ $^ 
flash_read : mem_rd.c
	${CROSS_COMPILE}gcc -o $@  $^
flash_write:mem_wr.c
	${CROSS_COMPILE}gcc -o $@  $^

clean:
	rm -rf binary_operate flash_read flash_write

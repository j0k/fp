file=fp.py
all:
	echo "make test1; or make tutorial"
test1:
	cat test/test.sh
	#================
	./${file} -C "a:/etc/passwd:/etc/fstab" test/test.sh
	#echo "If you see the source of /etc/fstab it means that everything OK"
	#echo "In otherway check that you have boost (c++) installed"

_file:
	gcc -w -fpermissive -fPIC -c -Wall file.cpp
	gcc -shared file.o -ldl -lstdc++ -o wrap_loadfile.so

install:
	cp ${file} /usr/bin/FILE_PRELOAD

tutorial:
	docs/tut.sh

tut:
	docs/tut.sh

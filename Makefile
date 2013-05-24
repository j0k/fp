file=fp.py

_test:
	LD_PRELOAD="./wrap_loadfile.so" test/test.sh

_file:
	gcc -w -fpermissive -fPIC -c -Wall file.cpp
	gcc -shared file.o -ldl -lstdc++ -o wrap_loadfile.so

install:
	cp ${file} /usr/bin/FILE_PRELOAD

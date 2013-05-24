fp = FILE_PRELOAD
==
 ---------------
_|_|_|_| _|_|_|  
_|       _|    _|
_|_|_|   _|_|_|  
_|       _|      
_|       _|      
 ---------------
_______________ 

File Preload like LD_PRELOAD

_______________ 
     __                    
     /        /            
----/-----__-/----__----__-
   /    /   /   /___) /   )
 _/_ __(___/___(___ _(___(_
====================
_______________ 
idea:

 we have program_A & program_C  which use program_B
 after new update of B program_A works correctly with B but C crashed down

 so we need to have program_B.old & and program_B.new and before C runs do the next
   
     $: ll /usr/bin/program_B 
     # =>  /usr/bin/program_B -> /usr/bin/program_B.new

     $: ln -sf /usr/bin/program_B.old /usr/bin/program_B
     $: ./program_C

     # then revert
     $: ln -sf /usr/bin/program_B.new /usr/bin/program_B
     #: ./program_A

we can do it with bash script but it's not a good deal when A & C runs B in random-threaded time.

Cute way will be the next:

            $: FILE_PRELOAD -C "execve+open+stat:/usr/bin/program_B:/usr/bin/program_B.old" -- bash
      (new) $: ./program_C
      	or
	    $: FILE_PRELOAD -C "execve+open+stat:/usr/bin/program_B:/usr/bin/program_B.old" -- ./program_C
    
    (other) $: ./program_A   

 
======================
end of the story

 _______________ 
< HOW ITS WORKS >
 --------------- 
        \   ^__^
         \  (<>)\_______
            (__)\       )\/\
             @ ||----w |
               ||     ||
1.  Firstly it parse syscalls from config or command line
    ./fp.py -c config ... || ./fp.py "open:/A:/B" -- evalprog

1.2 Calculate MD5 hash from options+config string 
1.5 See does we have already launched FP with such config
    (usually /tmp/$USER/FILE_PRELOAD/confs.md5)
1.7 If not launched:
2.     Generate .cpp file (usually in /tmp/$USER/FILE_PRELOAD/cpp/)
3.     Compile it to shared lib and put to some ..E_PRELOAD/so/)
4.  launch command line
    (smth like LD_PRELOAD=/tmp/$USER/FILE_PRELOAD/so/02402012b7.so cat /etc/passwd


 .____ _ .     .____    _____
 /     | /     /       (     
 |__.  | |     |__.     `--. 
 |     | |     |           | 
 /     / /---/ /----/ \___.' 
======================

| file             | description                                      |
|------------------+--------------------------------------------------|
| ./               |                                                  |
| ├── configs      | examples                                         |
| │   ├── cf2.ex   | ex: ./fp.py -c configs/cf2.ex -- cat /etc/passwd |
| │   └── cf.ex    |                                                  |
| ├── docs         |                                                  |
| │   ├── DO       | TODO in future                                   |
| │   └── hook.org | these hooks we hook                              |
| ├── fp.py        | main file                                        |
| ├── Makefile     | make install                                     |
| ├── README.md    |                                                  |
| ├── sh_prev_ex   |                                                  |
| │   ├── f1.cpp   | just to see the start of deal                    |
| │   └── f2.cpp   |                                                  |
| └── test         |                                                  |
| --> └── test.sh  |                                                  |
|                  |                                                  |

======================


    _    ____  ____ ___ _____ ___ ___  _   _    _    _     
   / \  |  _ \|  _ \_ _|_   _|_ _/ _ \| \ | |  / \  | |    
  / _ \ | | | | | | | |  | |  | | | | |  \| | / _ \ | |    
 / ___ \| |_| | |_| | |  | |  | | |_| | |\  |/ ___ \| |___ 
/_/   \_\____/|____/___| |_| |___\___/|_| \_/_/   \_\_____|
=====================

The code of generated .cpp file a bit like Jynx-Kit rootkit

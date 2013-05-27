#!/bin/bash

# just a tutorial for FILE_PRELOAD


function anyk {
    echo -en "...Press ANY key (key \"a\")..."
    read -n 1
    echo -en "                                   \r"
}

function textpart {
    part=$1
    mpart=12
    echo -en "                         _____________  \r\n"
    printf   ".-~=====================< part: %2s/%2s >=========\n" \
	$part $mpart
    echo     "|                        \\-----------/"
    echo     "^"
    case $part in
	1)  
	    cat <<EOF
  This is a short tutorial about some directions 
how to use FILE_PRELOAD.

(We will call FILE_PRELOAD as FP to be short)
EOF
	    ;;
	2) 
	    cat <<EOF
  Imagine! You use a PROGRAM which was developed by 
Silk Mind Company.

 _____________________________________ 
/ Today we announced a new version of \\
\\ the PROGRAM!                        /
 ------------------------------------- 
        \   ^__^
         \  (<>)\_______
            (__)\       )\\/\\
                ||----w |
                ||     ||
EOF
	    ;;
	3)
	    cat <<EOF
                          __      __ __ __                   
.--.--.-----.--.--.---.-.|  |    |  |__|  |--.  .-----.-----.
|  |  |__ --|  |  |  _  ||  |    |  |  |  _  |__|__ --|  _  |
|_____|_____|_____|___._||__|____|__|__|_____|__|_____|_____|
                           |______|                          

PROGRAM used usual_lib.so and try to load it from /lib/ with special modification. All other program use it without any modifications.

So:
  PROGRAM use usual_lib.so with modification mod_SPEC,
  OTHER_PROGRAM it with mod_old mod.
EOF
	    ;;
	4)
	    cat <<EOF
     _  _  _      
  _ (_)(_)(_)_    
 (_)        (_)   
          _ (_)   
       _ (_)      
      (_)         
       _          
      (_)         

What you will do in such situation?

Think about it.
EOF
	    ;;
	5)
	    cat <<EOF
So. We have:

$ pwd; tree 
/tmp/e
.
├── bin
│   ├── OTHER_PROGRAM
│   └── PROGRAM
└── lib
    ├── usual_lib_mod.so
    └── usual_lib.so

$ for f in lib/*; do echo FILE: \$f; cat \$f; done
FILE: lib/usual_lib_mod.so
SPECIAL_MOD
FILE: lib/usual_lib.so
USUAL_MOD

$ cat bin/PROGRAM 
#!/bin/bash

file=/tmp/e/lib/usual_lib.so
if [ -f \$file ]
then
    mod=\`cat \$file | grep SPECIAL_MOD\`
    if ! [ "\$mod" == "" ]; then
        echo "\$0: SUCCESS"
    else
        echo "\$0: You use OLD version of \$(basename \$file)"
    fi
fi

$ cat bin/OTHER_PROGRAM 
#!/bin/bash

file=/tmp/e/lib/usual_lib.so
if [ -f \$file ]
then
    mod=\`cat \$file | grep USUAL_MOD\`
    if ! [ "\$mod" == "" ]; then
        echo "\$0: SUCCESS"
    else
        echo "\$0: You strange version of \$(basename $file)"
    fi
fi

$ bin/PROGRAM 
bin/PROGRAM: You use OLD version of usual_lib.so
$ bin/OTHER_PROGRAM 
bin/OTHER_PROGRAM: SUCCESS
EOF
	    ;;
	6) cat <<EOF
Our actions:

$ cat > bin/PROGRAM.p
#!/bin/bash

FILE_PRELOAD -C "a:/tmp/e/lib/usual_lib.so:/tmp/e/lib/usual_lib_mod.so" -- bin/PROGRAM

$ bin/PROGRAM.p 
bin/PROGRAM: SUCCESS

ITS WORKING!
(.p - means patched)
EOF
	    ;;
	7) cat <<EOF
What really happened?

1. FILE_PRELOAD created .cpp file in /tmp/\$USER/FILE_PRELOAD/cpp/02350b5614.cpp
2. compiled to /tmp/$USER/FILE_PRELOAD/so/02350b5614.so
3. run LD_PRELOAD=./tmp/$USER/FILE_PRELOAD/so/02350b5614.so bin/PROGRAM

cpp file have the next look:
...
    #define I int
    #define C char
    #define S string
    #define P // old_printf
    #define R return
...
    typedef map<S,S> MAP;
...
    static I (*old_printf)(const C* f) = dlsym(RTLD_NEXT, "printf");
    
    static I (*old_stat)(const C *p, struct stat *buf);
    static I (*old_lstat64)(const C *p, struct stat64 *buf);
    static I (*old___lxstat64)(I ver,const C *p, struct stat64 *buf);
    static I (*old_lstat)(const C *p, struct stat *buf);
    static I (*old_fopen)(const C *p, const C * mode);
    static I (*old_mkdir)(const C *p);
    static I (*old_opendir)(const C *p, mode_t mode );
    static I (*old___lxstat)(I ver, const C *p, struct stat *buf);
    static I (*old_freopen64)(const C *p, const C * mode, _IO_FILE * file);
    static I (*old_execve)(const C *p, C *const argv[], C *const envp[]);
    static I (*old_unlinkat)(I dirfd, const C *p, int flags);
    static I (*old_freopen)(const C *p, const C * mode, _IO_FILE * file);
    static I (*old_fopen64)(const C *p, const C * mode);
    static I (*old_unlink)(const C *p);
    static I (*old_open)(const C *p, I flags, mode_t mode);
    static I (*old_stat64)(const C *p, struct stat64 *buf);
    static I (*old_rmdir)(const C *p);
...
//example
extern "C" 
    I open (const C *p, I flags, mode_t mode){
      old_open = dlsym(RTLD_NEXT, "open");
      P("open hook\n");    
      
      MAP files;
      files[pathS(PA(p))]=pathS(PA(p));
      files["/tmp/e/lib/usual_lib.so"]="/tmp/e/lib/usual_lib_mod.so";
      
      S newpath = files[pathS(PA(p))]; 
    
      R old_open(newpath.c_str(), flags, mode);
    }
---
Is is simple.
EOF
	    ;;
	    8) cat <<EOF
    ___               ___      ___      ___     // //  ___    
  ((   ) ) //   / / ((   ) ) //   ) ) //   ) ) // // ((   ) ) 
   \ \    ((___/ /   \ \    //       //   / / // //   \ \     
//  ) )       / / //  ) )  ((____   ((___( ( // // //  ) ) 

If we take a look at the source code of FP we will find the next:

syscalls = [ #synonims
    ["open"      ,     "o"  , "op"  , "A" , "a"], 
    ["fopen"     ,     "fo" , "op"  , "A" , "a"], 
    ["fopen64"   ,     "fo" , "op"  , "A" , "a"], 
    ["opendir"   ,     "od" , "op"  , "A" , "a"], 
    ["mkdir"     ,     "nd" , "op"  , "A" , "a"], 
    ["execve"    ,     "e"  , "A"   , "a"], 
    ["unlink"    ,     "u"  , "rm"  , "A" , "a"], 
    ["unlinkat"  ,     "u"  , "rm"  , "A" , "a"], 
    ["rmdir"     ,     "rm" , "A"   , "a"], 
    ["stat"      ,     "s"  , "A"   , "a"], 
    ["lstat"     ,     "s"  , "A"   , "a"], 
    ["lstat64"   ,     "s"  , "A"   , "a"], 
    ["__lxstat"  ,     "sx" , "Ax"  , "a"], 
    ["__lxstat64",     "sx" , "Ax"  , "a"], 
    ["stat64"    ,     "s"  , "A"   , "a"], 
    ["__xstat"   ,     "sx" , "Axx"], 
    ["__xstat64" ,     "sx" , "Axx"],
    ["__fxstatat",     "sxx"],
    ["freopen"   ,     "fo" , "op"  , "A" , "a"], 
    ["freopen64" ,     "fo" , "op"  , "A" , "a"]
]
---


so "a:/tmp/e/lib/usual_lib.so:/tmp/e/lib/usual_lib_mod.so" means:

generate: open, fopen, fopen64, ... freopen64 except __xstat & __xstat64.

The next command works fine too:
$ FILE_PRELOAD -C "open:/tmp/e/lib/usual_lib.so:/tmp/e/lib/usual_lib_mod.so" -- bin/PROGRAM
bin/PROGRAM: SUCCESS

(generate only function for 'open'. If you want to generate funcs for open & execve => "open+execve:/file1:/file2")
EOF
	    ;;
	9)
	    cat <<EOF
Now, lets change PROGRAM code a bit (diff PROGRAM.new PROGRAM.old):
< file=/tmp/e/lib/../lib/usual_lib.so
> file=/tmp/e/lib/usual_lib.so

FILE_PRELOAD -C "a:/tmp/e/lib/usual_lib_mod.so:/tmp/e/lib/usual_lib.so" -- bin/PROGRAM
bin/PROGRAM: You use OLD version of usual_lib.so

What a pity!
EOF
	    ;;
	10) cat<<EOF
Our actions:

$ FILE_PRELOAD -C "open+f:/tmp/e/lib/usual_lib.so:/tmp/e/lib/usual_lib_mod.so" -- bin/PROGRAM
bin/PROGRAM: SUCCESS

it's because "+f" call short_path on argument of syscall-ARGV and make a/../b => b.

The most default options are "a+f", "A+F" & "a+F".

EOF
	    ;;
	11) cat <<EOF
  ___    __    __  __  ____ 
 / __)  /__\  (  \/  )( ___)
( (_-. /(__)\  )    (  )__) 
 \___/(__)(__)(_/\/\_)(____)

At the end here is a little call-game:

$ echo f1   > game/f1
$ echo f22  > game/f2
$ echo f333 > game/f3

$ tree -s game/
game/
├── [          3]  f1
├── [          4]  f2
└── [          5]  f3
# 3,4,5 => file sizes

$ FILE_PRELOAD -C "op:game/f1:game/f2;rm:game/f2:game/f3;s+sx:game/f2:game/f1" -- cat game/f1
f22

$ FILE_PRELOAD -C "op:game/f1:game/f2;rm:game/f2:game/f3;s+a+sxx:game/f2:game/f1" -- ls -l game/
total 12
-rw-r--r-- 1 u u 3 May 27 13:24 f1
-rw-r--r-- 1 u u 3 May 27 13:24 f2
-rw-r--r-- 1 u u 5 May 27 13:26 f3
# filesize(f2) = 3

$ ls -l game/*
-rw-r--r-- 1 u u 3 May 27 13:24 game/f1
-rw-r--r-- 1 u u 4 May 27 13:26 game/f2
-rw-r--r-- 1 u u 5 May 27 13:26 game/f3

$ FILE_PRELOAD -C "op:game/f1:game/f2;rm:game/f2:game/f3;s+a+sxx:game/f2:game/f1" -- du -sk game/*
4       game/f1
4       game/f3
# wtf! where is f2? it's strange

$ FILE_PRELOAD -C "op:game/f1:game/f2;rm:game/f2:game/f3;s+a+sxx:game/f2:game/f1" -- rm game/f2; ls game/
f2  f3	

$ FILE_PRELOAD -C "op+f:game/f1:game/f2;rm+f:game/f2:game/f3;A:game/f2:game/f1" bash
$ cat game/f1
f22

# PS: there are a lot of other calls which we don't hook
EOF
	    ;;
	12) cat <<EOF
Want say/ask smth or advice:
 - just PM

Have an idea of any proj || startup || little service:
 - lets do it quick. 

Maybe you have an idea of cryptocurrency service?
- welcome 

Or you just want to connect APL/J/K langs to some project?
- Oh e! PM.

contacts:
- silkneo h0td0g Gmail dot com

donate opts:
- ( BTC: 1dreamMuQ1owg1AJhP3QVzwoMUXpQa3cU  ,
    LTC: Ldreamtf2nyRQS5F9wNSfqUC16wP8LDriP ,
    CNC: CKBwtFiB4UrCCnEjXAWbkDdULg87y5fwD2 ,
    YAC: YHKanDc9bidaDTwzGUTu9DMwCcW7FeWSKC )
EOF
	    ;;

    esac
    echo
    printf "'-,_-===========================================\n" 
}

textpart 1
anyk
textpart 2
anyk
textpart 3
anyk
textpart 4
anyk
textpart 5
anyk
textpart 6
anyk
textpart 7
anyk
textpart 8
anyk
textpart 9
anyk
textpart 10
anyk
textpart 11
anyk
textpart 12

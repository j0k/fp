#!/usr/bin/env python

import sys
from optparse import OptionParser

syscalls = [ #synonims
    ["open"     ,"o","op","A"], 
    ["execve"   ,"e","A"] ,
    ["unlink"   ,"u","A"],
    ["unlinkat" ,"u","A"],
    ["stat" ,"s","A"]
]

gtable = {}
for e in syscalls:
    gtable[e[0]] = []
# gtable = {
#     "open":[],
#     "execve":[]
#     ...
# }

tcalls = []

def defa(h,k,d):                # default
    if h.get(k) == None:
        h[k] = d
  
def inform(k):
    h = {"nocall":"I can't find call decription."}

    f = h.get(k)
    if f == None:
        exit(-2)
    print(h[k])
    exit(-1)

def add_call(coml):
    global gtable
    global syscalls
    
    t = gtable
    h = {}
    if len(coml) == 2:
        for k in gtable.keys():
            defa(h,k,[])
            h[k] += [coml]
        return h
    
    if len(coml) == 3:
        coms = coml[0].split('+')
        for com in coms:
            for cl in syscalls:
                if com in cl:
                    defa(h,cl[0],[])
                    h[cl[0]] += [coml[1:]]
       
    return h

def create_table(selem):         # string elem ent
    table = {}
    l = filter(lambda x: len(x) , selem.split(';') )
    for e in l:
        a = e.split(':')
        c = add_call(a)
        for k in c.keys():
            defa(table,k,[])
            table[k] += c[k]

    return table

def findinfo(l):
    i, m = [0,len(l)]
    
    while(i < m):
        if l[i][0] == '-':
            i += 2
        else:
            r= i if (i<m) else -1
            return r

def main():
    global tcalls
    global lfunc
    a = sys.argv
    # print(a)
    pos = findinfo(a[1:])

    if pos < 0:
        inform("nocall")

    tcalls = create_table(a[1+pos])
    tcallscode = {}
    
    for fn in tcalls.keys():
        nfn = 'gen_'+fn
        if nfn in lfunc.keys():
            tcallscode[fn] = lfunc[nfn](tcalls[fn])
      
    res = "" + \
    header() + \
    statics() + \
    ''.join(map(lambda x: "\nextern \"C\" "+x,tcallscode.values()))

    return res
   
    # print(tcallscode)
    # print(tcalls)

def gen_static(ret,fname,args):
    stat = """
    static RETURN (*old_FNAME)(ARGS);"""
    stat = stat.replace("RETURN",ret)
    stat = stat.replace("FNAME",fname)
    stat = stat.replace("ARGS",args)

    return stat
    
def gen_t0(ret,fname,args,args_res,genstat=True):
    global fstatic
    if genstat:
        fstatic += [gen_static(ret,fname,args)]

    code = """
    RETURN_TYPE FNAME (ARGS_MAIN){
      old_FNAME = dlsym(RTLD_NEXT, \"SYSCALL\");
      P("FNAME hook\\n");
      BODY
      R old_FNAME(ARGS_RES);
    }
    """
    code = code.replace("RETURN_TYPE",ret)
    code = code.replace("FNAME",fname)
    code = code.replace("SYSCALL",fname)
    code = code.replace("ARGS_MAIN",args)
    code = code.replace("ARGS_RES",args_res)

    return code



def gen_mapstring(mapvar,files,patharg):
    code = ""
    code += "" +mapvar+"["+patharg+"]="+patharg+";\n      ";
    for fdual in files:
        fold,fnew = fdual
        code += "" +mapvar+"[\""+fold+"\"]=\""+fnew+"\";\n      ";
    return code
    
    

def gen_tfiles0(files):
    code = """
      MAP files;
      PULL_FILES
      S newpath = files[S(PATH)]; 
    """
    code = code.replace("PATH","p")
    code = code.replace("PULL_FILES", gen_mapstring("files",files,"p"))

    return code
    

def gen_open(files):                 #1 ! syscall
    code = gen_t0("I", "open",
                  "const C *p, I flags, mode_t mode",
                  "newpath.c_str(), flags, mode")
    return code.replace("BODY",gen_tfiles0(files))


def gen_execve(files):               #2 ! sc
    code = gen_t0("I", "execve",
                  "const C *p, C *const argv[], C *const envp[]",
                  "newpath.c_str(), argv, envp")
    return code.replace("BODY",gen_tfiles0(files))

def gen_unlinkat(files):             #3 ! sc
    code = gen_t0("I", "unlinkat",
                  "I dirfd, const C *p, int flags",
                  "dirfd, newpath.c_str(), flags")
    return code.replace("BODY",gen_tfiles0(files))


def gen_unlink(files):               #4 ! sc
    code = gen_t0("I", "unlink",
                  "const C *p",
                  "newpath.c_str()")
    return code.replace("BODY",gen_tfiles0(files))

def gen_stat(files):               #4 ! sc
    code = gen_t0("I", "stat",
                  "const C *p, struct stat *buf",
                  "3, newpath.c_str(), buf")
    return code.replace("BODY",gen_tfiles0(files))


def header():
    return """
    #include <sys/types.h>
    #include <dlfcn.h>
    #include <stdio.h>
    #include <map>
    #include <string>

    #define I int
    #define C char
    #define S string
    #define P printf
    #define R return
    
    using std::map;
    using std::string;
    typedef map<S,S> MAP;
    """

fstatic = [];
def statics():
    global fstatic
    return ''.join(fstatic)+"\n\n    "


lfunc = locals()

usage = """
usage: %prog [options] arg1 arg2"
"""
parser = OptionParser(usage)
parser.add_option("-f", "--file", dest="filename",
                  help="write code to FILE", default=None)
parser.add_option("-c", "--conf", dest="config",
                  help="use config file instead of ARGV", default=None)


(options, args) = parser.parse_args()

if __name__ == "__main__" :    
    code = main()
    if (options.filename != None):
        open(options.filename,"w").write(code)
    else:
        print(code)
    



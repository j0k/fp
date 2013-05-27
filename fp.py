#!/usr/bin/env python

import sys,os
import subprocess
import json
from optparse import OptionParser
from getpass import getuser
from subprocess import call
from hashlib import md5

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

modifiers = { #modif f -> path shorting
    "f":["norm"], # => fuppath
    "F":["norm_abs"]
}

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
    global modifiers
    
    t = gtable
    h = {}
    if len(coml) == 2:
        for k in gtable.keys():
            defa(h,k,[])
            h[k] += [coml]
        return h

    if len(coml) == 3:
        coms = coml[0].split('+')
        smods = list(set(map(lambda x: x[0],modifiers.keys())).intersection(coms))
        
        for com in coms:
            for cl in syscalls:
                if com in cl:
                    defa(h,cl[0],[])
                    h[cl[0]] += [[{'mod':smods}] + coml[1:] ]

    return h

def create_table(selem):         # string elem ent
    table = {}
    for elem in selem:
        l = filter(lambda x: len(x) , elem.split(';') )
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

def read_config(c):
    fc = open(c,"r")
    conf = fc.readlines()
    conf = filter(lambda x:len(x)>0 and (x[0] not in ['#',';']), conf)
    conf = map(lambda x: x.rstrip(), conf)
    fc.close()
    return conf

def main(confstr):
    global tcalls
    global lfunc
    global options

    if (confstr !=None):
        conf = [confstr]
    else:
        conf = read_config(options.config)
        
    tcalls = create_table(conf)
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

def gen_mapstring(mapvar,files,patharg,fuppath):
    code = ""
    # code += "" +mapvar+"["+patharg+"]="+patharg+";\n      ";
    code += "" +mapvar+"["+fuppath+"(PA("+patharg+"))]="+fuppath+"(PA("+patharg+"));\n      ";
    
    for fdual in files:
        fold,fnew = fdual[1:]
        code += "" +mapvar+"[\""+fold+"\"]=\""+fnew+"\";\n      ";
    return code
  

def extract_fuppath(fuppath, mods):
    global modifiers

    pathm = list ( set(mods["mod"]).intersection(["f","F"]))
    if len(pathm) > 0:
        return modifiers[pathm[0]][0]        
    return fuppath



def gen_tfiles0(files,fuppath="pathS"):
    code = """
      MAP files;
      PULL_FILES
      S newpath = files[UPDATE(PA(PATH))]; 
    """
    fuppath = extract_fuppath(fuppath,files[0][0])
    code = code.replace("UPDATE",fuppath)
    code = code.replace("PATH","p")
    code = code.replace("PULL_FILES", gen_mapstring("files",files,"p",fuppath))

    return code
    

def gen_open(files):                 #1 ! syscall
    code = gen_t0("I", "open",
                  "const C *p, I flags, mode_t mode",
                  "newpath.c_str(), flags, mode")
    return code.replace("BODY",gen_tfiles0(files))

def gen_fopen(files):                 #1 ! syscall
    code = gen_t0("I", "fopen",
                  "const C *p, const C * mode",
                  "newpath.c_str(), mode")
    return code.replace("BODY",gen_tfiles0(files))

def gen_fopen64(files):                 #1 ! syscall
    code = gen_t0("I", "fopen64",
                  "const C *p, const C * mode",
                  "newpath.c_str(), mode")
    return code.replace("BODY",gen_tfiles0(files))

def gen_freopen(files):                 #1 ! syscall
    code = gen_t0("I", "freopen",
                  "const C *p, const C * mode, _IO_FILE * file",
                  "newpath.c_str(), mode, file")
    return code.replace("BODY",gen_tfiles0(files))

def gen_freopen64(files):                 #1 ! syscall
    code = gen_t0("I", "freopen64",
                  "const C *p, const C * mode, _IO_FILE * file",
                  "newpath.c_str(), mode, file")
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

def gen_opendir(files):               #4 ! sc
    code = gen_t0("I", "opendir",
                  "const C *p, mode_t mode ",
                  "newpath.c_str(), mode")
    return code.replace("BODY",gen_tfiles0(files))

def gen_mkdir(files):               #4 ! sc
    code = gen_t0("I", "mkdir",
                  "const C *p",
                  "newpath.c_str()")
    return code.replace("BODY",gen_tfiles0(files))


def gen_rmdir(files):               #4 ! sc
    code = gen_t0("I", "rmdir",
                  "const C *p",
                  "newpath.c_str()")
    return code.replace("BODY",gen_tfiles0(files))


def gen_stat(files):               #4 ! sc
    code = gen_t0("I", "stat",
                  "const C *p, struct stat *buf",
                  "newpath.c_str(), buf")
    return code.replace("BODY",gen_tfiles0(files))

def gen_lstat(files):               
    code = gen_t0("I", "lstat",
                  "const C *p, struct stat *buf",
                  "newpath.c_str(), buf")
    return code.replace("BODY",gen_tfiles0(files))

def gen_lstat64(files):               
    code = gen_t0("I", "lstat64",
                  "const C *p, struct stat64 *buf",
                  "newpath.c_str(), buf")
    return code.replace("BODY",gen_tfiles0(files))

def gen___lxstat(files):               
    code = gen_t0("I", "__lxstat",
                  "I ver, const C *p, struct stat *buf",
                  "ver, newpath.c_str(), buf")
    return code.replace("BODY",gen_tfiles0(files))

def gen___lxstat64(files):               
    code = gen_t0("I", "__lxstat64",
                  "I ver,const C *p, struct stat64 *buf",
                  "ver, newpath.c_str(), buf")
    return code.replace("BODY",gen_tfiles0(files))

def gen_stat64(files):               
    code = gen_t0("I", "stat64",
                  "const C *p, struct stat64 *buf",
                  "newpath.c_str(), buf")
    return code.replace("BODY",gen_tfiles0(files))

def gen___xstat(files):               
    code = gen_t0("I", "__xstat",
                  "I ver, const C *p, struct stat *buf",
                  "ver, newpath.c_str(), buf")
    return code.replace("BODY",gen_tfiles0(files))

def gen___xstat64(files):               
    code = gen_t0("I", "__xstat64",
                  "I ver, const C *p, struct stat64 *buf",
                  "ver, newpath.c_str(), buf")
    return code.replace("BODY",gen_tfiles0(files))

def gen___fxstatat(files):
    #__fxstatat (int vers, int fd, const char *filename, struct stat *buf, int flag)

    code = gen_t0("I", "__fxstatat",
                  "I ver, I fd, const C *p, struct stat *buf, I flag",
                  "ver, fd, newpath.c_str(), buf, flag")
    return code.replace("BODY",gen_tfiles0(files))


configuration = ""
def header():
    global options
    global congiration
    head = """
    // FILE_PRELOAD template"""+"\n"+ \
        configuration + \
    """
    #include <sys/types.h>
    #include <libio.h> // FILE = struct _IO_FILE
    #include <dlfcn.h>
    //#include <stdio.h>
    #include <map>
    #include <string>

    #include <boost/filesystem/operations.hpp>
    #include <boost/utility.hpp>

    #define I int
    #define C char
    #define S string
    #define P_P_P_P_P old_printf
    #define R return
    
    using std::map;
    using std::string;
    typedef map<S,S> MAP;

    using boost::next;
    namespace bf = boost::filesystem;
 
    S norm(bf::path p){
      bf::path np;
      for (bf::path::iterator it = p.begin(); it != p.end(); it++){
        if (*it == "."){}
        else if (((*it != "..") && (*it != "."))
                 && *(next(it)) == ".." ){it++;}
        else { np /= *it; } 
      }
      R np.string();
    }

    S norm_abs(bf::path p){
      R bf::canonical(p).string();
    }

    bf::path PA(S s ){bf::path p = s; R p;}

    S pathS(bf::path p){R p.string();}

    static I (*old_printf)(const C* f) = dlsym(RTLD_NEXT, "printf");
    """
    return head.replace("P_P_P_P_P",{True:"P",False:"P //"}[options.printsyscalls])

fstatic = [];
def statics():
    global fstatic
    return ''.join(fstatic)+"\n\n    "


lfunc = locals()

usage = """
usage: %prog [options] -- progname arg1 arg2 ..."

example: 
 %prog -C "a:/etc/passwd:/etc/fstab" -- cat /etc/passwd
 %prog -C "a+f:/tmp:/etc;a+f:/boot:/etc" -- ls -al /tmp /boot
"""
user = getuser()
tmpdir = "/tmp/"+user+"/FILE_PRELOAD/"
parser = OptionParser(usage)
parser.add_option("-f", "--file", dest="filename",
                  help="write code to FILE", default=None)
parser.add_option("-c", "--conf", dest="config",
                  help="use config file instead of ARGV", default=None)
parser.add_option("-C", "--confstr", dest="configstr",
                  help="use config line", default=None)
parser.add_option("-t", "--tmpdir", dest="tmpdir",
                  help="use TMP_DIR for tmp files", default=tmpdir)
parser.add_option("-u", "--usetmpdir", dest="usetmpdir",
                  help="use or not TMP_DIR", default=None)
parser.add_option("-d", "--debug", dest="debugout",
                  help="use any to see stdout", default=None)
parser.add_option("-p", "--print", dest="printc",
                  action="store_true", help="print code", default=False)
parser.add_option("-s", "--printsyscalls", dest="printsyscalls",
                  action="store_true", help="print syscalls", default=False)
parser.add_option("-v", "--verbose",
                  action="store_true", dest="verbose", default=True,
                  help="make lots of noise [default]")
(options, args) = parser.parse_args()

def push_config_section(options, conf):
    global configuration
    
    configuration = ''.join( \
             map(lambda x: "    // options: "  + x + "\n",[options]) + \
             map(lambda x: "    // config : "  + x + "\n",conf))

def create_tmp():
    global options

    td_m = options.tmpdir
    td_so = td_m + "so"
    td_cpp = td_m + "cpp"
    def createD(p):
        if not os.path.exists(p): os.makedirs(p)

    map(createD,[td_m,td_so,td_cpp])

def read_md5():
    p = options.tmpdir+"confs.md5";
    j = {}
    if os.path.exists(p):
        f = open(p,"r")
        data = ''.join(f.readlines()).rstrip()
        j = json.loads(data) if len(data)>0 else {}
        f.close()
    return j
    
def dump_md5(confs):
    p = options.tmpdir+"confs.md5";
    #if not os.path.exists(p):
    f = open(p,"w")
    f.write(json.dumps(confs,sort_keys=True, indent=4, separators=(',', ': ')))
    f.close()

def choose_hash(conf,h):
    return None

def hashit(s):
    d = s;
    if type(s) == list:
        d = ''.join(s);
    return md5(d).hexdigest()[:10]

def compile_file(f):
    subprocess.Popen(["make"],stdout=stdout,stderr=stderr).communicate()[0]

# sorry, this code section needs rlly refactoring & simplifing
if __name__ == "__main__" : 
    stderr=subprocess.STDOUT
    stdout=sys.stdout
    create_tmp()

    if options.debugout == None:
        devnull = open(os.devnull, 'w')
        stderr,stdout = devnull,devnull
    
    #sys.stdout = stdout
    conf = [options.configstr] if (options.config==None ) else read_config(options.config)
    push_config_section(str(options), conf)
    confs = read_md5()
    preload = None 

    hash = hashit([str(options)]+ conf)
    confs[hash] = preload = options.tmpdir + "so/" + hash + ".so"
    dump_md5(confs)

    if preload == None or not os.path.exists(preload):
        def compile_file(fin, fout_o, fout_so):
            subprocess.Popen("gcc -w -fpermissive -fPIC -c -Wall -O3".split() + \
                              [fin,"-o",fout_o],
                             stdout=stdout,stderr=stderr).communicate()[0]
            subprocess.Popen(["gcc","-shared",fout_o,"-ldl","-lstdc++",
                              "-lboost_filesystem","-o",fout_so],
                             stdout=stdout,stderr=stderr).communicate()[0]

        code  = main(options.configstr)
        filec = options.tmpdir + "cpp/" + hash +".cpp"
        if options.filename != None:
            filec = options.filename
        fcode = open(filec, "w")
        fcode.write(code)
        fcode.close();

        if (options.filename != None):
            open(options.filename,"w").write(code) # tmpdir
        if (options.printc == True):
            print(code)
        open(filec,"w").write(code)

        compile_file(filec, preload[:-3]+".o", preload) 
        

    if len(args) >= 1:
        os.environ['LD_PRELOAD'] = preload
        os.system(' '.join(args))



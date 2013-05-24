
    #include <stdio.h>

    #define I int
    #define C char
    #define P printf
    
    
    I open (const C *pathname, I flags, mode_t mode){
      old_open = dlsym(RTLD_NEXT, SYSCALL);
      P("open hook");
      
    
      return old_open(newpath, mode);
    }
    
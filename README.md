fp
==

File Preload like LD_PRELOAD

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

            $: FILE_PRELOAD "execve+open+stat:/usr/bin/program_B:/usr/bin/program_B.old" bash
      (new) $: ./program_C
      	or
	    $: FILE_PRELOAD "execve+open+stat:/usr/bin/program_B:/usr/bin/program_B.old" ./program_C
    
    (other) $: ./program_A   

 
======================
end of the story

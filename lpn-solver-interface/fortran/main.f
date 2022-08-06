
      program main

      real*8 time_step, time
      real*8 solution(100)

      integer block_id, i

      character(len=80) lpn_library
      character(len=80) lpn_file

      ! Set the LPN interface library.
      !
      lpn_library = 
     +  "/Users/Shared/svzerod/lib/libsvzero_interface_library.dylib"//
     +  achar(0)

      call lpn_interface_init(lpn_library)

      lpn_file = "steadyFlow_RC_R.json"//achar(0)
      time_step = 0.01

      call lpn_interface_add_block(lpn_file, time_step, block_id)

      time = 0.0
      do i = 1, 100
        call lpn_interface_get_solution(block_id, time, solution)
        write(*,*) "time: ", time, " solution: ", solution(1), 
     +       solution(2), solution(3), solution(4), solution(5)
        time = time + time_step
      end do

      end

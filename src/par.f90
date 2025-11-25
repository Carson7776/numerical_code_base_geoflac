! -*- F90 -*-

program DREZINA
!$ACC routine(marker2elem) gang
use arrays
use params
use marker_data

character*200 inputfile
real*4 secnds,time0
integer :: narg, iargc, j,irestart, kk, fsave, lstime
double precision :: dtacc_file, dtacc_save, dtacc_screen, fl, fr, ringforce, vl, vr, dl, sxxd, sxx, stressI
integer, parameter :: isize = 20
real :: ring(isize)

narg = iargc()
if(narg /= 1) then
    write(*,*) 'usage: flac inputfile'
    stop 1
endif
call getarg(1, inputfile)

open( 333, file='output.asc' )

time0 = secnds(0.0)

! Read task parameters
call read_params(inputfile)
call allocate_arrays(nz, nx, nphase)
call allocate_markers(nz, nx)

! Try to read save-file contents. If file exist - restart, othewise - new start
open(1,file='_contents.rs',status='old',err=10)

irestart = 1
close(1)
goto 20

10 irestart = 0

20 continue

if ( irestart .eq. 1 ) then  !file exists - restart
    call rsflac
    if( dtout_screen .ne. 0 ) then
        write(6,*) 'you CONTINUE from  ', nloop, ' step'
    else
        call SysMsg('you CONTINUE the execution')
    endif
else ! file does not exist - new start
    if( dtout_screen .ne. 0 ) then
        write(6,*) 'you have NEW start conditions'
        write(333,*) 'you have NEW start conditions'
    else
        call SysMsg('you have NEW start conditions')
    endif
    call setflac
    ! Output of initial configuration
    call outflac
    call outmarker
end if 

!      ****************** running ********************************
dtacc_screen = 0
dtacc_file = 0
dtacc_save = 0
lstime = 500

do while( time .le. time_max )
  if( dtout_screen .ne. 0 ) then
    if( dtacc_screen .gt. dtout_screen ) then
       write(*,'(I10,A,F7.3,A,F8.1,A)') nloop,'''s step. Time[My]=', time/sec_year/1.d+6, &
                ',  elapsed sec-', secnds(time0)
       write(333,'(I10,A,F7.3,A,F8.1,A)') nloop,'''s step. Time[My]=', time/sec_year/1.d+6, &
                ',  elapsed sec-', secnds(time0)
       dtacc_screen = 0
    endif
  endif
  ! forces at the boundaries
  if (io_forc==1 .and.  mod(nloop, 1000)==0) then
          fl = 0.d0
          fr = 0.d0
          !$ACC parallel loop reduction(+:fl, fr) async(1)
    do j = 1, nz-1
      sxx = 0.25d0*(stress0(j,1,1,1)+stress0(j,1,1,2)+stress0(j,1,1,3)+stress0(j,1,1,4))
      sxxd = sxx-stressI(j,1)
      dl = cord(j+1,1,2)-cord(j,1,2)
      fl = fl + sxxd*(-dl)

      sxx = 0.25*(stress0(j,nx-1,1,1)+stress0(j,nx-1,1,2)+stress0(j,nx-1,1,3)+stress0(j,nx-1,1,4))
      sxxd = sxx-stressI(j,nx-1)
      dl = cord(j+1,nx-1,2)-cord(j,nx-1,2)
      fr = fr + sxxd*(-dl)
    end do
    !$ACC wait(1)
    force_l = (-fl)
    force_r = (-fr)
    fsave = nloop/1000
    !$ACC parallel loop async(1)
    do kk = 1, isize
     if (mod(fsave,isize) == kk-1) then
        ring(kk) = -(-fl)
        ringforce = (sum(ring(:))/isize)
        exit
     end if
    end do
    !$ACC wait (1)
    vl = vel(1,1,1)
    vr = vel(1,nx,1)
    open(1, file = 'forc.0', position = 'append')
    write(1,'(i10,1x,f7.3,1x,e10.3,1x,e10.3,1x,e10.3,1x,e10.3,1x,e10.3,1x,i10,1x,e10.3)') &
    nloop,time/sec_year/1.d6, force_l, force_r,ringforce, vl, vr, nloop-lstime,limit_force
    close(1)
    if (itype_force ==1 .and.abs(ringforce).gt.limit_force .and. abs(nloop-lstime).gt.10000) then
       lstime = nloop
       !$ACC parallel loop async(1)
     do j = 1,nz
        bc(j,1,1) = decf*bc(j,1,1)
        bc(j,nx,1) = decf*bc(j,nx,1)
     end do
    end if
    if (itype_force == 1.and. abs(nloop_lstime).gt.1000000) then
     lstime = nloop
     !$ACC parallel loop asysnc(1)
     do j = 1, nz
      bc(j,1,1) = incf*bc(j,1,1)
      bc(j,nx,1) = incf*bc(j,nx,1)
     end do
    end if
  end if

  do j = 1, ntest_rem
    ! FLAC
    call flac

    nloop = nloop + 1
    time = time + dt
    !$ACC update device(time,nloop) async(1)
    dtacc_screen = dtacc_screen + dt
    dtacc_file   = dtacc_file   + dt
    dtacc_save   = dtacc_save   + dt
  end do

  ! Remeshing
  if( ny_rem.eq.1 .and. itherm.ne.2 ) then
    call itest_mesh(need_remeshing)
    if( need_remeshing .ne. 0 ) then
      ! If there are markers recalculate their x,y global coordinate and assign them aps, eII, press, temp
      call bar2euler
      call remesh
      ! If markers are present recalculate a1,a2 local coordinates and assign elements with phase ratio vector
      call lpeuler2bar
      !$ACC parallel async(1)
      call marker2elem
      !$ACC end parallel
      !$ACC update self(nmarkers) async(1)
    endif
  endif

    ! OUTPUT  
  !$ACC wait
  if( dtout_file .ne. 0 ) then 
    if( dtacc_file .gt. dtout_file ) then
      call outflac
      call outmarker
      dtacc_file = 0
    endif
  endif
  ! SAVING the restart information
  if( dtsave_file .ne. 0 ) then 
    if( dtacc_save .gt. dtsave_file ) then
      call saveflac
      dtacc_save = 0
    endif
  endif

end do

! SAVING the restart information of last step
call saveflac

close(333)

call SysMsg('Congratulations !')
end program DREZINA

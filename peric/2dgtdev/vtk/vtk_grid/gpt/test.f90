module test_write_vts
  use pfunit
  implicit none
contains

  @test
  subroutine test_small_grid()
    implicit none

    integer, parameter :: NI=2, NJ=2, NK=1
    real :: X(NI,NJ,NK), Y(NI,NJ,NK), Z(NI,NJ,NK)

    ! Simple square grid
    X(:,:,1) = reshape([0.0,1.0, 0.0,1.0], [NI,NJ])
    Y(:,:,1) = reshape([0.0,0.0, 1.0,1.0], [NI,NJ])
    Z(:,:,1) = 0.0

    call write_vts('test.vts', X, Y, Z, NI, NJ, NK)

    call assertTrue(file_exists('test.vts'))

  end subroutine test_small_grid

  @test
  subroutine test_coordinates_written()
    implicit none

    integer, parameter :: NI=2, NJ=1, NK=1
    real :: X(NI,NJ,NK), Y(NI,NJ,NK), Z(NI,NJ,NK)
    character(len=256) :: line
    integer :: unit

    X(:,:,1) = reshape([0.0, 2.0], [NI,NJ])
    Y(:,:,1) = 0.0
    Z(:,:,1) = 0.0

    call write_vts('test_coords.vts', X, Y, Z, NI, NJ, NK)

    open(unit=10, file='test_coords.vts', status='old')

    ! Scan file for coordinate value
    do
      read(10,'(A)',end=100) line
      if (index(line, '2.00000000E+00') > 0) then
        call assertTrue(.true.)
        close(10)
        return
      end if
    end do

100 continue
    close(10)
    call assertTrue(.false.)

  end subroutine test_coordinates_written

end module test_write_vts

logical function file_exists(fname)
  implicit none
  character(len=*), intent(in) :: fname
  inquire(file=fname, exist=file_exists)
end function file_exists
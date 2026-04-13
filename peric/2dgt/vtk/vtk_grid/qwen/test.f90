module test_vts_writer
  use pfunit
  use vts_writer
  implicit none
contains

  @test
  subroutine test_vts_creation_and_structure()
    character(len=*), parameter :: fname = 'test_grid'
    integer, parameter :: nx=2, ny=2, nz=2
    real(kind=real64) :: x(nx,ny,nz), y(nx,ny,nz), z(nx,ny,nz)
    integer :: i, j, k, iunit, iostat
    character(len=256) :: line
    logical :: has_extent, has_points_end, has_vtk_end
    integer :: n_data_lines
    real(kind=real64) :: rx, ry, rz

    ! Setup a simple 2x2x2 grid
    do k=1,nz
      do j=1,ny
        do i=1,nx
          x(i,j,k) = dble(i-1)
          y(i,j,k) = dble(j-1)
          z(i,j,k) = dble(k-1)
        end do
      end do
    end do

    call write_vts(fname, x, y, z, nx, ny, nz)

    ! Verify file contents
    has_extent = .false.
    has_points_end = .false.
    has_vtk_end = .false.
    n_data_lines = 0

    open(newunit=iunit, file=trim(fname)//'.vts', status='old', action='read')
    do
      read(iunit, '(A)', iostat=iostat) line
      if (iostat /= 0) exit

      if (index(line, 'WholeExtent="0 1 0 1 0 1"') > 0) has_extent = .true.
      if (index(line, '</DataArray>') > 0) has_points_end = .true.
      if (index(line, '</VTKFile>') > 0) has_vtk_end = .true.

      ! Count pure data lines (skip XML tags and comments)
      if (scan(line, '0123456789.') > 0 .and. &
          index(line, 'DataArray') == 0 .and. &
          index(line, 'StructuredGrid') == 0 .and. &
          index(line, 'Piece') == 0 .and. &
          index(line, 'Points') == 0 .and. &
          index(line, 'xml') == 0 .and. &
          index(line, 'VTKFile') == 0) then
        n_data_lines = n_data_lines + 1
        if (n_data_lines == 1) then
          read(line, *) rx, ry, rz
          @assertEqual(0.0d0, rx, relTol=1.0d-12, msg='First point x')
          @assertEqual(0.0d0, ry, relTol=1.0d-12, msg='First point y')
          @assertEqual(0.0d0, rz, relTol=1.0d-12, msg='First point z')
        end if
      end if
    end do
    close(iunit)

    @assertTrue(has_extent, msg='WholeExtent tag missing or incorrect')
    @assertTrue(has_points_end, msg='Points DataArray not properly closed')
    @assertTrue(has_vtk_end, msg='VTKFile closing tag missing')
    @assertEqual(nx*ny*nz, n_data_lines, msg='Point count mismatch')
  end subroutine test_vts_creation_and_structure

  @test
  subroutine test_vts_invalid_dimensions()
    integer :: stat
    real(kind=real64) :: dummy(1,1,1)
    
    call write_vts('bad', dummy, dummy, dummy, 0, 1, 1, status=stat)
    @assertEqual(1, stat, msg='Should return error status for nx=0')
    
    call write_vts('bad', dummy, dummy, dummy, 1, 0, 1, status=stat)
    @assertEqual(1, stat, msg='Should return error status for ny=0')
  end subroutine test_vts_invalid_dimensions

end module test_vts_writer
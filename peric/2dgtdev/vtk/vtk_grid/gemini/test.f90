module test_vtk_export
  use pfunit_mod
  use vtk_export_mod
  implicit none

contains

  @test
  subroutine test_write_vts_creates_file()
    character(len=30)  :: filename = 'test_mock_grid.vts'
    integer, parameter :: ni = 3, nj = 2
    real               :: x(ni*nj), y(ni*nj)
    integer            :: i, j, ij
    logical            :: file_exists
    character(len=256) :: line
    integer            :: unit_num, io_status
    logical            :: found_extent_tag

    ! 1. Setup mock grid data mimicking grid.f 1D allocation
    do j = 1, nj
      do i = 1, ni
        ij = (i - 1) * nj + j
        x(ij) = real(i)
        y(ij) = real(j)
      end do
    end do

    ! 2. Execute the VTS export subroutine
    call write_vts(filename, ni, nj, x, y)

    ! 3. Assert file creation
    inquire(file=filename, exist=file_exists)
    @assertTrue(file_exists, 'The VTS file should be created.')

    ! 4. Verify contents: Check if the WholeExtent tag is correctly formatted
    found_extent_tag = .false.
    open(newunit=unit_num, file=filename, status='old', iostat=io_status)
    @assertEqual(0, io_status, 'Should be able to open the generated VTS file.')

    do while (io_status == 0)
      read(unit_num, '(A)', iostat=io_status) line
      if (index(line, 'WholeExtent="1 3 1 2 1 1"') > 0) then
        found_extent_tag = .true.
        exit
      end if
    end do
    close(unit_num)

    @assertTrue(found_extent_tag, 'File should contain the correct StructuredGrid Extent tag.')

    ! 5. Teardown: Clean up the generated file
    open(newunit=unit_num, file=filename)
    close(unit_num, status='delete')

  end subroutine test_write_vts_creates_file

end module test_vtk_export

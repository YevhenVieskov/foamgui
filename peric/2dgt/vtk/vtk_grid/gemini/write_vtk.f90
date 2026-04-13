module vtk_export_mod
  implicit none

contains

  !=============================================================================
  ! Writes 2D grid coordinates to a VTK XML Structured Grid (.vts) file.
  !=============================================================================
  subroutine write_vts(filename, ni, nj, x, y)
    character(len=*), intent(in) :: filename
    integer, intent(in)          :: ni, nj
    real, intent(in)             :: x(*), y(*)

    integer :: i, j, ij, unit_num, io_status

    open(newunit=unit_num, file=trim(filename), status='replace', iostat=io_status)
    if (io_status /= 0) then
      print *, 'ERROR: Could not open file for VTS export: ', trim(filename)
      return
    end if

    ! Write VTK XML Headers
    write(unit_num, '(A)') '<?xml version="1.0"?>'
    write(unit_num, '(A)') '<VTKFile type="StructuredGrid" version="0.1" byte_order="LittleEndian">'
    write(unit_num, '(A,I0,A,I0,A)') '  <StructuredGrid WholeExtent="1 ', ni, ' 1 ', nj, ' 1 1">'
    write(unit_num, '(A,I0,A,I0,A)') '    <Piece Extent="1 ', ni, ' 1 ', nj, ' 1 1">'
    write(unit_num, '(A)') '      <Points>'
    write(unit_num, '(A)') '        <DataArray type="Float32" Name="Points" NumberOfComponents="3" format="ascii">'

    ! VTK expects points strictly sorted by X first, then Y, then Z.
    ! We recreate the 1D mapping (I-1)*NJ + J used in grid.f.
    do j = 1, nj
      do i = 1, ni
        ij = (i - 1) * nj + j
        write(unit_num, '(3(ES15.6,1X))') x(ij), y(ij), 0.0
      end do
    end do

    ! Write VTK XML Footers
    write(unit_num, '(A)') '        </DataArray>'
    write(unit_num, '(A)') '      </Points>'
    write(unit_num, '(A)') '    </Piece>'
    write(unit_num, '(A)') '  </StructuredGrid>'
    write(unit_num, '(A)') '</VTKFile>'

    close(unit_num)
  end subroutine write_vts

end module vtk_export_mod

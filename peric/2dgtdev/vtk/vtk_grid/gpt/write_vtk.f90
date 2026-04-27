subroutine write_vts(filename, X, Y, Z, NI, NJ, NK)
  implicit none
  character(len=*), intent(in) :: filename
  integer, intent(in) :: NI, NJ, NK
  real, intent(in) :: X(NI,NJ,NK), Y(NI,NJ,NK), Z(NI,NJ,NK)

  integer :: i, j, k
  integer :: unit

  unit = 99
  open(unit=unit, file=filename, status='replace', action='write', form='formatted')

  write(unit,'(A)') '<?xml version="1.0"?>'
  write(unit,'(A)') '<VTKFile type="StructuredGrid" version="0.1" byte_order="LittleEndian">'

  write(unit,'(A,I0,A,I0,A,I0,A)') '  <StructuredGrid WholeExtent="0 ', NI-1, ' 0 ', NJ-1, ' 0 ', NK-1, '">'
  write(unit,'(A,I0,A,I0,A,I0,A)') '    <Piece Extent="0 ', NI-1, ' 0 ', NJ-1, ' 0 ', NK-1, '">'

  write(unit,'(A)') '      <Points>'
  write(unit,'(A)') '        <DataArray type="Float32" NumberOfComponents="3" format="ascii">'

  do k = 1, NK
    do j = 1, NJ
      do i = 1, NI
        write(unit,'(3(ES16.8,1X))') X(i,j,k), Y(i,j,k), Z(i,j,k)
      end do
    end do
  end do

  write(unit,'(A)') '        </DataArray>'
  write(unit,'(A)') '      </Points>'

  write(unit,'(A)') '    </Piece>'
  write(unit,'(A)') '  </StructuredGrid>'
  write(unit,'(A)') '</VTKFile>'

  close(unit)

end subroutine write_vts
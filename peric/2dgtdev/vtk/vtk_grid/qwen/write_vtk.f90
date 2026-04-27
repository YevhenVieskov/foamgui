module vts_writer
  use iso_fortran_env, only: real64
  implicit none
  private
  public :: write_vts

contains

  !> Write a 3D structured grid to VTK XML StructuredGrid format (ASCII)
  subroutine write_vts(filename, x, y, z, nx, ny, nz, status)
    character(len=*), intent(in)  :: filename
    integer, intent(in)           :: nx, ny, nz
    real(kind=real64), intent(in) :: x(nx,ny,nz), y(nx,ny,nz), z(nx,ny,nz)
    integer, intent(out), optional :: status

    integer :: i, j, k, iunit, iostat, err

    err = 0
    if (nx < 1 .or. ny < 1 .or. nz < 1) then
      err = 1
      if (present(status)) status = err
      return
    end if

    open(newunit=iunit, file=trim(filename)//'.vts', status='replace', &
         action='write', iostat=iostat)
    if (iostat /= 0) then
      err = 2
      if (present(status)) status = err
      return
    end if

    ! VTK XML Header
    write(iunit, '(A)') '<?xml version="1.0"?>'
    write(iunit, '(A)') '<VTKFile type="StructuredGrid" version="0.1">'
    
    ! Extent is 0-indexed and inclusive: xmin xmax ymin ymax zmin zmax
    write(iunit, '(A,I0,A,I0,A,I0,A,I0,A,I0,A,I0,A)') &
      '  <StructuredGrid WholeExtent="0 ', nx-1, ' 0 ', ny-1, ' 0 ', nz-1, '">', &
      '    <Piece Extent="0 ', nx-1, ' 0 ', ny-1, ' 0 ', nz-1, '">', &
      '      <Points>'
      
    write(iunit, '(A)') '        <DataArray type="Float64" Name="Points" &
         &NumberOfComponents="3" format="ascii">'

    ! VTK expects points ordered with i varying fastest, then j, then k
    do k = 1, nz
      do j = 1, ny
        do i = 1, nx
          write(iunit, '(3ES22.14E3)') x(i,j,k), y(i,j,k), z(i,j,k)
        end do
      end do
    end do

    write(iunit, '(A)') '        </DataArray>'
    write(iunit, '(A)') '      </Points>'
    write(iunit, '(A)') '    </Piece>'
    write(iunit, '(A)') '  </StructuredGrid>'
    write(iunit, '(A)') '</VTKFile>'

    close(iunit)
    if (present(status)) status = err
  end subroutine write_vts

end module vts_writer
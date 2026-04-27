! =============================================================================
! pFUnit test suite for the VTK writer (save as e.g. test_vts_writer.pf)
! Requires pFUnit[](https://github.com/nasa/pFUnit) - preprocessed with pFUnit
! =============================================================================
module VTSWriterTests
  use pFUnit
  implicit none

  ! We assume the GRGEN include files and common blocks are available
  ! via the same INCLUDE statements used in grid.f.
  ! For a full integration the test would be linked against the compiled
  ! GRGEN objects.

contains

  ! ---------------------------------------------------------------------------
  ! Helper to create a minimal rectangular grid (unit square) for testing.
  ! Only the arrays needed by WRITVTS are filled.
  ! ---------------------------------------------------------------------------
  subroutine setupSimpleGrid(K, NI_in, NJ_in)
    integer, intent(in)  :: K, NI_in, NJ_in
    integer :: I, J, IJ, IST_local
    real    :: dx, dy

    ! Minimal setup compatible with GRGEN indexing
    include 'param.ing'   ! brings NXYA, etc.
    include 'indexg.ing'  ! brings LI, IGR, etc.
    include 'grid.ing'    ! brings X, Y, IST, NI, NJ, NIGR, NJGR

    NI  = NI_in
    NJ  = NJ_in
    NIGR(K) = NI
    NJGR(K) = NJ
    IGR(K)  = 0                     ! simplest case, single block
    IST     = IGR(K)

    ! Set LI pointers exactly as GRIDGN does
    do I = 1, NI
      LI(I + IST) = (I-1)*NJ
    end do

    ! Uniform Cartesian grid on unit square
    dx = 1.0 / real(NI-1)
    dy = 1.0 / real(NJ-1)
    do I = 1, NI
      do J = 1, NJ
        IJ = LI(I + IST) + J
        X(IJ) = real(I-1) * dx
        Y(IJ) = real(J-1) * dy
      end do
    end do
  end subroutine setupSimpleGrid

  ! ---------------------------------------------------------------------------
  @test
  subroutine testWriteVTS_SimpleGrid()
    character(len=32) :: filename = 'test_grid.vts'
    integer :: ios
    logical :: file_exists

    ! Create a tiny 3×4 point grid (2×3 cells)
    call setupSimpleGrid(1, 3, 4)

    ! Execute the writer
    call WRITVTS(1, filename)

    ! Basic assertions
    inquire(file=filename, exist=file_exists)
    @assertTrue (file_exists, 'VTK file was not created')

    ! Open and check that it contains the expected XML tags
    open(unit=20, file=filename, status='old', iostat=ios)
    @assertEqual (0, ios, 'Could not open generated VTK file')

    call checkVTSContent(20)
    close(20)

    ! Optional cleanup (comment out if you want to keep the file)
    ! call system('rm -f '//trim(filename))
  end subroutine testWriteVTS_SimpleGrid

  ! ---------------------------------------------------------------------------
  ! Helper that parses the first few lines of the VTK file for correctness
  ! ---------------------------------------------------------------------------
  subroutine checkVTSContent(unit)
    integer, intent(in) :: unit
    character(len=256) :: line
    integer :: i

    ! Header must start with XML declaration
    read(unit, '(A)') line
    @assertTrue (index(line, '<?xml') > 0, 'Missing XML declaration')

    ! Must contain StructuredGrid with correct extents for our 3×4 grid
    do i = 1, 20
      read(unit, '(A)', end=999) line
      if (index(line, 'WholeExtent="0 2 0 3 0 0"') > 0) then
        @assertTrue (.true.)
        return
      end if
    end do

999 continue
    @assertFalse (.true., 'Did not find correct WholeExtent="0 2 0 3 0 0"')
  end subroutine checkVTSContent

end module VTSWriterTests
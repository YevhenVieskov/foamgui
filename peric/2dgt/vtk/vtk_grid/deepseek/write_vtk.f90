!#############################################################
      SUBROUTINE WRITE_VTK_VTS(K, FILENAME)
!#############################################################
!     This routine writes the grid for level K in VTK XML
!     Structured Grid format (.vts file).
!=============================================================
      INCLUDE 'param.ing'
      INCLUDE 'indexg.ing'
      INCLUDE 'grid.ing'
      INCLUDE 'logico.ing'
      INCLUDE 'bound.ing'
      
      INTEGER, INTENT(IN) :: K
      CHARACTER(LEN=*), INTENT(IN) :: FILENAME
      
      INTEGER :: I, J, IJ, UNIT_NUM
      INTEGER :: NPOINTS, NCELLS
      CHARACTER(LEN=20) :: STR_NI, STR_NJ
      
      ! Set grid indices for level K
      CALL SETIND(K)
      
      NPOINTS = NI * NJ
      NCELLS = (NI - 1) * (NJ - 1)
      
      ! Open file for writing
      UNIT_NUM = 88
      OPEN(UNIT=UNIT_NUM, FILE=TRIM(FILENAME), STATUS='REPLACE')
      
      ! Write XML header
      WRITE(UNIT_NUM, '(A)') '<?xml version="1.0"?>'
      WRITE(UNIT_NUM, '(A)') '<VTKFile type="StructuredGrid" ' //
     &  'version="0.1" byte_order="LittleEndian">'
      WRITE(UNIT_NUM, '(A)') '  <StructuredGrid WholeExtent="' //
     &  '0 ' // TRIM(INT2STR(NI-1)) // ' ' //
     &  '0 ' // TRIM(INT2STR(NJ-1)) // ' ' //
     &  '0 0">'
      WRITE(UNIT_NUM, '(A,I0,A,I0,A)') 
     &  '    <Piece Extent="0 ', NI-1, ' 0 ', NJ-1, ' 0 0">'
      
      ! Write point coordinates
      WRITE(UNIT_NUM, '(A)') '      <Points>'
      WRITE(UNIT_NUM, '(A)') 
     &  '        <DataArray type="Float64" Name="Points" ' //
     &  'NumberOfComponents="3" format="ascii">'
      
      DO J = 1, NJ
        DO I = 1, NI
          IJ = LI(I + IST) + J
          ! For 2D grid, set Z=0 for all points
          WRITE(UNIT_NUM, '(3(ES16.8,1X))') X(IJ), Y(IJ), 0.0D0
        END DO
      END DO
      
      WRITE(UNIT_NUM, '(A)') '        </DataArray>'
      WRITE(UNIT_NUM, '(A)') '      </Points>'
      
      ! Write cell data (volumes, interpolation factors, etc.)
      WRITE(UNIT_NUM, '(A)') '      <CellData>'
      
      ! Cell volumes
      WRITE(UNIT_NUM, '(A)') 
     &  '        <DataArray type="Float64" Name="Volume" ' //
     &  'format="ascii">'
      DO J = 2, NJM
        DO I = 2, NIM
          IJ = LI(I + IST) + J
          WRITE(UNIT_NUM, '(ES16.8)') VOL(IJ)
        END DO
      END DO
      WRITE(UNIT_NUM, '(A)') '        </DataArray>'
      
      ! Interpolation factor FX
      WRITE(UNIT_NUM, '(A)') 
     &  '        <DataArray type="Float64" Name="FX" format="ascii">'
      DO J = 2, NJM
        DO I = 2, NIM
          IJ = LI(I + IST) + J
          WRITE(UNIT_NUM, '(ES16.8)') FX(IJ)
        END DO
      END DO
      WRITE(UNIT_NUM, '(A)') '        </DataArray>'
      
      ! Interpolation factor FY
      WRITE(UNIT_NUM, '(A)') 
     &  '        <DataArray type="Float64" Name="FY" format="ascii">'
      DO J = 2, NJM
        DO I = 2, NIM
          IJ = LI(I + IST) + J
          WRITE(UNIT_NUM, '(ES16.8)') FY(IJ)
        END DO
      END DO
      WRITE(UNIT_NUM, '(A)') '        </DataArray>'
      
      ! Cell center coordinates
      WRITE(UNIT_NUM, '(A)') 
     &  '        <DataArray type="Float64" Name="CellCenter" ' //
     &  'NumberOfComponents="2" format="ascii">'
      DO J = 2, NJM
        DO I = 2, NIM
          IJ = LI(I + IST) + J
          WRITE(UNIT_NUM, '(2(ES16.8,1X))') XC(IJ), YC(IJ)
        END DO
      END DO
      WRITE(UNIT_NUM, '(A)') '        </DataArray>'
      
      WRITE(UNIT_NUM, '(A)') '      </CellData>'
      
      ! Write point data (boundary indicators if needed)
      WRITE(UNIT_NUM, '(A)') '      <PointData>'
      WRITE(UNIT_NUM, '(A)') '      </PointData>'
      
      ! Close XML tags
      WRITE(UNIT_NUM, '(A)') '    </Piece>'
      WRITE(UNIT_NUM, '(A)') '  </StructuredGrid>'
      WRITE(UNIT_NUM, '(A)') '</VTKFile>'
      
      CLOSE(UNIT_NUM)
      
      WRITE(*,*) 'Grid level ', K, ' written to ', TRIM(FILENAME)
      WRITE(*,*) '  Dimensions: ', NI, ' x ', NJ
      WRITE(*,*) '  Points: ', NPOINTS, ', Cells: ', NCELLS
      
      RETURN
      
      CONTAINS
      
      ! Helper function to convert integer to string
      FUNCTION INT2STR(NUM) RESULT(STR)
        INTEGER, INTENT(IN) :: NUM
        CHARACTER(LEN=20) :: STR
        WRITE(STR, '(I0)') NUM
      END FUNCTION INT2STR
      
      END SUBROUTINE WRITE_VTK_VTS

!#############################################################
      SUBROUTINE WRITE_ALL_GRIDS_VTS(BASE_NAME)
!#############################################################
!     This routine writes all grid levels in VTK XML
!     Structured Grid format (.vts files).
!=============================================================
      INCLUDE 'param.ing'
      INCLUDE 'indexg.ing'
      INCLUDE 'grid.ing'
      
      CHARACTER(LEN=*), INTENT(IN) :: BASE_NAME
      CHARACTER(LEN=256) :: FILENAME
      INTEGER :: K
      
      DO K = 1, NGR
        WRITE(FILENAME, '(A,A,I0,A)') TRIM(BASE_NAME), '_level', K, '.vts'
        CALL WRITE_VTK_VTS(K, FILENAME)
      END DO
      
      END SUBROUTINE WRITE_ALL_GRIDS_VTS

!#############################################################
      SUBROUTINE WRITE_VTK_VTS_WITH_BC(K, FILENAME)
!#############################################################
!     This routine writes the grid with boundary condition
!     markers as cell data.
!=============================================================
      INCLUDE 'param.ing'
      INCLUDE 'indexg.ing'
      INCLUDE 'grid.ing'
      INCLUDE 'bound.ing'
      INCLUDE 'lines.ing'
      
      INTEGER, INTENT(IN) :: K
      CHARACTER(LEN=*), INTENT(IN) :: FILENAME
      
      INTEGER :: I, J, IJ, UNIT_NUM
      INTEGER :: BC_TYPE
      INTEGER, ALLOCATABLE :: CELL_BC(:)
      
      ! Set grid indices for level K
      CALL SETIND(K)
      
      ! Allocate array for cell boundary markers
      ALLOCATE(CELL_BC(NIJA))
      CELL_BC = 0
      
      ! Mark boundary cells based on ITB and JTB arrays
      ! South boundary
      DO I = 2, NIM
        BC_TYPE = ITB(1, I + IST)
        IF (BC_TYPE .GT. 0) THEN
          IJ = LI(I + IST) + 2
          CELL_BC(IJ) = BC_TYPE
        END IF
      END DO
      
      ! North boundary
      DO I = 2, NIM
        BC_TYPE = ITB(2, I + IST)
        IF (BC_TYPE .GT. 0) THEN
          IJ = LI(I + IST) + NJM
          CELL_BC(IJ) = BC_TYPE
        END IF
      END DO
      
      ! West boundary
      DO J = 2, NJM
        BC_TYPE = JTB(1, J + JST)
        IF (BC_TYPE .GT. 0) THEN
          IJ = LI(2 + IST) + J
          CELL_BC(IJ) = BC_TYPE
        END IF
      END DO
      
      ! East boundary
      DO J = 2, NJM
        BC_TYPE = JTB(2, J + JST)
        IF (BC_TYPE .GT. 0) THEN
          IJ = LI(NIM + IST) + J
          CELL_BC(IJ) = BC_TYPE
        END IF
      END DO
      
      ! Open file and write VTK XML (similar to above but with BC data)
      UNIT_NUM = 88
      OPEN(UNIT=UNIT_NUM, FILE=TRIM(FILENAME), STATUS='REPLACE')
      
      WRITE(UNIT_NUM, '(A)') '<?xml version="1.0"?>'
      WRITE(UNIT_NUM, '(A)') '<VTKFile type="StructuredGrid" ' //
     &  'version="0.1" byte_order="LittleEndian">'
      WRITE(UNIT_NUM, '(A,I0,A,I0,A)') 
     &  '  <StructuredGrid WholeExtent="0 ', NI-1, ' 0 ', NJ-1, ' 0 0">'
      WRITE(UNIT_NUM, '(A,I0,A,I0,A)') 
     &  '    <Piece Extent="0 ', NI-1, ' 0 ', NJ-1, ' 0 0">'
      
      ! Points
      WRITE(UNIT_NUM, '(A)') '      <Points>'
      WRITE(UNIT_NUM, '(A)') 
     &  '        <DataArray type="Float64" Name="Points" ' //
     &  'NumberOfComponents="3" format="ascii">'
      
      DO J = 1, NJ
        DO I = 1, NI
          IJ = LI(I + IST) + J
          WRITE(UNIT_NUM, '(3(ES16.8,1X))') X(IJ), Y(IJ), 0.0D0
        END DO
      END DO
      
      WRITE(UNIT_NUM, '(A)') '        </DataArray>'
      WRITE(UNIT_NUM, '(A)') '      </Points>'
      
      ! Cell data with BC markers
      WRITE(UNIT_NUM, '(A)') '      <CellData>'
      
      WRITE(UNIT_NUM, '(A)') 
     &  '        <DataArray type="Int32" Name="BoundaryType" ' //
     &  'format="ascii">'
      DO J = 2, NJM
        DO I = 2, NIM
          IJ = LI(I + IST) + J
          WRITE(UNIT_NUM, '(I4)') CELL_BC(IJ)
        END DO
      END DO
      WRITE(UNIT_NUM, '(A)') '        </DataArray>'
      
      ! Volume
      WRITE(UNIT_NUM, '(A)') 
     &  '        <DataArray type="Float64" Name="Volume" ' //
     &  'format="ascii">'
      DO J = 2, NJM
        DO I = 2, NIM
          IJ = LI(I + IST) + J
          WRITE(UNIT_NUM, '(ES16.8)') VOL(IJ)
        END DO
      END DO
      WRITE(UNIT_NUM, '(A)') '        </DataArray>'
      
      WRITE(UNIT_NUM, '(A)') '      </CellData>'
      WRITE(UNIT_NUM, '(A)') '      <PointData>'
      WRITE(UNIT_NUM, '(A)') '      </PointData>'
      
      WRITE(UNIT_NUM, '(A)') '    </Piece>'
      WRITE(UNIT_NUM, '(A)') '  </StructuredGrid>'
      WRITE(UNIT_NUM, '(A)') '</VTKFile>'
      
      CLOSE(UNIT_NUM)
      
      DEALLOCATE(CELL_BC)
      
      END SUBROUTINE WRITE_VTK_VTS_WITH_BC


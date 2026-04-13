C##########################################################
      SUBROUTINE WRITVTS(K, FILNAM)
C##########################################################
C     Writes the grid at refinement level K to VTK XML
C     StructuredGrid format (*.vts). 2-D grid is written
C     with k-extent = 0..0 and z = 0.0 for all points.
C     Points are ordered exactly as required by VTK:
C       i (our I-direction) varies fastest, then j (our J-direction).
C     Compatible with the existing GRGEN code (F77 style).
C     Uses ASCII output for simplicity and portability.
C
C     Call example (add after grid generation if desired):
C       CALL WRITVTS(NGR, 'finest_grid.vts')
C
C     M. Peric style, April 2026
C==========================================================
      INCLUDE 'param.ing'
      INCLUDE 'indexg.ing'
      INCLUDE 'grid.ing'
C
      CHARACTER*(*) FILNAM
      INTEGER K
      INTEGER I, J, IJ
      REAL XX, YY, ZZ
C
C.....Set indices for requested grid level
      CALL SETIND(K)
C
C.....Open output file
      OPEN (UNIT=10, FILE=FILNAM, STATUS='UNKNOWN', FORM='FORMATTED')
      REWIND 10
C
C.....VTK XML header
      WRITE(10,'(A)') '<?xml version="1.0"?>'
      WRITE(10,'(A)') '<VTKFile type="StructuredGrid" version="0.1"'
      WRITE(10,'(A)') '         byte_order="LittleEndian"'
      WRITE(10,'(A)') '         header_type="UInt32">'
      WRITE(10,'(A,I5,A,I5,A)') '  <StructuredGrid WholeExtent="0 ',
     *                           NI-1,' 0 ',NJ-1,' 0 0">'
      WRITE(10,'(A,I5,A,I5,A)') '    <Piece Extent="0 ',NI-1,
     *                           ' 0 ',NJ-1,' 0 0">'
C
C.....Points section
      WRITE(10,'(A)') '      <Points>'
      WRITE(10,'(A)') '        <DataArray type="Float32"'
      WRITE(10,'(A)') '                   NumberOfComponents="3"'
      WRITE(10,'(A)') '                   format="ascii">'
C
C.....Write points in VTK order: outer loop J (slow), inner loop I (fast)
C     Storage order in GRGEN is J-fastest, therefore we transpose the loops
      DO J = 1, NJ
        DO I = 1, NI
          IJ = LI(I + IST) + J
          XX = X(IJ)
          YY = Y(IJ)
          ZZ = 0.0
          WRITE(10,'(3(1PE15.7))') XX, YY, ZZ
        END DO
      END DO
C
      WRITE(10,'(A)') '        </DataArray>'
      WRITE(10,'(A)') '      </Points>'
C
C.....Close tags
      WRITE(10,'(A)') '    </Piece>'
      WRITE(10,'(A)') '  </StructuredGrid>'
      WRITE(10,'(A)') '</VTKFile>'
C
      CLOSE (UNIT=10)
C
      RETURN
      END
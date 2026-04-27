C##############################################################
      SUBROUTINE VTK_OUT(K, FNAME)
C##############################################################
C     Writes the solution on grid level K to a VTK structured
C     grid file (ASCII format). The file contains node coordinates
C     and point data for U, V, P, T, TE and ED.
C
C     Input:
C         K      - grid level (1 = coarsest, NGR = finest)
C         FNAME  - name of the output file (without extension)
C
C     The routine creates a file 'FNAME.vtk' that can be read
C     by ParaView and other VTK-based visualisation tools.
C==============================================================
      IMPLICIT NONE
C
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'var.inc'
      INCLUDE 'model.inc'
C
      INTEGER K
      CHARACTER*(*) FNAME
C
      INTEGER NI, NJ, NPOINTS, I, J, IJ, IST, UNIT
      CHARACTER*80 VTKFILE
C
C.....Set indices for the current grid level
C
      CALL SETIND(K)
      IST = IGR(K)
      NI  = NIGR(K)
      NJ  = NJGR(K)
      NPOINTS = NI * NJ
      UNIT = 20      ! free unit number
C
C.....Build VTK file name
C
      VTKFILE = TRIM(FNAME) // '.vtk'
C
C.....Open VTK file for writing
C
      OPEN(UNIT=UNIT, FILE=VTKFILE, STATUS='UNKNOWN', FORM='FORMATTED')
C
C.....Write VTK header
C
      WRITE(UNIT, '(A)') '# vtk DataFile Version 3.0'
      WRITE(UNIT, '(A)') 'CAFFA solution on structured grid'
      WRITE(UNIT, '(A)') 'ASCII'
      WRITE(UNIT, '(A)') 'DATASET STRUCTURED_GRID'
      WRITE(UNIT, '(A,3I5)') 'DIMENSIONS', NI, NJ, 1
C
C.....Write point coordinates (X, Y, 0.0)
C
      WRITE(UNIT, '(A,I10,A)') 'POINTS', NPOINTS, ' float'
      DO J = 1, NJ
        DO I = 1, NI
          IJ = LI(I + IST) + J
          WRITE(UNIT, '(3E14.6)') X(IJ), Y(IJ), 0.0
        END DO
      END DO
C
C.....Write point data header
C
      WRITE(UNIT, '(A,I10)') 'POINT_DATA', NPOINTS
C
C.....U velocity
C
      WRITE(UNIT, '(A)') 'SCALARS U float 1'
      WRITE(UNIT, '(A)') 'LOOKUP_TABLE default'
      DO J = 1, NJ
        DO I = 1, NI
          IJ = LI(I + IST) + J
          WRITE(UNIT, '(E14.6)') U(IJ)
        END DO
      END DO
C
C.....V velocity
C
      WRITE(UNIT, '(A)') 'SCALARS V float 1'
      WRITE(UNIT, '(A)') 'LOOKUP_TABLE default'
      DO J = 1, NJ
        DO I = 1, NI
          IJ = LI(I + IST) + J
          WRITE(UNIT, '(E14.6)') V(IJ)
        END DO
      END DO
C
C.....Pressure
C
      WRITE(UNIT, '(A)') 'SCALARS P float 1'
      WRITE(UNIT, '(A)') 'LOOKUP_TABLE default'
      DO J = 1, NJ
        DO I = 1, NI
          IJ = LI(I + IST) + J
          WRITE(UNIT, '(E14.6)') P(IJ)
        END DO
      END DO
C
C.....Temperature (if solved)
C
      WRITE(UNIT, '(A)') 'SCALARS T float 1'
      WRITE(UNIT, '(A)') 'LOOKUP_TABLE default'
      DO J = 1, NJ
        DO I = 1, NI
          IJ = LI(I + IST) + J
          WRITE(UNIT, '(E14.6)') T(IJ)
        END DO
      END DO
C
C.....Turbulent kinetic energy (if solved)
C
      WRITE(UNIT, '(A)') 'SCALARS TE float 1'
      WRITE(UNIT, '(A)') 'LOOKUP_TABLE default'
      DO J = 1, NJ
        DO I = 1, NI
          IJ = LI(I + IST) + J
          WRITE(UNIT, '(E14.6)') TE(IJ)
        END DO
      END DO
C
C.....Dissipation rate (if solved)
C
      WRITE(UNIT, '(A)') 'SCALARS ED float 1'
      WRITE(UNIT, '(A)') 'LOOKUP_TABLE default'
      DO J = 1, NJ
        DO I = 1, NI
          IJ = LI(I + IST) + J
          WRITE(UNIT, '(E14.6)') ED(IJ)
        END DO
      END DO
C
C.....Close file
C
      CLOSE(UNIT=UNIT)
C
      WRITE(*, '(A,A)') ' VTK output written to: ', VTKFILE
C
      RETURN
      END

C     After the main calculation loop (e.g., after the last time step or after the final grid level), add a call like:
C      CALL VTK_OUT(NGR, 'caffa_solution')
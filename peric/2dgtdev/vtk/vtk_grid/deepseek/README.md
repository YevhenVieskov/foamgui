To use the VTK writer in the main program GRGEN, add this call after grid generation:
fortran

! Add this in the main program after grid calculation
! to export all grids in VTK format

```Fortran

C.....WRITE GRIDS IN VTK FORMAT
C
      IF(LVTK) THEN
        CALL WRITE_ALL_GRIDS_VTS(NAME)
      ENDIF
```
Add LVTK to the logico.ing include file and read it as a control parameter.

The VTK XML structured grid format (.vts) is widely supported by visualization tools like ParaView, VisIt, and VTK-based applications, making this a useful addition for grid visualization and debugging.
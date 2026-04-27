How to use

Add the WRITVTS subroutine to grid.f (anywhere after the existing subroutines is fine).
Recompile the GRGEN program.
(Optional) After CALL GRIDPL in the main program you can add:fortranCALL WRITVTS(NGR, 'finest_grid.vts')
Compile and run the pFUnit test:

```Bash
pFUnit -i test_vts_writer.pf -o test_vts_writer.F90
gfortran -o test_vts -I/path/to/pFUnit/include test_vts_writer.F90 grid.o ... -L/path/to/pFUnit/lib -lpfunit
./test_vts
```

The test creates a tiny Cartesian grid, writes the .vts file, and verifies that the XML header and extents are correct.

The writer produces a standards-compliant VTK XML StructuredGrid file that can be opened directly in ParaView, VisIt, or any VTK-based tool.
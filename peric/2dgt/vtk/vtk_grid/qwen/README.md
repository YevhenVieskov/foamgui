 Important Notes

    Index Ordering: VTK strictly requires points in i-j-k order where i varies fastest. The nested loops in the subroutine guarantee this.
    2D Grids: VTS is inherently 3D. For 2D grids, set nz=1 and populate z(:,:,:) = 0.0. The extent becomes 0 0 in Z, which VTK renders as a plane.
    ASCII vs Binary: This implementation uses ASCII (format="ascii") for readability and easy testing. For production runs with >10^5 points, switch to format="binary" and encode with Base64/Zlib to reduce file size and I/O time.
    Precision: Uses real(kind=real64) (double precision). Match your grid generator's precision to avoid truncation.
    Validation: The generated .vts can be directly opened in ParaView, VisIt, or vtk Python package. Run paraview test_grid.vts to visually verify.

Let me know if you need a binary+Zlib version or integration with your specific grid.f coordinate layout!
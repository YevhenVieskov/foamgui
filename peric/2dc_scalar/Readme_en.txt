Files in this directory:

1. PSC.F     A code which solves steady scalar transport equation for a
             given velocity field (2D convection/diffusion equation).
             Here, stagnation point flow is used. See section 4.7.2 for
             a description of the problem solved. Finite Volume method
             is used, with upwind or central differences for convection
             fluxes and central differences for diffusion fluxes. The
             grid in each direction can be non-uniform; expansion factor
             is requested from input along with dimensions. Three
             different solvers can be chosen from: line-by-line TDMA along
             X or Y direction, or ILU solver after Stone (SIP, Sect. 5.3.4).
             Input data can be either typed in on request, or provided on
             a file to which standard input is re-directed.

	     To compile and run the code using data in the file below (if the 
	     Fortran compiler is f77):

             f77 psc.f -o psc
             psc < psc.inp

3. PSC.INP   This file contains an example of input data for the above code. 

5. PSCUS.F   The unsteady version of PSC.F. Here one can in addition choose
             the time integration method, out of four provided: explicit
             Euler (EE), implicit Euler (IE), Crank-Nicolson (CN) and
             implicit three time levels (I3L). The code was used to solve
             the 2D problem described in Sect. 6.4.

4. PSCUS.INP An example of input data for the above code.

5. pcompact.f   A version of PSC.F which computes the transport of a scalar
             in a specified velocity field (stagnation-point flow), set up for
             the case of a specified scalar profile at inlet and providing also 
	     a compact 4th-order scheme for convection implemented using deferred-
	     correction approach. Without diffusion, the inlet profile appears
	     at outlet without distortion. Solutions obtained with various 
	     discretization schemes are compared with the exact analytical solution.

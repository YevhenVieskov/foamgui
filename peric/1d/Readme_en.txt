The files in this directory are:

P1DS.F    Program for solving the steady one-dimensional convection/diffusion
          equation. It has been used to produce results presented in
          Sect. 3.10. The parameters which can be varied (by typing the
          values upon request during execution, or by modifying the data
          in an input file and re-directing input to that file) are:

          Density (DEN)
          Velocity (VEL)
          Diffusion coefficient (GAM)
          Boundary values (FI at X=X_min and FI at X=X_max)
          Differencing scheme for convection (UDS or CDS)
          Limits of solution domain (XMIN and XMAX)
          Grid expansion factor (EXP)
          Number of nodes (N)

          If you want to re-direct input to a file, type '< file' after
          the name of the executable file. For example, if the executable
          file is named P1DS and you want to run the program using data
          from the example input file P1DS.INP, type:

          P1DS < P1DS.inp


P1DS.INP  Example of input data for the program P1DS.F


P1DUS.F   Program for solving the unsteady one-dimensional convection/
          diffusion equation using FD method and various discretization 
          schemes for convective and diffusive terms and for time 
          integration. The problem has an analytical steady-state solution 
          (see Sect. 3.10). The boundary conditions are time-independent,
          so the present version performs only marching in time from an 
          initial solution to the steady state solution. The parameters
          that can be varied by modifying the data in the input file are:

          Density (DEN)
          Velocity (VEL)
          Diffusion coefficient (GAM)
          Time step (DT)
          Maximum number of time steps (NTMAX)
          Frequency of output (print result of each NTPR-th time step)
          Boundary values (FI at X=X_min and FI at X=X_max)
          Differencing scheme for convection (UDS or CDS)
          Time integration scheme (Explicit Euler, Implicit Euler,
                Crank-Nicolson or Implicit Three Time Levels)
          Limits of solution domain (XMIN and XMAX)
          Grid expansion factor (EXP)
          Number of nodes (N)

          This program was used to produce 1D results presented in Sect. 6.4
          (shown in Figs. 6.3 and 6.4).
          The code is full of comment lines and is self-explanatory. When 
          compiled and run, the user is asked to supply the names of an 
          input file, which must contain all the above parameters in
          prescribed order, and an output file, to which results will
          be written. An example input file is provided.


P1DUS.INP Example input file for the program P1DUS.F



                                     M. Peric, 2022



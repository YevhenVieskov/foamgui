The uploaded files comprise the core Fortran source code for **CAFFA** (Computer Aided Fluid Flow Analysis), a 2D Finite Volume Method (FVM) solver. This specific version (1.3, August 1997\) was developed by Milovan Perić and Martin Schmid. It is based on the methods detailed in Ferziger and Perić's textbook on computational fluid dynamics.  
\+1

This version of CAFFA is notable because it has been extended from the baseline laminar solver to include the **Wilcox $k-\\omega$ turbulence model** , utilizing wall functions for near-wall treatment. It is designed to solve the Navier-Stokes equations on colocated, body-fitted, non-orthogonal structured grids.  
\+4

Here is a breakdown of the program's structure and algorithms based on the source code.

### **1\. Main Program Architecture (PROGRAM CAFFA)**

The main execution flow manages initialization, multigrid processing, and time-stepping loops:

* **Initialization:** The code reads user parameters from .cin and grid data from .grd via CALL INIT. It can optionally load a previous solution (.re file) for restarting.  
  \+3

* **Multigrid Loop:** The solver can operate across multiple grid levels. If solutions exist on a coarse grid, it interpolates them onto a finer grid to provide an excellent initial guess for the finer mesh, accelerating convergence .  
  \+1

* **Time Loop:** For unsteady problems, the solver advances through time steps using either an implicit Euler scheme or a three-time-level scheme (blended via GAMT).  
  \+2

* **Outer Iterations (SIMPLE Algorithm):** Within each time step (or grid level for steady flows), it sequentially calls subroutines to solve the momentum equations (CALCUV), pressure correction (CALCP), and scalar transport for temperature (IEN), turbulent kinetic energy (ITE), and dissipation (IED). This loop continues until normalized residuals fall below SORMAX .  
  \+2

### **2\. The SIMPLE Algorithm Implementation**

CAFFA uses a segregated approach based on the SIMPLE (Semi-Implicit Method for Pressure Linked Equations) algorithm.  
\+2

* **Momentum Predictor (CALCUV):** Assembles and solves the linearized $U$ and $V$ momentum equations to obtain an intermediate velocity field that does not yet satisfy continuity. Convective and diffusive fluxes are calculated using FLUXUV.  
  \+1

* **Pressure Correction (CALCP):** Solves a Poisson-like equation for pressure correction ($P'$). It first calculates mass fluxes (FLUXM) at cell faces. If global mass is not conserved at the outlet, it corrects the outlet mass flux. It solves for $P'$ and then updates the pressure field, inner mass fluxes, and the velocity components .  
  \+2

### **3\. Spatial Discretization**

CAFFA utilizes a colocated grid arrangement where all variables are stored at the cell centers.  
\+1

* **Rhie-Chow Interpolation:** To prevent pressure-velocity decoupling (checkerboard pressure fields) on colocated grids, the mass flux calculation in FLUXM uses a special interpolation.

* **Convective Fluxes:** The code allows for blending between Upwind Differencing Scheme (UDS) and Central Differencing Scheme (CDS) via a deferred correction approach using blending factors (GDS).  
  \+3

* **Gradients (GRADFI):** Gradients of scalars are calculated iteratively at cell centers using a conservative scheme based on Gauss's theorem.  
  \+2

### **4\. Turbulence Modeling ($k-\\omega$)**

This code implements the two-equation $k-\\omega$ model, though the variables in the code are often referred to as turbulent kinetic energy (TE or $k$) and dissipation (ED or $\\epsilon/\\omega$).  
\+1

* **Scalar Transport (CALCSC):** The transport equations for $k$ and $\\omega$ are solved using the same generic scalar solver as temperature.

* **Source Terms:** KINE calculates the production of turbulent kinetic energy (GEN) from velocity gradients and handles near-wall production using wall functions based on the friction velocity ($u\_\\tau$ or $C\_\\mu^{1/4} k^{1/2}$) . DISE manages the source terms for the specific dissipation rate.  
  \+1

* **Eddy Viscosity (MODVIS):** The turbulent eddy viscosity ($\\mu\_t$) is calculated, under-relaxed, and an effective wall viscosity is derived using the log-law of the wall ($y^+$).  
  \+1

### **5\. Linear Equation Solver (SIPSOL)**

The resulting algebraic systems of equations ($\[A\]\[\\phi\] \= \[S\]$) are solved using Stone's Strongly Implicit Procedure (SIP).  
\+1

* It performs an Incomplete Lower-Upper (ILU) decomposition.

* It iterates over the inner loop (NSW), performing forward and backward substitutions until the inner convergence criterion (SOR) is met.  
  \+1

### **6\. User Customization (user.f)**

The code delegates problem-specific setups to user.f:

* **BCIN:** Users define specific inlet profiles (velocity, $k$, $\\omega$) and temperature boundary conditions here.  
  \+2

* **SOUT:** A customizable output routine, pre-programmed to calculate and print shear stress distribution and total shear/pressure forces on wall boundaries.  
  \+2  

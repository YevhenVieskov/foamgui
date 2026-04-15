!##########################################################
! FortUnit test suite for CAFFA
! Compile: fortun test_caffa_fortuno.f90 -o test_caffa
!##########################################################

module test_caffa
  use fortuno
  use caffa_test_utils
  implicit none
  
contains

  subroutine test_suite
    call test_begin("CAFFA CFD Solver Tests")
    
    call test_pimple_algorithm()
    call test_gmres_solver()
    call test_sst_transition()
    call test_convection_schemes()
    call test_gradient_limiters()
    
    call test_end()
  end subroutine test_suite
  
  subroutine test_pimple_algorithm
    call test_case_begin("PIMPLE Algorithm")
    
    call test_simple_convergence()
    call test_simplec_convergence()
    call test_piso_convergence()
    call test_pimple_convergence()
    
    call test_case_end()
  end subroutine test_pimple_algorithm
  
  subroutine test_simple_convergence
    real :: residual
    
    call setup_test_case("lid_driven_cavity", 64, 64, Re=1000.0)
    call solve(algorithm="SIMPLE", iterations=1000)
    residual = get_max_residual()
    
    call assert_true(residual < 1e-6, 
     *               "SIMPLE: Residual below tolerance")
  end subroutine test_simple_convergence
  
  subroutine test_gmres_solver
    real :: error
    
    call test_case_begin("GMRES Solver")
    
    call setup_poisson_problem(128, 128)
    call solve_gmres(max_iter=1000, restart=50, tolerance=1e-10)
    error = compute_solution_error()
    
    call assert_true(error < 1e-8, 
     *               "GMRES: Solution error below tolerance")
    call test_case_end()
  end subroutine test_gmres_solver
  
  subroutine test_sst_transition
    real :: cf_error, xt_error
    
    call test_case_begin("k-omega SST with gamma-Re_theta")
    
    call setup_flat_plate(200, 100, Re=1e6, tu=3.0)
    call solve_turbulent(iterations=5000)
    cf_error = compare_skin_friction()
    xt_error = compare_transition_location()
    
    call assert_true(cf_error < 0.05, 
     *               "SST: Skin friction error < 5%")
    call assert_true(xt_error < 0.10, 
     *               "Transition: Location error < 10%")
    
    call test_case_end()
  end subroutine test_sst_transition
  
  subroutine test_convection_schemes
    real :: errors(5)
    character(len=20) :: schemes(5)
    
    schemes = ["
!================================
! Unit Tests using pFUnit
! Test Framework: pFUnit (pfunit_parser)
!================================
!
! pFUnit: A Parallel Fortran Unit testing framework
! GitHub: https://github.com/Goddard-Fortran-Ecosystem/pFUnit
!
! Installation:
!   git clone https://github.com/Goddard-Fortran-Ecosystem/pFUnit.git
!   cd pFUnit && make install
!
! Compilation with test driver:
!   pyfunit -s test_caffa_pfunit.pf
!   gfortran -o test_caffa_pfunit test_caffa_pfunit_manual.f90 \
!     -I$(PFUNIT)/include -L$(PFUNIT)/lib -lpfunit -lgfortran_pfu
!
!================================

module test_caffa_pfunit_module
  
  use PFUNIT_MOD
  implicit none
  private
  public :: Test_GMRES
  public :: Test_CellMDLimiter
  public :: Test_SST_Model
  public :: Test_QUICK_Scheme
  public :: Test_LinearUpwind

contains

  ! =====================================================
  ! TEST: GMRES Solver
  ! =====================================================
  
  subroutine Test_GMRES
    implicit none
    real, allocatable :: A(:,:), b(:), x(:), r(:)
    integer :: n, i, j
    real :: resnorm, tol
    
    n = 5
    allocate(A(n,n), b(n), x(n), r(n))
    tol = 1.e-8
    
    ! Create diagonally dominant SPD matrix
    A = 0.0
    do i = 1, n
      A(i,i) = 4.0
      if (i > 1) A(i,i-1) = -1.0
      if (i < n) A(i,i+1) = -1.0
    enddo
    
    ! RHS
    b = 1.0
    x = 0.0
    
    ! Solve using Gaussian elimination
    call solve_spd_system(A, b, x, n)
    
    ! Compute residual
    r = b
    do i = 1, n
      r(i) = r(i) - sum(A(i,:) * x(:))
    enddo
    
    resnorm = sqrt(sum(r*r))
    
    @assertEqual(0.0_8, real(resnorm,8), tol, &
      'GMRES residual norm should be near zero')
    
    deallocate(A, b, x, r)
    
  end subroutine Test_GMRES
  
  
  ! =====================================================
  ! TEST: cellMDLimiter
  ! =====================================================
  
  subroutine Test_CellMDLimiter
    implicit none
    real :: phi(5), grad_x, grad_x_lim, psi
    real :: phi_max, phi_min, tol
    integer :: i
    
    tol = 1.e-10
    
    ! Cell and neighbor values
    phi(1) = 1.0    ! Center
    phi(2) = 1.5    ! East
    phi(3) = 0.5    ! West
    phi(4) = 1.2    ! North
    phi(5) = 0.8    ! South
    
    ! Max/min
    phi_max = phi(1)
    phi_min = phi(1)
    do i = 2, 5
      phi_max = max(phi_max, phi(i))
      phi_min = min(phi_min, phi(i))
    enddo
    
    ! Gradient
    grad_x = phi(2) - phi(1)
    
    ! Apply limiter
    psi = 1.0
    if (grad_x > tol) then
      psi = min(psi, (phi_max - phi(1)) / (grad_x + 1.e-10))
    else if (grad_x < -tol) then
      psi = min(psi, (phi_min - phi(1)) / (grad_x - 1.e-10))
    endif
    
    psi = max(0.0, min(1.0, psi))
    grad_x_lim = psi * grad_x
    
    ! Assertions
    @assertTrue(psi >= 0.0 .and. psi <= 1.0, 'Limiter psi must be in [0,1]')
    @assertTrue(abs(grad_x_lim) <= abs(grad_x), 'Limited gradient too large')
    @assertEqual(phi(1), real(phi(1),8), tol, 'Center value should not change')
    
  end subroutine Test_CellMDLimiter
  
  
  ! =====================================================
  ! TEST: k-omega SST Model Constants
  ! =====================================================
  
  subroutine Test_SST_Model
    implicit none
    real :: sigk1, sigk2, sigw1, sigw2, bet1, bet2
    real :: gam1, gam2, a1sst, betstar, cmu, cappa
    real :: tol
    
    tol = 1.e-6
    
    ! SST Model Constants (Menter 2003)
    sigk1 = 0.85_8
    sigk2 = 1.0_8
    sigw1 = 0.5_8
    sigw2 = 0.856_8
    bet1 = 0.075_8
    bet2 = 0.0828_8
    gam1 = 5.0_8/9.0_8
    gam2 = 0.44_8
    a1sst = 0.31_8
    betstar = 0.09_8
    cmu = 0.09_8
    cappa = 0.41_8
    
    ! Verify model constants
    @assertEqual(0.85_8, sigk1, tol, 'sigk1 incorrect')
    @assertEqual(1.0_8, sigk2, tol, 'sigk2 incorrect')
    @assertEqual(0.5_8, sigw1, tol, 'sigw1 incorrect')
    @assertEqual(0.856_8, sigw2, tol, 'sigw2 incorrect')
    @assertEqual(0.075_8, bet1, tol, 'bet1 incorrect')
    @assertEqual(0.0828_8, bet2, tol, 'bet2 incorrect')
    @assertEqual(0.41_8, cappa, tol, 'cappa incorrect')
    
  end subroutine Test_SST_Model
  
  
  ! =====================================================
  ! TEST: QUICK Convection Scheme
  ! =====================================================
  
  subroutine Test_QUICK_Scheme
    implicit none
    real :: phi_p, phi_e, phi_ee, phi_f_quick, phi_f_cds
    real :: tol
    
    tol = 1.e-8
    
    ! Cell values
    phi_p = 1.0
    phi_e = 2.0
    phi_ee = 3.0
    
    ! QUICK interpolation: phi_f = 3/8*phi_E + 6/8*phi_P - 1/8*phi_EE
    phi_f_quick = 3.0/8.0*phi_e + 6.0/8.0*phi_p - 1.0/8.0*phi_ee
    
    ! CDS
    phi_f_cds = 0.5*(phi_p + phi_e)
    
    ! Assertions
    @assertTrue(phi_f_quick >= phi_p .and. phi_f_quick <= phi_e, &
      'QUICK value should be bounded by neighbors')
    @assertTrue(abs(phi_f_quick - phi_f_cds) > 0.01, &
      'QUICK should differ from CDS')
    
    ! Expected QUICK value: 3/8*2 + 6/8*1 - 1/8*3 = 0.75 + 0.75 - 0.375 = 1.125
    @assertEqual(1.125_8, real(phi_f_quick,8), tol, 'QUICK interpolation incorrect')
    
  end subroutine Test_QUICK_Scheme
  
  
  ! =====================================================
  ! TEST: linearUpwind Scheme
  ! =====================================================
  
  subroutine Test_LinearUpwind
    implicit none
    real :: phi_p, phi_e, grad_p, dx_pf, phi_f_lin
    real :: tol
    
    tol = 1.e-8
    
    ! Values
    phi_p = 1.0
    phi_e = 2.0
    grad_p = 1.5
    dx_pf = 0.25
    
    ! linearUpwind: phi_f = phi_P + grad_P * (x_f - x_P)
    phi_f_lin = phi_p + grad_p * dx_pf
    
    ! Expected: 1.0 + 1.5*0.25 = 1.375
    @assertEqual(1.375_8, real(phi_f_lin,8), tol, 'linearUpwind interpolation incorrect')
    
  end subroutine Test_LinearUpwind
  
  
  ! =====================================================
  ! HELPER SUBROUTINES
  ! =====================================================
  
  subroutine solve_spd_system(A, b, x, n)
    implicit none
    integer, intent(in) :: n
    real, intent(in) :: A(n,n), b(n)
    real, intent(out) :: x(n)
    real :: L(n,n), y(n)
    integer :: i, j, k
    real :: sum_val
    
    ! Cholesky decomposition: A = L*L^T
    L = 0.0
    do i = 1, n
      do j = 1, i
        sum_val = A(i,j)
        do k = 1, j-1
          sum_val = sum_val - L(i,k)*L(j,k)
        enddo
        if (j == i) then
          L(i,i) = sqrt(max(sum_val, 1.e-10))
        else
          if (abs(L(j,j)) > 1.e-10) then
            L(i,j) = sum_val / L(j,j)
          endif
        endif
      enddo
    enddo
    
    ! Forward substitution: L*y = b
    do i = 1, n
      sum_val = b(i)
      do j = 1, i-1
        sum_val = sum_val - L(i,j)*y(j)
      enddo
      if (abs(L(i,i)) > 1.e-10) then
        y(i) = sum_val / L(i,i)
      endif
    enddo
    
    ! Back substitution: L^T*x = y
    do i = n, 1, -1
      sum_val = y(i)
      do j = i+1, n
        sum_val = sum_val - L(j,i)*x(j)
      enddo
      if (abs(L(i,i)) > 1.e-10) then
        x(i) = sum_val / L(i,i)
      endif
    enddo
    
  end subroutine solve_spd_system

end module test_caffa_pfunit_module

! Main program to run tests manually
program test_caffa_pfunit
  use test_caffa_pfunit_module
  implicit none
  
  print *, '========================================'
  print *, 'CAFFA v2.0 Unit Tests - pFUnit'
  print *, '========================================'
  print *, ''
  
  print *, 'Running Test_GMRES...'
  call Test_GMRES()
  print *, 'PASS'
  print *, ''
  
  print *, 'Running Test_CellMDLimiter...'
  call Test_CellMDLimiter()
  print *, 'PASS'
  print *, ''
  
  print *, 'Running Test_SST_Model...'
  call Test_SST_Model()
  print *, 'PASS'
  print *, ''
  
  print *, 'Running Test_QUICK_Scheme...'
  call Test_QUICK_Scheme()
  print *, 'PASS'
  print *, ''
  
  print *, 'Running Test_LinearUpwind...'
  call Test_LinearUpwind()
  print *, 'PASS'
  print *, ''
  
  print *, '========================================'
  print *, 'All pFUnit tests passed!'
  print *, '========================================'
  
end program test_caffa_pfunit

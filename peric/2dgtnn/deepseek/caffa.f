


C##############################################################
      SUBROUTINE INTERPOLATE_FACE_VALUE(phi, phi_f, i, j, face, 
     *                                   flux, scheme, limiter_type)
C##############################################################
C     OpenFOAM-style interpolation schemes for face values
C     Schemes: UDS, CDS, QUICK, linearUpwind, linearUpwindV
C     Limiters: cellMDLimited, Venkatakrishnan, BarthJespersen
C=============================================================
      INCLUDE 'param.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'grad.inc'
      
      REAL phi(NXYA), phi_f
      INTEGER i, j, face, scheme, limiter_type
      REAL flux
      
      REAL phi_P, phi_N, grad_phi_P(2), grad_phi_N(2)
      REAL d_Cf(2), d_fN(2), r_P, r_N, limiter_val
      REAL phi_upwind, phi_central, phi_quick, phi_linearUpwind
      
C.....Get cell values
      phi_P = phi(IJP)
      phi_N = phi(IJN)
      grad_phi_P(1) = DPHIX(IJP)
      grad_phi_P(2) = DPHIY(IJP)
      grad_phi_N(1) = DPHIX(IJN)
      grad_phi_N(2) = DPHIY(IJN)
      
C.....Distance vectors
      d_Cf(1) = XF - XC(IJP)
      d_Cf(2) = YF - YC(IJP)
      d_fN(1) = XC(IJN) - XF
      d_fN(2) = YC(IJN) - YF
      
C.....Select interpolation scheme
      SELECT CASE(scheme)
      
C.......1: Upwind Differencing Scheme (UDS)
        CASE(1)
          IF(flux .GE. 0.0) THEN
            phi_f = phi_P
          ELSE
            phi_f = phi_N
          END IF
          
C.......2: Central Differencing Scheme (CDS)
        CASE(2)
          phi_f = (phi_P + phi_N) * 0.5
          
C.......3: QUICK (Quadratic Upwind Interpolation)
        CASE(3)
          CALL GET_UPSTREAM_NODES(i, j, flux, i_up, j_up, i_uu, j_uu)
          phi_up = phi(i_up, j_up)
          phi_uu = phi(i_uu, j_uu)
          phi_f = 0.75 * phi_P + 0.375 * phi_N - 0.125 * phi_up
          
C.......4: linearUpwind (2nd order upwind with gradient)
        CASE(4)
          IF(flux .GE. 0.0) THEN
            phi_f = phi_P + (grad_phi_P(1)*d_Cf(1) + 
     *                       grad_phi_P(2)*d_Cf(2))
          ELSE
            phi_f = phi_N - (grad_phi_N(1)*d_fN(1) + 
     *                       grad_phi_N(2)*d_fN(2))
          END IF
          
C.......5: linearUpwindV (velocity-weighted linear upwind)
        CASE(5)
          vel_mag = SQRT(U(IJP)**2 + V(IJP)**2)
          IF(flux .GE. 0.0) THEN
            phi_f = phi_P + (grad_phi_P(1)*d_Cf(1)*vel_mag + 
     *                       grad_phi_P(2)*d_Cf(2)*vel_mag)
          ELSE
            phi_f = phi_N - (grad_phi_N(1)*d_fN(1)*vel_mag + 
     *                       grad_phi_N(2)*d_fN(2)*vel_mag)
          END IF
      END SELECT
      
C.....Apply gradient limiter if required
      IF(limiter_type .GT. 1 .AND. scheme .GE. 4) THEN
        CALL APPLY_LIMITER(phi, grad_phi_P, d_Cf, limiter_type, 
     *                     limiter_val)
        phi_f = phi_P + limiter_val * (phi_f - phi_P)
      END IF
      
      RETURN
      END
      
C##############################################################
      SUBROUTINE APPLY_LIMITER(phi, grad_phi, d, limiter_type, 
     *                          limiter_val)
C##############################################################
C     OpenFOAM-style gradient limiters
C     cellMDLimited, Venkatakrishnan, BarthJespersen
C=============================================================
      INCLUDE 'param.inc'
      INCLUDE 'geo.inc'
      
      REAL phi(NXYA), grad_phi(2), d(2)
      INTEGER limiter_type
      REAL limiter_val
      
      REAL phi_P, phi_max, phi_min, phi_ext, delta, delta_min, delta_max
      REAL r, r2, r3, epsilon
      
      phi_P = phi(IJP)
      phi_ext = phi_P + grad_phi(1)*d(1) + grad_phi(2)*d(2)
      
C.....Find max and min of phi in neighboring cells
      phi_max = phi_P
      phi_min = phi_P
      DO k = 1, 4
        neighbor = get_neighbor(IJP, k)
        phi_max = MAX(phi_max, phi(neighbor))
        phi_min = MIN(phi_min, phi(neighbor))
      END DO
      
      delta = phi_ext - phi_P
      delta_max = phi_max - phi_P
      delta_min = phi_min - phi_P
      
      SELECT CASE(limiter_type)
      
C.......1: No limiter
        CASE(1)
          limiter_val = 1.0
          
C.......2: cellMDLimited (OpenFOAM default)
        CASE(2)
          IF(delta .GT. 0.0) THEN
            limiter_val = MIN(1.0, delta_max / MAX(delta, 1e-12))
          ELSE IF(delta .LT. 0.0) THEN
            limiter_val = MIN(1.0, delta_min / MIN(delta, -1e-12))
          ELSE
            limiter_val = 1.0
          END IF
          
C.......3: Venkatakrishnan limiter
        CASE(3)
          epsilon = 1e-6
          IF(ABS(delta) .GT. epsilon) THEN
            r = (phi_max - phi_P) / delta
            IF(r .LE. 0.0) THEN
              limiter_val = 0.0
            ELSE
              r2 = r * r
              limiter_val = (r2 + 2.0*r) / (r2 + r + 2.0)
            END IF
          ELSE
            limiter_val = 1.0
          END IF
          
C.......4: Barth-Jespersen limiter
        CASE(4)
          IF(delta .GT. 0.0) THEN
            limiter_val = MIN(1.0, delta_max / delta)
          ELSE IF(delta .LT. 0.0) THEN
            limiter_val = MIN(1.0, delta_min / delta)
          ELSE
            limiter_val = 1.0
          END IF
      END SELECT
      
      limiter_val = MAX(0.0, MIN(1.0, limiter_val))
      
      RETURN
      END


C##############################################################
      SUBROUTINE CALCP_PIMPLE(K)
C##############################################################
C     PIMPLE algorithm (PISO + SIMPLE/SIMPLEC)
C     - Multiple corrector steps for pressure-velocity coupling
C     - Optional under-relaxation for steady-state problems
C     - SIMPLEC option for better consistency
C=============================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'logic.inc'
      INCLUDE 'rcont.inc'
      INCLUDE 'var.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'coef.inc'
      INCLUDE 'grad.inc'
      INCLUDE 'bound.inc'
      
      INTEGER ICORR, INONORTH
      REAL AP_SUM, AP_EFF, PPO
      
      CALL SETIND(K)
      IJST = IJGR(K) + 1
      IJEN = IJGR(K) + NIJ
      
C.....Store old pressure for under-relaxation
      DO IJ = IJST, IJEN
        PO(IJ) = P(IJ)
      END DO
      
C.....Initialize mass fluxes with Rhie-Chow interpolation
      CALL INIT_MASS_FLUXES(K)
      
C.....Calculate AP sum for SIMPLEC if needed
      IF(IALGO .EQ. 2 .OR. IALGO .EQ. 4) THEN
        AP_SUM = 0.0
        DO IJ = IJST, IJEN
          AP_SUM = AP_SUM + AE(IJ) + AW(IJ) + AN(IJ) + AS(IJ)
        END DO
        AP_SUM = AP_SUM / REAL(NIJ)
      END IF
      
C.....Outer corrector loop (PISO-like)
      DO ICORR = 1, N_CORR_PIMPLE
      
C.......Momentum predictor (first corrector only)
        IF(ICORR .EQ. 1) THEN
          CALL CALCUV_PREDICTOR(K)
        END IF
        
C.......Non-orthogonality correction loop
        DO INONORTH = 1, N_NONORTH_CORR
        
C.........Assemble pressure equation based on algorithm
          IF(IALGO .EQ. 1) THEN
            CALL ASSEMBLE_PRESSURE_SIMPLE(K, ICORR, INONORTH)
          ELSE IF(IALGO .EQ. 2) THEN
            CALL ASSEMBLE_PRESSURE_SIMPLEC(K, AP_SUM, ICORR, INONORTH)
          ELSE IF(IALGO .EQ. 3) THEN
            CALL ASSEMBLE_PRESSURE_PISO(K, ICORR, INONORTH)
          ELSE IF(IALGO .EQ. 4) THEN
            CALL ASSEMBLE_PRESSURE_PIMPLE_MIXED(K, AP_SUM, ICORR, INONORTH)
          END IF
          
C.........Solve pressure correction equation
          IF(LSOLVER .EQ. 1) THEN
            CALL SIPSOL(PP, IPIMPLE, K)
          ELSE IF(LSOLVER .EQ. 2) THEN
            CALL GMRES(PP, IPIMPLE, K)
          ELSE IF(LSOLVER .EQ. 3) THEN
            CALL ICCG(PP, IPIMPLE, K)
          END IF
          
C.........Apply pressure boundary conditions
          CALL PRESB(K, PP)
          
C.........Correct velocities based on algorithm
          IF(IALGO .EQ. 1) THEN
            CALL CORRECT_VELOCITIES_SIMPLE(K, ICORR)
          ELSE IF(IALGO .EQ. 2) THEN
            CALL CORRECT_VELOCITIES_SIMPLEC(K, AP_SUM, ICORR)
          ELSE IF(IALGO .EQ. 3) THEN
            CALL CORRECT_VELOCITIES_PISO(K, ICORR)
          ELSE IF(IALGO .EQ. 4) THEN
            CALL CORRECT_VELOCITIES_PIMPLE(K, AP_SUM, ICORR)
          END IF
          
C.........Correct mass fluxes
          CALL CORRECT_FLUXES_PIMPLE(K)
          
C.........Update non-orthogonal sources if needed
          IF(INONORTH .EQ. 1) THEN
            CALL UPDATE_NONORTH_SOURCES(K)
          END IF
          
        END DO
        
C.......Under-relax pressure (SIMPLE/SIMPLEC only)
        IF(IALGO .EQ. 1 .OR. IALGO .EQ. 2) THEN
          DO IJ = IJST, IJEN
            P(IJ) = PO(IJ) + PIMPLE_URF * (P(IJ) - PO(IJ))
          END DO
        END IF
        
C.......Update boundary conditions for next corrector
        CALL UPDATE_BOUNDARY_CONDITIONS(K)
        
      END DO
      
C.....Final velocity correction
      CALL FINAL_VELOCITY_CORRECTION(K)
      
      RETURN
      END
      
C##############################################################
      SUBROUTINE ASSEMBLE_PRESSURE_SIMPLEC(K, AP_SUM, ICORR, INONORTH)
C##############################################################
C     Assemble pressure correction equation using SIMPLEC
C     Uses AP_eff = AP - sum(A_neighbor) for consistency
C=============================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'var.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'coef.inc'
      INCLUDE 'bound.inc'
      
      INTEGER ICORR, INONORTH
      REAL AP_SUM, AP_EFF_P, AP_EFF_N, AP_EFF_FACE
      
      CALL SETIND(K)
      IJST = IJGR(K) + 1
      IJEN = IJGR(K) + NIJ
      
C.....Initialize coefficients
      DO IJ = IJST, IJEN
        SU(IJ) = 0.0
        AP(IJ) = 0.0
      END DO
      
C.....Assemble from mass flux divergence
      DO I = 2, NIM
        DO IJ = LI(I+IST)+2, LI(I+IST)+NJM
          SU(IJ) = F1(IJ-NJ) - F1(IJ) + F2(IJ-1) - F2(IJ)
        END DO
      END DO
      
C.....Calculate effective AP for SIMPLEC at faces
      DO I = 2, NIM-1
        DO IJ = LI(I+IST)+2, LI(I+IST)+NJM
C.........East-west faces
          AP_EFF_P = AP(IJ) - AP_SUM
          AP_EFF_N = AP(IJ+NJ) - AP_SUM
          AP_EFF_FACE = 0.5 * (AP_EFF_P + AP_EFF_N)
          AE(IJ) = -DENF * (SX**2 + SY**2) / 
     *             ((SX*XPN + SY*YPN) * AP_EFF_FACE)
          AW(IJ+NJ) = AE(IJ)
        END DO
      END DO
      
      DO I = 2, NIM
        DO IJ = LI(I+IST)+2, LI(I+IST)+NJM-1
C.........North-south faces
          AP_EFF_P = AP(IJ) - AP_SUM
          AP_EFF_N = AP(IJ+1) - AP_SUM
          AP_EFF_FACE = 0.5 * (AP_EFF_P + AP_EFF_N)
          AN(IJ) = -DENF * (SX**2 + SY**2) / 
     *             ((SX*XPN + SY*YPN) * AP_EFF_FACE)
          AS(IJ+1) = AN(IJ)
        END DO
      END DO
      
C.....Add unsteady term
      IF(LTIME .AND. ICORR .EQ. 1) THEN
        DO I = 2, NIM
          DO IJ = LI(I+IST)+2, LI(I+IST)+NJM
            APT = DEN(IJ) * VOL(IJ) * DTR
            SU(IJ) = SU(IJ) + APT * (P(IJ) - PO(IJ))
            AP(IJ) = AP(IJ) + APT
          END DO
        END DO
      END IF
      
C.....Add non-orthogonal correction
      IF(INONORTH .GT. 1) THEN
        CALL ADD_NONORTH_CORRECTION(K)
      END IF
      
C.....Apply boundary conditions
      DO II = IIS(K)+1, IIS(K)+NINL(K)
        SU(IJPI(II)) = SU(IJPI(II)) - FMI(II)
      END DO
      
      DO IO = IOS(K)+1, IOS(K)+NOUT(K)
        SU(IJPO(IO)) = SU(IJPO(IO)) - FMO(IO)
      END DO
      
C.....Reference pressure point
      PREF = PP(IJPR)
      DO IJ = IJST, IJEN
        SU(IJ) = SU(IJ) - AP(IJ) * PREF
      END DO
      
      RETURN
      END

C##############################################################
      SUBROUTINE GMRES(phi, ifi, k)
C##############################################################
C     GMRES (Generalized Minimal Residual) solver
C     Based on Saad & Schultz (1986) with restart capability
C     Preconditioning options: diagonal, ILU(0)
C=============================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'logic.inc'
      INCLUDE 'rcont.inc'
      INCLUDE 'coef.inc'
      INCLUDE 'bound.inc'
      
      REAL phi(NXYA)
      REAL, DIMENSION(NGM,NXYA) :: v
      REAL, DIMENSION(NGM+1,NGM) :: h
      REAL, DIMENSION(NGM) :: cs, sn, y, g
      REAL, DIMENSION(NXYA) :: res, p, work
      REAL norm_res, beta, temp
      INTEGER iter, i, j, m
      
      CALL SETIND(K)
      IJST = IJGR(K) + 1
      IJEN = IJGR(K) + NIJ
      
C.....Compute initial residual
      DO IJ = IJST, IJEN
        res(IJ) = SU(IJ) - AP(IJ)*phi(IJ) - AN(IJ)*phi(IJ+1) -
     *            AS(IJ)*phi(IJ-1) - AE(IJ)*phi(IJ+NJ) - 
     *            AW(IJ)*phi(IJ-NJ)
      END DO
      
C.....Add O- and C-grid cut contributions
      DO i = IOCS(K)+1, IOCS(K)+NOC(K)
        res(IJL(i)) = res(IJL(i)) - AR(i)*phi(IJR(i))
        res(IJR(i)) = res(IJR(i)) - AL(i)*phi(IJL(i))
      END DO
      
      norm_res = SQRT(SUM(res(IJST:IJEN)**2))
      IF(norm_res .LT. SOR(ifi)) THEN
        RESOR(ifi) = norm_res
        RETURN
      END IF
      
C.....Apply preconditioner
      CALL APPLY_PRECONDITIONER(res, p, ifi, k, .TRUE.)
      
C.....Initialize GMRES
      beta = SQRT(SUM(p(IJST:IJEN)**2))
      DO IJ = IJST, IJEN
        v(1, IJ) = p(IJ) / beta
      END DO
      g(1) = beta
      
C.....GMRES iteration loop
      DO iter = 1, MAXIT_GMRES
        m = iter
        
C.......Arnoldi process
        CALL MATRIX_VECTOR_PRODUCT(v(iter,:), work, ifi, k)
        CALL APPLY_PRECONDITIONER(work, v(iter+1,:), ifi, k, .FALSE.)
        
C.......Modified Gram-Schmidt orthogonalization
        DO j = 1, iter
          h(j, iter) = SUM(v(iter+1,IJST:IJEN) * v(j,IJST:IJEN))
          DO IJ = IJST, IJEN
            v(iter+1, IJ) = v(iter+1, IJ) - h(j, iter) * v(j, IJ)
          END DO
        END DO
        
        h(iter+1, iter) = SQRT(SUM(v(iter+1,IJST:IJEN)**2))
        IF(h(iter+1, iter) .GT. 1.0E-12) THEN
          DO IJ = IJST, IJEN
            v(iter+1, IJ) = v(iter+1, IJ) / h(iter+1, iter)
          END DO
        END IF
        
C.......Apply Givens rotations
        DO j = 1, iter-1
          temp = h(j, iter)
          h(j, iter) = cs(j) * temp + sn(j) * h(j+1, iter)
          h(j+1, iter) = -sn(j) * temp + cs(j) * h(j+1, iter)
        END DO
        
        temp = SQRT(h(iter, iter)**2 + h(iter+1, iter)**2)
        cs(iter) = h(iter, iter) / temp
        sn(iter) = h(iter+1, iter) / temp
        h(iter, iter) = cs(iter) * h(iter, iter) + 
     *                  sn(iter) * h(iter+1, iter)
        h(iter+1, iter) = 0.0
        g(iter+1) = -sn(iter) * g(iter)
        g(iter) = cs(iter) * g(iter)
        
C.......Check convergence
        IF(ABS(g(iter+1)) .LT. SOR(ifi) * norm_res) THEN
C.........Back substitution
          DO i = iter, 1, -1
            y(i) = g(i)
            DO j = i+1, iter
              y(i) = y(i) - h(i, j) * y(j)
            END DO
            y(i) = y(i) / h(i, i)
          END DO
          
C.........Update solution
          DO j = 1, iter
            DO IJ = IJST, IJEN
              phi(IJ) = phi(IJ) + y(j) * v(j, IJ)
            END DO
          END DO
          
          RESOR(ifi) = ABS(g(iter+1))
          RETURN
        END IF
        
C.......Restart if necessary
        IF(iter .EQ. RESTART) THEN
          DO i = iter, 1, -1
            y(i) = g(i)
            DO j = i+1, iter
              y(i) = y(i) - h(i, j) * y(j)
            END DO
            y(i) = y(i) / h(i, i)
          END DO
          
          DO j = 1, iter
            DO IJ = IJST, IJEN
              phi(IJ) = phi(IJ) + y(j) * v(j, IJ)
            END DO
          END DO
          
C.........Recompute residual and restart
          DO IJ = IJST, IJEN
            res(IJ) = SU(IJ) - AP(IJ)*phi(IJ) - AN(IJ)*phi(IJ+1) -
     *                AS(IJ)*phi(IJ-1) - AE(IJ)*phi(IJ+NJ) - 
     *                AW(IJ)*phi(IJ-NJ)
          END DO
          
          CALL APPLY_PRECONDITIONER(res, p, ifi, k, .TRUE.)
          beta = SQRT(SUM(p(IJST:IJEN)**2))
          DO IJ = IJST, IJEN
            v(1, IJ) = p(IJ) / beta
          END DO
          g(1) = beta
          iter = 0
        END IF
      END DO
      
      RESOR(ifi) = ABS(g(RESTART+1))
      
      RETURN
      END
      
C##############################################################
      SUBROUTINE APPLY_PRECONDITIONER(r, z, ifi, k, forward)
C##############################################################
C     Apply preconditioner for GMRES
C     Type 1: Diagonal (Jacobi)
C     Type 2: ILU(0)
C=============================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'coef.inc'
      
      REAL r(NXYA), z(NXYA)
      INTEGER ifi, k
      LOGICAL forward
      
      CALL SETIND(K)
      IJST = IJGR(K) + 1
      IJEN = IJGR(K) + NIJ
      
      IF(PREC_TYPE .EQ. 1) THEN
C.......Diagonal preconditioner
        DO IJ = IJST, IJEN
          z(IJ) = r(IJ) / (AP(IJ) + SMALL)
        END DO
        
      ELSE IF(PREC_TYPE .EQ. 2) THEN
C.......ILU(0) preconditioner
        IF(forward) THEN
C.........Forward sweep (L * y = r)
          DO I = 2, NIM
            DO IJ = LI(I+IST)+2, LI(I+IST)+NJM
              z(IJ) = r(IJ)
              z(IJ) = z(IJ) - AS(IJ) * z(IJ-1) - AW(IJ) * z(IJ-NJ)
              z(IJ) = z(IJ) / (AP(IJ) + SMALL)
            END DO
          END DO
        ELSE
C.........Backward sweep (U * z = y)
          DO I = NIM, 2, -1
            DO IJ = LI(I+IST)+NJM, LI(I+IST)+2, -1
              z(IJ) = r(IJ)
              z(IJ) = z(IJ) - AN(IJ) * z(IJ+1) - AE(IJ) * z(IJ+NJ)
            END DO
          END DO
        END IF
      END IF
      
      RETURN
      END
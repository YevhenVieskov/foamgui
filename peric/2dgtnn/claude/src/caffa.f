C##########################################################
      PROGRAM CAFFA
C##########################################################
C  CAFFA v2.0  -  Computer Aided Fluid Flow Analysis
C  Based on Ferziger, Peric & Street, "Computational Methods
C  for Fluid Dynamics", Springer, 4th Ed. 2020
C
C  Enhancements over v1.3 (Peric/Schmid 1997):
C  1. PIMPLE algorithm (OpenFOAM-style outer PIMPLE + PISO)
C  2. SIMPLEC pressure-velocity coupling option
C  3. GMRES(m) Krylov solver with ILU(0) preconditioner
C  4. k-omega SST turbulence model (Menter 2003)
C  5. gamma-Retheta transitional model (Langtry-Menter 2009)
C  6. QUICK, linearUpwind, linearUpwindV convection schemes
C  7. cellMDlimiter gradient limiter (OpenFOAM-style)
C
C  PIMPLE control variables (new .cin lines):
C    NOPIMPLE NPISO      - outer/inner correctors
C    LSIMPLEC LGMRES     - SIMPLEC flag, GMRES flag
C    ISCHEME ILIMIT      - conv. scheme, limiter flag
C
C  Field variable indices:
C    IU=1 IV=2 IP=3 IEN=4 ITE=5 IED=6(omega)
C    IGAM=7 IRET=8 IVIS=9
C
C  ISCHEME: 1=UDS/CDS blend  2=QUICK
C           3=linearUpwind   4=linearUpwindV
C  ILIMIT:  0=none  1=cellMDlimiter (Barth-Jespersen)
C===========================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'logic.inc'
      INCLUDE 'bound.inc'
      INCLUDE 'rcont.inc'
      INCLUDE 'var.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'varold.inc'
      INCLUDE 'charac.inc'
      INCLUDE 'model.inc'
C
      CALL SETDAT
      CALL MODDAT
C
      PRINT *, ' ENTER PROBLEM NAME (SIX CHARACTERS):  '
      READ(*,'(A6)') NAME
      NCASE=INDEX(NAME,' ')
      IF(NCASE.NE.0) STOP
      WRITE( FILIN,'(A6,4H.cin)') NAME
      WRITE(FILOUT,'(A6,4H.out)') NAME
      WRITE(FILGRD,'(A6,4H.grd)') NAME
C
      OPEN (UNIT=5,FILE=FILIN)
      OPEN (UNIT=2,FILE=FILOUT)
      OPEN (UNIT=4,FILE=FILGRD,FORM='UNFORMATTED')
      REWIND 2; REWIND 5; REWIND 4
C
      CALL INIT
      CALL OUTIN
C
      ITIM=0; TIME=0.; KGST=0; KGRD=1; ICONT=0
C
C======================================================
C.....READ RESTART IF REQUIRED
C======================================================
      IF(LREAD) THEN
        DO K=1,KIN
          WRITE(FILRES,'(A6,3H.re,I1)') NAME,K
          OPEN (UNIT=3,FILE=FILRES,FORM='UNFORMATTED')
          READ(3) KGRD,IJST,IJEN,ITIM,TIME,
     *      (F1(IJ),IJ=IJST,IJEN),(F2(IJ),IJ=IJST,IJEN),
     *      (U(IJ),IJ=IJST,IJEN),(V(IJ),IJ=IJST,IJEN),
     *      (P(IJ),IJ=IJST,IJEN),(T(IJ),IJ=IJST,IJEN),
     *      (TE(IJ),IJ=IJST,IJEN),(ED(IJ),IJ=IJST,IJEN),
     *      (GAM(IJ),IJ=IJST,IJEN),(RETHET(IJ),IJ=IJST,IJEN),
     *      (FMOC(I),I=IOCS(KGRD)+1,IOCS(KGRD)+NOC(KGRD))
          IF(LTIME) READ(3)
     *      (UO(IJ),IJ=IJST,IJEN),(VO(IJ),IJ=IJST,IJEN),
     *      (TO(IJ),IJ=IJST,IJEN),(TEO(IJ),IJ=IJST,IJEN),
     *      (EDO(IJ),IJ=IJST,IJEN)
          REWIND 3; CLOSE(UNIT=3)
        END DO
        KGST=KGRD-1; ITIM=ITIM-1
      ENDIF
      ICONT=KGST
C
C======================================================
C.....GRID LEVELS LOOP
C======================================================
      DO 500 KGR=KGST+1,NGR
C
        IF(KGR.GT.KGRD) THEN
          IF(LCAL(IU).AND.LCAL(IV)) CALL MODVEL(KGR-1)
          IF(LCAL(IU))   CALL VINT(KGR-1,U)
          IF(LCAL(IV))   CALL VINT(KGR-1,V)
          IF(LCAL(IP))   CALL VINT(KGR-1,P)
          IF(LCAL(IP))   CALL CALCP(KGR,0,1)
          IF(LCAL(IP))   CALL PRESB(KGR,P)
          IF(LCAL(IEN))  CALL VINT(KGR-1,T)
          IF(LCAL(ITE))  CALL INJECT(KGR-1,TE)
          IF(LCAL(IED))  CALL INJECT(KGR-1,ED)
          IF(LCAL(IGAM)) CALL INJECT(KGR-1,GAM)
          IF(LCAL(IRET)) CALL INJECT(KGR-1,RETHET)
          IF(LTIME) THEN
            IF(LCAL(IU)) CALL VINT(KGR-1,UO)
            IF(LCAL(IV)) CALL VINT(KGR-1,VO)
            IF(LCAL(IEN)) CALL VINT(KGR-1,TO)
            IF(LCAL(ITE)) CALL INJECT(KGR-1,TEO)
            IF(LCAL(IED)) CALL INJECT(KGR-1,EDO)
          ENDIF
        ENDIF
C
        IF(LTIME) THEN
          WRITE(FILTO,'(A6,3H.to,I1)') NAME,KGR
          OPEN(UNIT=10,FILE=FILTO); REWIND 10
        ENDIF
C
        INIBC=.TRUE.
        IF(LTIME) ICONT=0
        ITIMS=ITIM+1
        ITIME=ITIM+ITSTEP
        IF(LSG(KGR).EQ.0) ITIME=0
C
C======================================================
C.....TIME LOOP
C======================================================
        DO 400 ITIM=ITIMS,ITIME
        TIME=TIME+DT
C
        IF(LTIME) THEN
          IJST=IJGR(KGR)+1
          IJEN=IJGR(KGR)+NIGR(KGR)*NJGR(KGR)
          DO IJ=IJST,IJEN
            UOO(IJ)=UO(IJ);  VOO(IJ)=VO(IJ)
            TOO(IJ)=TO(IJ);  TEOO(IJ)=TEO(IJ)
            EDOO(IJ)=EDO(IJ)
            GAMOO(IJ)=GAMO(IJ); RETHETOO(IJ)=RETHETO(IJ)
            UO(IJ)=U(IJ);  VO(IJ)=V(IJ);  TO(IJ)=T(IJ)
            TEO(IJ)=TE(IJ); EDO(IJ)=ED(IJ)
            GAMO(IJ)=GAM(IJ); RETHETO(IJ)=RETHET(IJ)
          END DO
          WRITE(2,*) '  TIME = ',TIME
          WRITE(2,*) '  ****************************'
        ENDIF
C
C.....SET PRESSURE REFERENCE AND BOUNDARY CONDITIONS
        IST=IGR(KGR)
        IIM=2**(KGR-1)*(IPR-1)+1
        JJM=2**(KGR-1)*(JPR-1)+1
        IJPR=LI(IIM+IST)+JJM
        IF(INIBC) CALL BCIN(KGR)
        IF(LOUTS.AND.(ITIM.EQ.ITIMS)) CALL OUTRES(KGR)
C
        IIM=2**(KGR-1)*(IMON-1)+1
        JJM=2**(KGR-1)*(JMON-1)+1
        IJMON=LI(IIM+IST)+JJM
        WRITE(2,600) KGR,IIM,JJM
C
C======================================================
C.....OUTER ITERATIONS (SIMPLE/PIMPLE loop)
C     OpenFOAM PIMPLE: NOPIMPLE outer + NPISO inner correctors
C     If NOPIMPLE=1, NPISO=1 -> standard SIMPLE
C     If NOPIMPLE=1, NPISO>1 -> PISO
C     If NOPIMPLE>1           -> full PIMPLE
C======================================================
        DO LS=1,LSG(KGR)
C
C.........PIMPLE OUTER CORRECTOR LOOP
C
          DO LOUTER=1,NOPIMPLE
C
C...........STEP 1 - MOMENTUM PREDICTOR
C           Solve U*,V* with current pressure field
C
            IF(LCAL(IU)) CALL CALCUV(KGR)
C
C...........STEP 2 - PISO INNER CORRECTORS
C           Each corrector: mass flux -> p' -> correct U,V,p,flux
C
            DO LPISO=1,NPISO
              IF(LCAL(IP)) CALL CALCP(KGR,1,LPISO)
            END DO
C
          END DO   ! LOUTER
C
C.........STEP 3 - SCALAR EQUATIONS
C
          IF(LCAL(IEN))  CALL CALCSC(KGR,IEN,T,TO,TOO)
          IF(LCAL(ITE))  CALL CALCSC(KGR,ITE,TE,TEO,TEOO)
          IF(LCAL(IED))  CALL CALCSC(KGR,IED,ED,EDO,EDOO)
          IF(LCAL(IGAM)) CALL CALCSC(KGR,IGAM,GAM,GAMO,GAMOO)
          IF(LCAL(IRET)) CALL CALCSC(KGR,IRET,RETHET,
     *                               RETHETO,RETHETOO)
          IF(LCAL(IVIS)) CALL MODVIS_SST(KGR)
C
C.........NORMALIZE RESIDUALS AND PRINT
          DO L=1,NFI
            RESOR(L)=RESOR(L)*RNOR(L)
          END DO
          WRITE(2,606) KGR,LS,LS,(RESOR(I),I=1,NFI),
     *      U(IJMON),V(IJMON),P(IJMON),T(IJMON),
     *      TE(IJMON),ED(IJMON),GAM(IJMON),RETHET(IJMON)
          IF(.NOT.LTIME) WRITE(*,606) KGR,LS,LS,
     *      (RESOR(I),I=1,NFI),
     *      U(IJMON),V(IJMON),P(IJMON),T(IJMON),
     *      TE(IJMON),ED(IJMON),GAM(IJMON),RETHET(IJMON)
C
          SOURCE=MAX(RESOR(IU),RESOR(IV),RESOR(IP),
     *               RESOR(IEN),RESOR(ITE))
          IF(SOURCE.GT.SLARGE) GO TO 510
          IF(SOURCE.LT.SORMAX) GO TO 250
        END DO
C
  250   CONTINUE
C
        IF(LTIME) THEN
          WRITE(*,606) KGR,LS,LS,(RESOR(I),I=1,NFI),
     *      U(IJMON),V(IJMON),P(IJMON),T(IJMON),
     *      TE(IJMON),ED(IJMON),GAM(IJMON),RETHET(IJMON)
          CALL TOUT(KGR)
          IF(MOD(ITIM,NOTT).EQ.0.AND.LWRITE) THEN
            ICONT=ICONT+1
            CALL POST(KGR,ICONT)
            IF(LOUTE) CALL OUTRES(KGR)
            CALL SOUT(KGR)
          ENDIF
        ENDIF
C
  400   CONTINUE
C
        IF(LSG(KGR).GT.0) THEN
          ICONT=ICONT+1
          CALL POST(KGR,ICONT)
          IF(LOUTE) CALL OUTRES(KGR)
          CALL SOUT(KGR)
          CALL SRES(KGR)
          IF(LTIME) CLOSE(UNIT=10)
          ITIM=0; TIME=0.
        ENDIF
C
  500 CONTINUE
C
      CLOSE(UNIT=8); CLOSE(UNIT=3)
      CLOSE(UNIT=4); CLOSE(UNIT=2); CLOSE(UNIT=5)
      PRINT *,'     *** CALCULATION FINISHED ***'
      STOP
C
  510 PRINT *,'     *** TERMINATED - DIVERGING ***'
      STOP
C
  600 FORMAT(1X,'GRID',1X,'CYCLE',1X,'ITER',2X,
     * 'I----------RESIDUALS----------I',
     * 'I----MONITORING(',I3,',',I3,')----I',/,
     * 1X,3('NO',4X),1X,'UMOM  VMOM  MASS  ENER',
     * '  KINE  DISE  GAMM  RETH  EVIS',
     * 4X,'U   V   P   T   k   om  gam  ret'/)
  606 FORMAT(1X,I2,3X,I3,2X,I4,3X,1P11E9.2,4X,1P8E9.2)
C
      END
C##########################################################
      SUBROUTINE INJECT(K,FI)
C##########################################################
C     Zero-order injection of coarse->fine grid (turbulence).
C==========================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'grad.inc'
      DIMENSION FI(NXYA)
      CALL SETIND(K)
      NJF=NJGR(K+1); ISTF=IGR(K+1)
      DO IG=2,NIM
        IF=2*IG-2
        DO JG=2,NJM
          IJG=LI(IG+IST)+JG; JF=2*JG-2
          IJF=LI(IF+ISTF)+JF
          FI(IJF)=FI(IJG);   FI(IJF+1)=FI(IJG)
          FI(IJF+NJF)=FI(IJG); FI(IJF+NJF+1)=FI(IJG)
        END DO
      END DO
      RETURN
      END
C
C##########################################################
      SUBROUTINE VINT(K,FI)
C##########################################################
C     First-order interpolation coarse->fine using gradient.
C==========================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'grad.inc'
      DIMENSION FI(NXYA)
      CALL SETIND(K)
      CALL GRADFI(K,FI,DUX,DUY)
      NJF=NJGR(K+1); ISTF=IGR(K+1)
      DO IG=2,NIM
        IF=2*IG-2
        DO JG=2,NJM
          IJG=LI(IG+IST)+JG; JF=2*JG-2
          IJF=LI(IF+ISTF)+JF
          FI(IJF)     =FI(IJG)+FICF(IJG,IJF)
          FI(IJF+1)   =FI(IJG)+FICF(IJG,IJF+1)
          FI(IJF+NJF) =FI(IJG)+FICF(IJG,IJF+NJF)
          FI(IJF+NJF+1)=FI(IJG)+FICF(IJG,IJF+NJF+1)
        END DO
      END DO
      RETURN
      END
C
C##########################################################
      FUNCTION FICF(IJG,IJF)
C##########################################################
      INCLUDE 'param.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'grad.inc'
      FICF=DUX(IJG)*(XC(IJF)-XC(IJG))+DUY(IJG)*(YC(IJF)-YC(IJG))
      RETURN
      END
C
C##########################################################
      SUBROUTINE MODVEL(K)
C##########################################################
C     Fictitious wall velocities for grid-to-grid transfer.
C==========================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'bound.inc'
      INCLUDE 'var.inc'
      INCLUDE 'model.inc'
      DO IW=IWS(K)+1,IWS(K)+NWAL(K)
        IJB=IJW(IW); IJP=IJPW(IW)
        CK=CMU25*SQRT(MAX(ZERO,TE(IJP)))
        CKK=CK/CAPPA
        VECPP=U(IJP)*XTW(IW)+V(IJP)*YTW(IW)
        VECPW=VECPP-CKK
        IF(ABS(VECPW).GT.ABS(VECPP)) VECPW=VECPP+CKK
        U(IJB)=VECPW*XTW(IW); V(IJB)=VECPW*YTW(IW)
      END DO
      RETURN
      END
C##########################################################
      SUBROUTINE CALCUV(K)
C##########################################################
C     Discretizes and solves the linearized momentum equations.
C     Supports ISCHEME: 1=UDS/CDS  2=QUICK  3=linUpwind  4=linUpwindV
C     Applies cellMDlimiter to velocity gradients when ILIMIT=1.
C=========================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'logic.inc'
      INCLUDE 'rcont.inc'
      INCLUDE 'var.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'coef.inc'
      INCLUDE 'varold.inc'
      INCLUDE 'grad.inc'
      INCLUDE 'bound.inc'
      INCLUDE 'model.inc'
C
      CALL SETIND(K)
C
C.....COMPUTE GRADIENTS FOR U, V, P
      CALL GRADFI(K,U,DUX,DUY)
      CALL GRADFI(K,V,DVX,DVY)
      CALL GRADFI(K,P,DPX,DPY)
C
C.....APPLY cellMDlimiter TO VELOCITY GRADIENTS (if requested)
      IF(ILIMIT.EQ.1) THEN
        CALL CELLMDLIM(K,U,DUX,DUY)
        CALL CELLMDLIM(K,V,DVX,DVY)
      ENDIF
C
      IJST=IJGR(K)+1; IJEN=IJGR(K)+NIJ
      DO IJ=IJST,IJEN
        SU(IJ)=0.; SV(IJ)=0.; AP(IJ)=0.; APR(IJ)=0.
      END DO
      GU=GDS(IU)
C
C.....EAST FACES
      DO I=2,NIM-1
      DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
        CALL FLUXUV(IJ,IJ+NJ,IJ,IJ-1,F1(IJ),
     *    AW(IJ+NJ),AE(IJ),FX(IJ),GU,ISCHEME)
      END DO
      END DO
C
C.....NORTH FACES
      DO I=2,NIM
      DO IJ=LI(I+IST)+2,LI(I+IST)+NJM-1
        CALL FLUXUV(IJ,IJ+1,IJ-NJ,IJ,F2(IJ),
     *    AS(IJ+1),AN(IJ),FY(IJ),GU,ISCHEME)
      END DO
      END DO
C
C.....BUOYANCY
      IF(LCAL(IEN)) THEN
        DO I=2,NIM
        DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
          SB=BETA*DEN(IJ)*VOL(IJ)*(T(IJ)-TREF)
          SU(IJ)=SU(IJ)+GRAVX*SB; SV(IJ)=SV(IJ)+GRAVY*SB
        END DO; END DO
      ENDIF
C
C.....AXISYMMETRIC
      IF(LAXIS) THEN
        DO I=2,NIM
        DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
          RCR=4./(R(IJ)+R(IJ-1)+R(IJ-NJ)+R(IJ-NJ-1))
          APR(IJ)=APR(IJ)+2.*VIS(IJ)*VOL(IJ)*RCR**2
        END DO; END DO
      ENDIF
C
C.....PRESSURE SOURCE
      DO I=2,NIM
      DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
        SU(IJ)=SU(IJ)-DPX(IJ)*VOL(IJ)
        SV(IJ)=SV(IJ)-DPY(IJ)*VOL(IJ)
      END DO; END DO
C
C.....UNSTEADY TERM (implicit Euler: GAMT=0; 3-level: GAMT=1)
      IF(LTIME) THEN
        DO I=2,NIM
        DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
          APT=DEN(IJ)*VOL(IJ)*DTR
          SU(IJ)=SU(IJ)+APT*((1.+GAMT)*UO(IJ)-0.5*GAMT*UOO(IJ))
          SV(IJ)=SV(IJ)+APT*((1.+GAMT)*VO(IJ)-0.5*GAMT*VOO(IJ))
          APR(IJ)=APR(IJ)+APT*(1.+0.5*GAMT)
          AP(IJ) = AP(IJ)+APT*(1.+0.5*GAMT)
        END DO; END DO
      ENDIF
C
C.....INLET BOUNDARIES
      DO II=IIS(K)+1,IIS(K)+NINL(K)
        IJP=IJPI(II); IJB=IJI(II)
        DUX(IJB)=DUX(IJP); DUY(IJB)=DUY(IJP)
        DVX(IJB)=DVX(IJP); DVY(IJB)=DVY(IJP)
        CALL FLUXUV(IJP,IJB,IJI1(II),IJI2(II),FMI(II),
     *    CP,CB,ONE,ZERO,1)
        AP(IJP)=AP(IJP)-CB; APR(IJP)=APR(IJP)-CB
        SU(IJP)=SU(IJP)-CB*U(IJB)
        SV(IJP)=SV(IJP)-CB*V(IJB)
      END DO
C
C.....OUTLET BOUNDARIES
      DO IO=IOS(K)+1,IOS(K)+NOUT(K)
        IJP=IJPO(IO); IJB=IJO(IO)
        DUX(IJB)=DUX(IJP); DUY(IJB)=DUY(IJP)
        DVX(IJB)=DVX(IJP); DVY(IJB)=DVY(IJP)
        CALL FLUXUV(IJP,IJB,IJO1(IO),IJO2(IO),FMO(IO),
     *    CP,CB,ONE,ZERO,1)
        AP(IJP)=AP(IJP)-CB; APR(IJP)=APR(IJP)-CB
        SU(IJP)=SU(IJP)-CB*U(IJB)
        SV(IJP)=SV(IJP)-CB*V(IJB)
      END DO
C
C.....WALL BOUNDARIES
      DO IW=IWS(K)+1,IWS(K)+NWAL(K)
        IJP=IJPW(IW); IJB=IJW(IW)
        VISS=VISC
        IF(LCAL(ITE).AND.YPL(IW).GT.CTRANS) VISS=VISW(IW)
        COEF=VISS*SRDW(IW)
        AP(IJP) =AP(IJP) +COEF*XTW(IW)**2
        APR(IJP)=APR(IJP)+COEF*YTW(IW)**2
        SU(IJP)=SU(IJP)+COEF*(U(IJB)*XTW(IW)**2
     *         -(V(IJP)-V(IJB))*XTW(IW)*YTW(IW))
        SV(IJP)=SV(IJP)+COEF*(V(IJB)*YTW(IW)**2
     *         -(U(IJP)-U(IJB))*XTW(IW)*YTW(IW))
      END DO
C
C.....SYMMETRY BOUNDARIES
      DO IS=ISS(K)+1,ISS(K)+NSYM(K)
        IJP=IJPS(IS); IJB=IJS(IS)
        C1=2.*XNS(IS)*YNS(IS)
        COEF=VIS(IJB)*SRDS(IS)
        AP(IJP) =AP(IJP) +COEF*XNS(IS)**2
        APR(IJP)=APR(IJP)+COEF*YNS(IS)**2
        SU(IJP)=SU(IJP)-COEF*(C1*V(IJP)+U(IJP)*XNS(IS)**2)
        SV(IJP)=SV(IJP)-COEF*(C1*U(IJP)+V(IJP)*YNS(IS)**2)
      END DO
C
C.....O- AND C-GRID CUTS
      DO I=IOCS(K)+1,IOCS(K)+NOC(K)
        IJP=IJL(I); IJN=IJR(I)
        CALL FLUXUV(IJP,IJN,IJOC1(I),IJOC2(I),FMOC(I),
     *    AL(I),AR(I),FOC(I),GU,ISCHEME)
        AP(IJP) =AP(IJP) -AR(I); APR(IJP)=APR(IJP)-AR(I)
        AP(IJN) =AP(IJN) -AL(I); APR(IJN)=APR(IJN)-AL(I)
      END DO
C
C.....FINAL COEFFICIENT MATRIX FOR U
C     SIMPLEC: use (AP - sumNB) as denominator -> faster p-v coupling
      DO I=2,NIM
      DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
        SUMNB=AE(IJ)+AW(IJ)+AN(IJ)+AS(IJ)
        IF(LSIMPLEC) THEN
          AP(IJ)=(AP(IJ)-SUMNB)*URFU
        ELSE
          AP(IJ)=(AP(IJ)-AE(IJ)-AW(IJ)-AN(IJ)-AS(IJ))*URFU
        ENDIF
        SU(IJ)=SU(IJ)+(1.-URF(IU))*AP(IJ)*U(IJ)
      END DO; END DO
C
C.....SOLVE U
      IF(LGMRES) THEN
        CALL GMRESSOL(U,IU,K)
      ELSE
        CALL SIPSOL(U,IU,K)
      ENDIF
C
C.....FINAL COEFFICIENT MATRIX FOR V
      DO I=2,NIM
      DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
        SUMNB=AE(IJ)+AW(IJ)+AN(IJ)+AS(IJ)
        IF(LSIMPLEC) THEN
          AP(IJ)=(APR(IJ)-SUMNB)*URFV
        ELSE
          AP(IJ)=(APR(IJ)-AE(IJ)-AW(IJ)-AN(IJ)-AS(IJ))*URFV
        ENDIF
        SU(IJ)=SV(IJ)+(1.-URF(IV))*AP(IJ)*V(IJ)
        APR(IJ)=1./(AP(IJ)+SMALL)
      END DO; END DO
C
C.....SOLVE V
      IF(LGMRES) THEN
        CALL GMRESSOL(V,IV,K)
      ELSE
        CALL SIPSOL(V,IV,K)
      ENDIF
C
      RETURN
      END
C################################################################
      SUBROUTINE FLUXUV(IJP,IJN,IJ1,IJ2,FM,CAP,CAN,FAC,G,ISCH)
C################################################################
C     Convective+diffusive momentum fluxes through one face.
C
C     ISCH=1: UDS/CDS blend (original CAFFA deferred correction)
C     ISCH=2: QUICK 3rd-order upwind-biased scheme
C     ISCH=3: linearUpwind  (1st+grad reconstruction, scalar)
C     ISCH=4: linearUpwindV (1st+grad reconstruction, vector;
C             uses full velocity-gradient tensor consistently)
C
C     Surface vector S points from IJP toward IJN.
C     Diffusive fluxes always use central differences.
C     Convective high-order contribution added as deferred correction.
C==============================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'var.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'grad.inc'
      INCLUDE 'coef.inc'
      INCLUDE 'rcont.inc'
C
      FACP=1.-FAC
C
C.....INTERPOLATE GRADIENTS TO FACE MIDPOINT (line IJP-IJN)
      DUXI=DUX(IJN)*FAC+DUX(IJP)*FACP
      DVXI=DVX(IJN)*FAC+DVX(IJP)*FACP
      DUYI=DUY(IJN)*FAC+DUY(IJP)*FACP
      DVYI=DVY(IJN)*FAC+DVY(IJP)*FACP
      XI=XC(IJN)*FAC+XC(IJP)*FACP
      YI=YC(IJN)*FAC+YC(IJP)*FACP
C
C.....FACE CENTRE COORDINATES
      XF=0.5*(X(IJ2)+X(IJ1)); YF=0.5*(Y(IJ2)+Y(IJ1))
C
C.....FACE VELOCITY AND VISCOSITY (central interpolation)
      UI=U(IJN)*FAC+U(IJP)*FACP+DUXI*(XF-XI)+DUYI*(YF-YI)
      VI=V(IJN)*FAC+V(IJP)*FACP+DVXI*(XF-XI)+DVYI*(YF-YI)
      VISI=VIS(IJN)*FAC+VIS(IJP)*FACP
C
C.....SURFACE AND DISTANCE VECTORS
      RC=0.5*(R(IJ1)+R(IJ2))
      SX=(Y(IJ1)-Y(IJ2))*RC;  SY=(X(IJ2)-X(IJ1))*RC
      XPN=XC(IJN)-XC(IJP);    YPN=YC(IJN)-YC(IJP)
      VSOL=VISI*SQRT((SX**2+SY**2)/(XPN**2+YPN**2+SMALL))
C
C.....DIFFUSIVE FLUXES (central differences, always)
      FDUE=VISI*(2.*DUXI*SX+(DUYI+DVXI)*SY)
      FDVE=VISI*((DUYI+DVXI)*SX+2.*DVYI*SY)
      FDUI=VSOL*(DUXI*XPN+DUYI*YPN)
      FDVI=VSOL*(DVXI*XPN+DVYI*YPN)
C
C.....IMPLICIT UPWIND CONVECTIVE FLUXES (1st-order base)
      FCUI=MIN(FM,ZERO)*U(IJN)+MAX(FM,ZERO)*U(IJP)
      FCVI=MIN(FM,ZERO)*V(IJN)+MAX(FM,ZERO)*V(IJP)
C
C.....HIGH-ORDER CONVECTIVE FLUXES (scheme-specific explicit part)
      IF(ISCH.EQ.2) THEN
C
C.......QUICK (Leonard 1979)
C       phi_f = 3/8*phi_D + 6/8*phi_C - 1/8*phi_UU  (uniform 1D)
C       On non-uniform grids: use gradient extrapolation for UU contribution
C       phi_f = phi_C + (phi_D-phi_C)*FAC
C              - (1/8)*(phi_D - 2*phi_C + phi_UU)  [curvature correction]
C       We approximate phi_UU via upstream gradient:
C         phi_UU ~ phi_C - grad_C . (x_D - x_C)
C
        IF(FM.GE.ZERO) THEN
C         Upwind=P, Downwind=N
          UPHIC=U(IJP)+DUX(IJP)*(XF-XC(IJP))+DUY(IJP)*(YF-YC(IJP))
          VPHIC=V(IJP)+DVX(IJP)*(XF-XC(IJP))+DVY(IJP)*(YF-YC(IJP))
          UPHID=U(IJN); VPHID=V(IJN)
          UUREC=U(IJP)-DUX(IJP)*(XC(IJN)-XC(IJP))
     *               -DUY(IJP)*(YC(IJN)-YC(IJP))
          VUREC=V(IJP)-DVX(IJP)*(XC(IJN)-XC(IJP))
     *               -DVY(IJP)*(YC(IJN)-YC(IJP))
          UF_Q=0.75*U(IJP)+0.375*(U(IJN)-U(IJP))*FAC
     *        +0.125*UUREC
          VF_Q=0.75*V(IJP)+0.375*(V(IJN)-V(IJP))*FAC
     *        +0.125*VUREC
        ELSE
C         Upwind=N, Downwind=P
          UUREC=U(IJN)-DUX(IJN)*(XC(IJP)-XC(IJN))
     *               -DUY(IJN)*(YC(IJP)-YC(IJN))
          VUREC=V(IJN)-DVX(IJN)*(XC(IJP)-XC(IJN))
     *               -DVY(IJN)*(YC(IJP)-YC(IJN))
          UF_Q=0.75*U(IJN)+0.375*(U(IJP)-U(IJN))*(1.-FAC)
     *        +0.125*UUREC
          VF_Q=0.75*V(IJN)+0.375*(V(IJP)-V(IJN))*(1.-FAC)
     *        +0.125*VUREC
        ENDIF
        FCUE=FM*UF_Q; FCVE=FM*VF_Q
C
      ELSEIF(ISCH.EQ.3) THEN
C
C.......linearUpwind  (scalar treatment - grad reconstructed independently)
C       phi_f = phi_C + grad(phi_C) . (x_f - x_C)
C
        IF(FM.GE.ZERO) THEN
          UF_L=U(IJP)+DUX(IJP)*(XF-XC(IJP))+DUY(IJP)*(YF-YC(IJP))
          VF_L=V(IJP)+DVX(IJP)*(XF-XC(IJP))+DVY(IJP)*(YF-YC(IJP))
        ELSE
          UF_L=U(IJN)+DUX(IJN)*(XF-XC(IJN))+DUY(IJN)*(YF-YC(IJN))
          VF_L=V(IJN)+DVX(IJN)*(XF-XC(IJN))+DVY(IJN)*(YF-YC(IJN))
        ENDIF
        FCUE=FM*UF_L; FCVE=FM*VF_L
C
      ELSEIF(ISCH.EQ.4) THEN
C
C.......linearUpwindV (vector treatment - velocity gradient tensor)
C       U_f = U_C + (gradU_C)^T . (x_f - x_C)
C       Consistent: uses full velocity-gradient tensor (not separate grads)
C       gradU = [[dU/dx, dU/dy],[dV/dx, dV/dy]]
C
        DX=XF-XC(IJP); DY=YF-YC(IJP)
        IF(FM.GE.ZERO) THEN
          DX=XF-XC(IJP); DY=YF-YC(IJP)
          UF_LV=U(IJP)+DUX(IJP)*DX+DUY(IJP)*DY
          VF_LV=V(IJP)+DVX(IJP)*DX+DVY(IJP)*DY
        ELSE
          DX=XF-XC(IJN); DY=YF-YC(IJN)
          UF_LV=U(IJN)+DUX(IJN)*DX+DUY(IJN)*DY
          VF_LV=V(IJN)+DVX(IJN)*DX+DVY(IJN)*DY
        ENDIF
        FCUE=FM*UF_LV; FCVE=FM*VF_LV
C
      ELSE
C
C.......UDS/CDS BLEND (default, original CAFFA)
        FCUE=FM*UI; FCVE=FM*VI
C
      ENDIF
C
C.....COEFFICIENTS
      CAN=-VSOL+MIN(FM,ZERO)
      CAP=-VSOL-MAX(FM,ZERO)
C
C.....DEFERRED CORRECTION + SOURCE
      FUC=G*(FCUE-FCUI)
      FVC=G*(FCVE-FCVI)
      SU(IJP)=SU(IJP)-FUC+FDUE-FDUI
      SU(IJN)=SU(IJN)+FUC-FDUE+FDUI
      SV(IJP)=SV(IJP)-FVC+FDVE-FDVI
      SV(IJN)=SV(IJN)+FVC-FDVE+FDVI
C
      RETURN
      END
C##############################################################
      SUBROUTINE CALCP(K,INTMF,LPISO)
C##############################################################
C     Assembles and solves the pressure-correction equation.
C
C     PIMPLE/PISO variant of the Rhie-Chow interpolation:
C       - For SIMPLEC: effective denominator = AP - sumNB
C         (Vandoormaal & Raithby 1984; Van Doormaal 1987)
C       - For standard SIMPLE: denominator = AP
C
C     PIMPLE workflow (called from main loop):
C       LPISO=1..NPISO inner correctors; URF on P applied
C       only in last corrector (LPISO=NPISO) when NOPIMPLE=1.
C       For PIMPLE (NOPIMPLE>1): URF(IP)=1 for all correctors.
C==============================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'logic.inc'
      INCLUDE 'rcont.inc'
      INCLUDE 'var.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'coef.inc'
      INCLUDE 'grad.inc'
      INCLUDE 'bound.inc'
      INCLUDE 'varold.inc'
C
      CALL SETIND(K)
      IJST=IJGR(K)+1; IJEN=IJGR(K)+NIJ
      SUM=0.
      DO IJ=IJST,IJEN
        SU(IJ)=0.; AP(IJ)=0.
      END DO
C
C.....MASS FLUXES: EAST FACES
      DO I=2,NIM-1
      DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
        CALL FLUXM(IJ,IJ+NJ,IJ,IJ-1,F1(IJ),
     *    AW(IJ+NJ),AE(IJ),FX(IJ))
      END DO; END DO
C
C.....MASS FLUXES: NORTH FACES
      DO I=2,NIM
      DO IJ=LI(I+IST)+2,LI(I+IST)+NJM-1
        CALL FLUXM(IJ,IJ+1,IJ-NJ,IJ,F2(IJ),
     *    AS(IJ+1),AN(IJ),FY(IJ))
      END DO; END DO
C
C.....O/C-GRID CUTS
      DO I=IOCS(K)+1,IOCS(K)+NOC(K)
        IJP=IJL(I); IJN=IJR(I)
        CALL FLUXM(IJP,IJN,IJOC1(I),IJOC2(I),FMOC(I),
     *    AL(I),AR(I),FOC(I))
        AP(IJP)=AP(IJP)-AR(I); AP(IJN)=AP(IJN)-AL(I)
        SU(IJP)=SU(IJP)-FMOC(I); SU(IJN)=SU(IJN)+FMOC(I)
      END DO
C
      IF(INTMF.EQ.0) RETURN
C
C.....INLET MASS SOURCES
      DO II=IIS(K)+1,IIS(K)+NINL(K)
        SU(IJPI(II))=SU(IJPI(II))-FMI(II)
      END DO
C
C.....OUTLET: EXTRAPOLATE VELOCITY, COMPUTE FLUX
      FLOWO=0.
      DO IO=IOS(K)+1,IOS(K)+NOUT(K)
        IJB=IJO(IO); IJP=IJPO(IO)
        U(IJB)=U(IJP); V(IJB)=V(IJP)
        RS=0.5*(R(IJO1(IO))+R(IJO2(IO)))
        SX=(Y(IJO1(IO))-Y(IJO2(IO)))
        SY=(X(IJO2(IO))-X(IJO1(IO)))
        FMO(IO)=DEN(IJP)*(U(IJB)*SX+V(IJB)*SY)*RS
        FLOWO=FLOWO+FMO(IO)
      END DO
C
C.....GLOBAL MASS CONSERVATION CORRECTION
      FAC=FLOMAS/(FLOWO+SMALL)
      DO IO=IOS(K)+1,IOS(K)+NOUT(K)
        IB=IJO(IO)
        FMO(IO)=FMO(IO)*FAC
        U(IB)=U(IB)*FAC; V(IB)=V(IB)*FAC
        SU(IJPO(IO))=SU(IJPO(IO))-FMO(IO)
      END DO
C
C.....ASSEMBLE SOURCE (mass imbalance) AND CENTRAL COEFFICIENT
      DO I=2,NIM
        DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
          PP(IJ)=0.
          SU(IJ)=SU(IJ)+F1(IJ-NJ)-F1(IJ)+F2(IJ-1)-F2(IJ)
          AP(IJ)=AP(IJ)-AE(IJ)-AW(IJ)-AN(IJ)-AS(IJ)
          SUM=SUM+SU(IJ)
        END DO
      END DO
C
      IF(LTEST) WRITE(2,*) '    MASS IMBALANCE = ',SUM
C
C.....SOLVE PRESSURE-CORRECTION EQUATION
      DO LC=1,NPCOR
C
        CALL SIPSOL(PP,IP,K)
        CALL PRESB(K,PP)
        CALL GRADFI(K,PP,DPX,DPY)
        PPO=PP(IJPR)
C
C.......CORRECT EAST MASS FLUXES
        DO I=2,NIM-1
          DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
            F1(IJ)=F1(IJ)+AE(IJ)*(PP(IJ+NJ)-PP(IJ))
          END DO
        END DO
C
C.......CORRECT NORTH MASS FLUXES
        DO I=2,NIM
          DO IJ=LI(I+IST)+2,LI(I+IST)+NJM-1
            F2(IJ)=F2(IJ)+AN(IJ)*(PP(IJ+1)-PP(IJ))
          END DO
        END DO
C
C.......CORRECT PERIODIC-CUT FLUXES
        DO I=IOCS(K)+1,IOCS(K)+NOC(K)
          FMOC(I)=FMOC(I)+AR(I)*(PP(IJR(I))-PP(IJL(I)))
        END DO
C
C.......CORRECT VELOCITY AND PRESSURE
C       PIMPLE outer mode: apply URF=1.0 for inner correctors
C       SIMPLE mode: apply URF(IP) always
        IF(NOPIMPLE.GT.1) THEN
          PURFA=1.0
        ELSE
          IF(LPISO.LT.NPISO) THEN
            PURFA=1.0
          ELSE
            PURFA=URF(IP)
          ENDIF
        ENDIF
C
        DO I=2,NIM
          DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
            U(IJ)=U(IJ)-DPX(IJ)*VOL(IJ)*APR(IJ)
            V(IJ)=V(IJ)-DPY(IJ)*VOL(IJ)*APR(IJ)
            P(IJ)=P(IJ)+PURFA*(PP(IJ)-PPO)
          END DO
        END DO
C
      END DO
C
      CALL PRESB(K,P)
C
C.....UPDATE SYMMETRY BOUNDARY VELOCITIES
      DO IS=ISS(K)+1,ISS(K)+NSYM(K)
        IJP=IJPS(IS); IJB=IJS(IS)
        UN=U(IJP)*XNS(IS)+V(IJP)*YNS(IS)
        U(IJB)=U(IJP)-UN*XNS(IS)
        V(IJB)=V(IJP)-UN*YNS(IS)
      END DO
C
      RETURN
      END
C
C
C##############################################################
      SUBROUTINE FLUXM(IJP,IJN,IJ1,IJ2,FM,CAP,CAN,FAC)
C##############################################################
C     Computes mass flux through cell face (Rhie-Chow interpolation).
C     SIMPLEC: effective momentum equation coefficient =
C              AP - sumNB  (faster convergence for p-v coupling)
C     SIMPLE:  effective coefficient = AP
C==============================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'logic.inc'
      INCLUDE 'rcont.inc'
      INCLUDE 'var.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'grad.inc'
      INCLUDE 'coef.inc'
C
      FACP=1.-FAC
      XI=XC(IJN)*FAC+XC(IJP)*FACP
      YI=YC(IJN)*FAC+YC(IJP)*FACP
      DUXI=DUX(IJN)*FAC+DUX(IJP)*FACP
      DVXI=DVX(IJN)*FAC+DVX(IJP)*FACP
      DUYI=DUY(IJN)*FAC+DUY(IJP)*FACP
      DVYI=DVY(IJN)*FAC+DVY(IJP)*FACP
      XF=0.5*(X(IJ2)+X(IJ1)); YF=0.5*(Y(IJ2)+Y(IJ1))
      UI=U(IJN)*FAC+U(IJP)*FACP+DUXI*(XF-XI)+DUYI*(YF-YI)
      VI=V(IJN)*FAC+V(IJP)*FACP+DVXI*(XF-XI)+DVYI*(YF-YI)
      DENI=DEN(IJN)*FAC+DEN(IJP)*FACP
      RC=0.5*(R(IJ1)+R(IJ2))
      SX=(Y(IJ1)-Y(IJ2))*RC; SY=(X(IJ2)-X(IJ1))*RC
      XPN=XC(IJN)-XC(IJP); YPN=YC(IJN)-YC(IJP)
      SMDPN=(SX**2+SY**2)/(SX*XPN+SY*YPN+SMALL)
C
C.....SIMPLEC vs SIMPLE: choose effective AP for pressure coupling
C     SIMPLEC: APeff = AP - sumNB  (Vandoormaal & Raithby 1984)
C     SIMPLE:  APeff = AP
      IF(LSIMPLEC) THEN
        SNBP=AE(IJP)+AW(IJP)+AN(IJP)+AS(IJP)
        SNBN=AE(IJN)+AW(IJN)+AN(IJN)+AS(IJN)
        APEFP=AP(IJP)-SNBP
        APEFN=AP(IJN)-SNBN
        IF(ABS(APEFP).LT.SMALL) APEFP=AP(IJP)
        IF(ABS(APEFN).LT.SMALL) APEFN=AP(IJN)
        APRP=1./(APEFP+SMALL)
        APRN=1./(APEFN+SMALL)
      ELSE
        APRP=APR(IJP); APRN=APR(IJN)
      ENDIF
C
      CAP=-0.5*(VOL(IJP)*APRP+VOL(IJN)*APRN)*DENI*SMDPN
      CAN=CAP
      DPXI=0.5*(DPX(IJN)+DPX(IJP))*XPN
      DPYI=0.5*(DPY(IJN)+DPY(IJP))*YPN
      FM=DENI*(UI*SX+VI*SY)+CAP*(P(IJN)-P(IJP)-DPXI-DPYI)
C
      RETURN
      END
C###############################################################
      SUBROUTINE PRESB(K,FI)
C###############################################################
C     Linear extrapolation of pressure (or p') to boundaries.
C==============================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'logic.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'model.inc'
      DIMENSION FI(NXYA)
      CALL SETIND(K)
      DO I=2,NIM
        IJ=LI(I+IST)+1
        FI(IJ)=FI(IJ+1)+(FI(IJ+1)-FI(IJ+2))*FY(IJ+1)
        IJ=LI(I+IST)+NJ
        FI(IJ)=FI(IJ-1)+(FI(IJ-1)-FI(IJ-2))*(1.-FY(IJ-2))
      END DO
      DO J=2,NJM
        IJ=LI(1+IST)+J
        FI(IJ)=FI(IJ+NJ)+(FI(IJ+NJ)-FI(IJ+NJ+NJ))*FX(IJ+NJ)
        IJ=LI(NI+IST)+J
        FI(IJ)=FI(IJ-NJ)+(FI(IJ-NJ)-FI(IJ-NJ-NJ))*(1.-FX(IJ-NJ-NJ))
      END DO
      RETURN
      END
C
C
C###############################################################
      SUBROUTINE GRADFI(K,FI,DFX,DFY)
C###############################################################
C     Iterative gradient computation using Gauss theorem.
C     Handles non-orthogonality via iterative correction.
C     See Ferziger-Peric 4th Ed., Ch. 8.6.
C===============================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'var.inc'
      INCLUDE 'logic.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'bound.inc'
      INCLUDE 'rcont.inc'
      DIMENSION FI(NXYA),DFX(NXYA),DFY(NXYA)
      COMMON /GROLD/ DFXO(NXYA),DFYO(NXYA)
C
      IJST=IJGR(K)+1; IJEN=IJGR(K)+NIJ
      DO IJ=IJST,IJEN
        DFXO(IJ)=0.; DFYO(IJ)=0.
      END DO
C
      DO LC=1,NIGRAD
C
        DO IJ=IJST,IJEN
          DFX(IJ)=0.; DFY(IJ)=0.
        END DO
C
        DO I=2,NIM-1
          DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
            CALL GRADCO(FI,DFX,DFY,FX(IJ),IJ,IJ+NJ,IJ,IJ-1)
          END DO
        END DO
C
        DO I=2,NIM
          DO IJ=LI(I+IST)+2,LI(I+IST)+NJM-1
            CALL GRADCO(FI,DFX,DFY,FY(IJ),IJ,IJ+1,IJ-NJ,IJ)
          END DO
        END DO
C
        DO I=IOCS(K)+1,IOCS(K)+NOC(K)
          CALL GRADCO(FI,DFX,DFY,FOC(I),IJL(I),IJR(I),
     *      IJOC1(I),IJOC2(I))
        END DO
C
        DO I=IIS(K)+1,IIS(K)+NINL(K)
          CALL GRADBC(IJPI(I),IJI(I),IJI1(I),IJI2(I),DFX,DFY,FI)
        END DO
        DO I=IOS(K)+1,IOS(K)+NOUT(K)
          CALL GRADBC(IJPO(I),IJO(I),IJO1(I),IJO2(I),DFX,DFY,FI)
        END DO
        DO I=ISS(K)+1,ISS(K)+NSYM(K)
          CALL GRADBC(IJPS(I),IJS(I),IJS1(I),IJS2(I),DFX,DFY,FI)
        END DO
        DO I=IWS(K)+1,IWS(K)+NWAL(K)
          CALL GRADBC(IJPW(I),IJW(I),IJW1(I),IJW2(I),DFX,DFY,FI)
        END DO
C
        IF(LAXIS) THEN
          DO I=2,NIM
            DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
              AREA=0.5*((X(IJ)-X(IJ-NJ-1))*(Y(IJ-NJ)-Y(IJ-1))
     *                 -(Y(IJ)-Y(IJ-NJ-1))*(X(IJ-NJ)-X(IJ-1)))
              DFY(IJ)=DFY(IJ)-FI(IJ)*AREA
            END DO
          END DO
        ENDIF
C
        DO I=2,NIM
          DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
            DFX(IJ)=DFX(IJ)/VOL(IJ); DFY(IJ)=DFY(IJ)/VOL(IJ)
          END DO
        END DO
C
        IF(LC.NE.NIGRAD) THEN
          DO IJ=IJST,IJEN
            DFXO(IJ)=DFX(IJ); DFYO(IJ)=DFY(IJ)
          END DO
        ENDIF
C
      END DO
      RETURN
      END
C
C##############################################################
      SUBROUTINE GRADCO(FI,DFX,DFY,FAC,IJP,IJN,IJ1,IJ2)
C##############################################################
C     Contribution of one inner face to gradient (Gauss theorem).
C==============================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'var.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'bound.inc'
      DIMENSION FI(NXYA),DFX(NXYA),DFY(NXYA)
      COMMON /GROLD/ DFXO(NXYA),DFYO(NXYA)
      FACP=1.-FAC
      XI=XC(IJN)*FAC+XC(IJP)*FACP
      YI=YC(IJN)*FAC+YC(IJP)*FACP
      DFXI=DFXO(IJN)*FAC+DFXO(IJP)*FACP
      DFYI=DFYO(IJN)*FAC+DFYO(IJP)*FACP
      XF=0.5*(X(IJ1)+X(IJ2)); YF=0.5*(Y(IJ1)+Y(IJ2))
      FIE=FI(IJN)*FAC+FI(IJP)*FACP+DFXI*(XF-XI)+DFYI*(YF-YI)
      RE=(R(IJ1)+R(IJ2))*0.5
      SX=(Y(IJ1)-Y(IJ2))*RE; SY=(X(IJ2)-X(IJ1))*RE
      DFXE=FIE*SX; DFYE=FIE*SY
      DFX(IJP)=DFX(IJP)+DFXE; DFY(IJP)=DFY(IJP)+DFYE
      DFX(IJN)=DFX(IJN)-DFXE; DFY(IJN)=DFY(IJN)-DFYE
      RETURN
      END
C
C########################################################
      SUBROUTINE GRADBC(IJP,IJB,IJ1,IJ2,DFX,DFY,FI)
C########################################################
      INCLUDE 'param.inc'
      INCLUDE 'geo.inc'
      DIMENSION FI(NXYA),DFX(NXYA),DFY(NXYA)
      RB=0.5*(R(IJ1)+R(IJ2))
      SX=(Y(IJ1)-Y(IJ2))*RB; SY=(X(IJ2)-X(IJ1))*RB
      DFX(IJP)=DFX(IJP)+FI(IJB)*SX
      DFY(IJP)=DFY(IJP)+FI(IJB)*SY
      RETURN
      END
C##############################################################
      SUBROUTINE CELLMDLIM(K,FI,DFX,DFY)
C##############################################################
C     Multidimensional slope limiter (cellMDlimiter from OpenFOAM).
C
C     Based on Barth & Jespersen (1989) limiter concept,
C     extended to unstructured/non-orthogonal meshes.
C
C     For each cell P:
C       1) Find phi_max, phi_min over all face-sharing neighbors
C       2) For each face f, compute reconstructed face value:
C             phi_f^rec = phi_P + grad_P . (x_f - x_P)
C       3) Compute ratio:
C             r_f = (phi_max - phi_P)/(phi_f^rec - phi_P) if overshoot
C             r_f = (phi_min - phi_P)/(phi_f^rec - phi_P) if undershoot
C             r_f = 1 otherwise
C       4) Cell limiter: psi_P = min(1, min_f(r_f))
C       5) Limited gradient: grad_P^lim = psi_P * grad_P
C
C     This ensures bounded face values while preserving accuracy
C     where the solution is smooth.
C==============================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'rcont.inc'
      INCLUDE 'var.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'bound.inc'
      DIMENSION FI(NXYA),DFX(NXYA),DFY(NXYA)
      REAL PHIMAX(NXYA),PHIMIN(NXYA),PSI(NXYA)
C
      CALL SETIND(K)
      IJST=IJGR(K)+1; IJEN=IJGR(K)+NIJ
C
C.....INITIALIZE LOCAL BOUNDS AND LIMITER
      DO IJ=IJST,IJEN
        PHIMAX(IJ)=FI(IJ); PHIMIN(IJ)=FI(IJ); PSI(IJ)=1.
      END DO
C
C.....GATHER MAX/MIN OVER ALL FACE-SHARING NEIGHBORS
C     East-West connections
      DO I=2,NIM-1
        DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
          IJN=IJ+NJ
          PHIMAX(IJ) =MAX(PHIMAX(IJ), FI(IJN))
          PHIMIN(IJ) =MIN(PHIMIN(IJ), FI(IJN))
          PHIMAX(IJN)=MAX(PHIMAX(IJN),FI(IJ))
          PHIMIN(IJN)=MIN(PHIMIN(IJN),FI(IJ))
        END DO
      END DO
C     North-South connections
      DO I=2,NIM
        DO IJ=LI(I+IST)+2,LI(I+IST)+NJM-1
          IJN=IJ+1
          PHIMAX(IJ) =MAX(PHIMAX(IJ), FI(IJN))
          PHIMIN(IJ) =MIN(PHIMIN(IJ), FI(IJN))
          PHIMAX(IJN)=MAX(PHIMAX(IJN),FI(IJ))
          PHIMIN(IJN)=MIN(PHIMIN(IJN),FI(IJ))
        END DO
      END DO
C
C.....COMPUTE LIMITER FROM EAST FACE CONTRIBUTIONS
      DO I=2,NIM-1
        DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
          IJN=IJ+NJ
          XF=0.5*(XC(IJ)+XC(IJN)); YF=0.5*(YC(IJ)+YC(IJN))
C         Reconstruction from P-side
          DPHI=DFX(IJ)*(XF-XC(IJ))+DFY(IJ)*(YF-YC(IJ))
          IF(ABS(DPHI).GT.SMALL) THEN
            IF(DPHI.GT.0.) THEN
              RP=(PHIMAX(IJ)-FI(IJ))/DPHI
            ELSE
              RP=(PHIMIN(IJ)-FI(IJ))/DPHI
            ENDIF
            PSI(IJ)=MIN(PSI(IJ),MIN(1.,RP))
          ENDIF
C         Reconstruction from N-side
          DPHI=DFX(IJN)*(XF-XC(IJN))+DFY(IJN)*(YF-YC(IJN))
          IF(ABS(DPHI).GT.SMALL) THEN
            IF(DPHI.GT.0.) THEN
              RN=(PHIMAX(IJN)-FI(IJN))/DPHI
            ELSE
              RN=(PHIMIN(IJN)-FI(IJN))/DPHI
            ENDIF
            PSI(IJN)=MIN(PSI(IJN),MIN(1.,RN))
          ENDIF
        END DO
      END DO
C
C.....COMPUTE LIMITER FROM NORTH FACE CONTRIBUTIONS
      DO I=2,NIM
        DO IJ=LI(I+IST)+2,LI(I+IST)+NJM-1
          IJN=IJ+1
          XF=0.5*(XC(IJ)+XC(IJN)); YF=0.5*(YC(IJ)+YC(IJN))
          DPHI=DFX(IJ)*(XF-XC(IJ))+DFY(IJ)*(YF-YC(IJ))
          IF(ABS(DPHI).GT.SMALL) THEN
            IF(DPHI.GT.0.) THEN
              RP=(PHIMAX(IJ)-FI(IJ))/DPHI
            ELSE
              RP=(PHIMIN(IJ)-FI(IJ))/DPHI
            ENDIF
            PSI(IJ)=MIN(PSI(IJ),MIN(1.,RP))
          ENDIF
          DPHI=DFX(IJN)*(XF-XC(IJN))+DFY(IJN)*(YF-YC(IJN))
          IF(ABS(DPHI).GT.SMALL) THEN
            IF(DPHI.GT.0.) THEN
              RN=(PHIMAX(IJN)-FI(IJN))/DPHI
            ELSE
              RN=(PHIMIN(IJN)-FI(IJN))/DPHI
            ENDIF
            PSI(IJN)=MIN(PSI(IJN),MIN(1.,RN))
          ENDIF
        END DO
      END DO
C
C.....APPLY LIMITER (clamp to [0,1] for safety)
      DO I=2,NIM
        DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
          PSIV=MAX(0.,MIN(1.,PSI(IJ)))
          DFX(IJ)=PSIV*DFX(IJ); DFY(IJ)=PSIV*DFY(IJ)
        END DO
      END DO
C
      RETURN
      END
C#############################################################
      SUBROUTINE CALCSC(K,IFI,FI,FIO,FIOO)
C#############################################################
C     Discretizes and solves scalar transport equations.
C     Routes to SST/gamma-Retheta source routines automatically.
C=============================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'logic.inc'
      INCLUDE 'rcont.inc'
      INCLUDE 'var.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'coef.inc'
      INCLUDE 'varold.inc'
      INCLUDE 'grad.inc'
      INCLUDE 'bound.inc'
      INCLUDE 'model.inc'
      DIMENSION FI(NXYA),FIO(NXYA),FIOO(NXYA)
C
      CALL SETIND(K)
      CALL GRADFI(K,FI,DPX,DPY)
C
C.....APPLY LIMITER TO SCALAR GRADIENTS (linearUpwind/QUICK only)
      IF(ILIMIT.EQ.1.AND.ISCHEME.GE.2) THEN
        CALL CELLMDLIM(K,FI,DPX,DPY)
      ENDIF
C
      IJST=IJGR(K)+1; IJEN=IJGR(K)+NIJ
      DO IJ=IJST,IJEN
        SU(IJ)=0.; AP(IJ)=0.
      END DO
C
      GFI=GDS(IFI); URFFI=1./URF(IFI)
C
C.....Use linearUpwind for scalars (ISCH=4->3 for vector field only)
      ISCSC=ISCHEME; IF(ISCSC.EQ.4) ISCSC=3
C
C.....EAST FACES
      DO I=2,NIM-1
      DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
        CALL FLUXSC(IFI,IJ,IJ+NJ,IJ,IJ-1,F1(IJ),
     *    AW(IJ+NJ),AE(IJ),FX(IJ),GFI,FI,ISCSC)
      END DO; END DO
C
C.....NORTH FACES
      DO I=2,NIM
      DO IJ=LI(I+IST)+2,LI(I+IST)+NJM-1
        CALL FLUXSC(IFI,IJ,IJ+1,IJ-NJ,IJ,F2(IJ),
     *    AS(IJ+1),AN(IJ),FY(IJ),GFI,FI,ISCSC)
      END DO; END DO
C
C.....O/C-GRID CUTS
      DO I=IOCS(K)+1,IOCS(K)+NOC(K)
        IJP=IJL(I); IJN=IJR(I)
        CALL FLUXSC(IFI,IJP,IJN,IJOC1(I),IJOC2(I),FMOC(I),
     *    AL(I),AR(I),FOC(I),GFI,FI,ISCSC)
        AP(IJP)=AP(IJP)-AR(I); AP(IJN)=AP(IJN)-AL(I)
      END DO
C
C.....UNSTEADY TERM
      IF(LTIME) THEN
        DO I=2,NIM
        DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
          APT=DEN(IJ)*VOL(IJ)*DTR
          SU(IJ)=SU(IJ)+APT*((1.+GAMT)*FIO(IJ)-0.5*GAMT*FIOO(IJ))
          AP(IJ)=AP(IJ)+APT*(1.+0.5*GAMT)
        END DO; END DO
      ENDIF
C
C.....INLET BOUNDARIES
      DO II=IIS(K)+1,IIS(K)+NINL(K)
        IJP=IJPI(II); IJB=IJI(II)
        DPX(IJB)=DPX(IJP); DPY(IJB)=DPY(IJP)
        CALL FLUXSC(IFI,IJP,IJB,IJI1(II),IJI2(II),FMI(II),
     *    CP,CB,ONE,ZERO,FI,1)
        AP(IJP)=AP(IJP)-CB
        SU(IJP)=SU(IJP)-CB*FI(IJB)
      END DO
C
C.....OUTLET BOUNDARIES
      DO IO=IOS(K)+1,IOS(K)+NOUT(K)
        IJP=IJPO(IO); IJB=IJO(IO)
        DPX(IJB)=DPX(IJP); DPY(IJB)=DPY(IJP)
        CALL FLUXSC(IFI,IJP,IJB,IJO1(IO),IJO2(IO),FMO(IO),
     *    CP,CB,ONE,ZERO,FI,1)
        AP(IJP)=AP(IJP)-CB
        SU(IJP)=SU(IJP)-CB*FI(IJB)
      END DO
C
C.....VARIABLE-SPECIFIC SOURCE TERMS AND WALL BC
      IF(IFI.EQ.IEN)  CALL TEMP(K)
      IF(IFI.EQ.ITE)  CALL KINE_SST(K)
      IF(IFI.EQ.IED)  CALL DISE_SST(K)
      IF(IFI.EQ.IGAM) CALL CALCGAM(K)
      IF(IFI.EQ.IRET) CALL CALCRET(K)
C
C.....FINAL COEFFICIENT MATRIX
      DO I=2,NIM
      DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
        AP(IJ)=(AP(IJ)-AE(IJ)-AW(IJ)-AN(IJ)-AS(IJ))*URFFI
        SU(IJ)=SU(IJ)+(1.-URF(IFI))*AP(IJ)*FI(IJ)
      END DO; END DO
C
C.....SOLVE
      CALL SIPSOL(FI,IFI,K)
C
C.....SYMMETRY/OUTLET BOUNDARIES
      DO IS=ISS(K)+1,ISS(K)+NSYM(K)
        FI(IJS(IS))=FI(IJPS(IS))
      END DO
      DO IO=IOS(K)+1,IOS(K)+NOUT(K)
        FI(IJO(IO))=FI(IJPO(IO))
      END DO
C
C.....POSITIVITY CLAMP (k, omega, gamma, Retheta must be positive)
      IF(IFI.EQ.ITE.OR.IFI.EQ.IED.OR.
     *   IFI.EQ.IGAM.OR.IFI.EQ.IRET) THEN
        DO IJ=IJST,IJEN
          FI(IJ)=MAX(FI(IJ),SMALL)
        END DO
      ENDIF
C
      RETURN
      END
C
C
C################################################################
      SUBROUTINE FLUXSC(IFI,IJP,IJN,IJ1,IJ2,FM,CAP,CAN,FAC,G,
     *                  FI,ISCH)
C################################################################
C     Scalar convective+diffusive flux through one face.
C     Supports ISCH=1 (UDS/CDS), 2 (QUICK), 3 (linearUpwind).
C     Diffusion coefficient selected by variable index IFI.
C     SST: blended sigma_k, sigma_omega using local F1 function.
C================================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'rcont.inc'
      INCLUDE 'var.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'grad.inc'
      INCLUDE 'coef.inc'
      INCLUDE 'model.inc'
      DIMENSION FI(NXYA)
C
      FACP=1.-FAC
      FII=FI(IJN)*FAC+FI(IJP)*FACP
      VISI=VIS(IJN)*FAC+VIS(IJP)*FACP-VISC
C
C.....BLENDED DIFFUSION COEFFICIENT (SST zone-blending via F1)
      F1F=F1SST(IJN)*FAC+F1SST(IJP)*FACP
      F1FC=1.-F1F
      IF(IFI.EQ.IEN) THEN
        DCOEF=(VISC+VISI*SIGT)/PRANL
      ELSEIF(IFI.EQ.ITE) THEN
        DCOEF=VISC+VISI*(F1F*SIGK1+F1FC*SIGK2)
      ELSEIF(IFI.EQ.IED) THEN
        DCOEF=VISC+VISI*(F1F*SIGOM1+F1FC*SIGOM2)
      ELSEIF(IFI.EQ.IGAM) THEN
        DCOEF=VISC+VISI/SIGF
      ELSEIF(IFI.EQ.IRET) THEN
        DCOEF=SIGTH*(VISC+VISI)
      ELSE
        DCOEF=VISC+VISI
      ENDIF
C
      RC=0.5*(R(IJ1)+R(IJ2))
      SX=(Y(IJ1)-Y(IJ2))*RC; SY=(X(IJ2)-X(IJ1))*RC
      XPN=XC(IJN)-XC(IJP); YPN=YC(IJN)-YC(IJP)
      VSOL=DCOEF*SQRT((SX**2+SY**2)/(XPN**2+YPN**2+SMALL))
C
      DFXI=DPX(IJN)*FAC+DPX(IJP)*FACP
      DFYI=DPY(IJN)*FAC+DPY(IJP)*FACP
C
C.....DIFFUSIVE FLUXES
      FCFIE_CDS=FM*FII
      FDFIE=DCOEF*(DFXI*SX+DFYI*SY)
      FDFII=VSOL*(DFXI*XPN+DFYI*YPN)
C
C.....IMPLICIT UPWIND
      FCFII=MIN(FM,ZERO)*FI(IJN)+MAX(FM,ZERO)*FI(IJP)
C
C.....SCHEME-SPECIFIC EXPLICIT CONVECTIVE FLUX
      XF=0.5*(X(IJ2)+X(IJ1)); YF=0.5*(Y(IJ2)+Y(IJ1))
C
      IF(ISCH.EQ.2) THEN
C.......QUICK
        IF(FM.GE.ZERO) THEN
          UUREC=FI(IJP)-DPX(IJP)*(XC(IJN)-XC(IJP))
     *                 -DPY(IJP)*(YC(IJN)-YC(IJP))
          FF_Q=0.75*FI(IJP)+0.375*(FI(IJN)-FI(IJP))*FAC
     *        +0.125*UUREC
        ELSE
          UUREC=FI(IJN)-DPX(IJN)*(XC(IJP)-XC(IJN))
     *                 -DPY(IJN)*(YC(IJP)-YC(IJN))
          FF_Q=0.75*FI(IJN)+0.375*(FI(IJP)-FI(IJN))*(1.-FAC)
     *        +0.125*UUREC
        ENDIF
        FCFIE=FM*FF_Q
C
      ELSEIF(ISCH.EQ.3) THEN
C.......linearUpwind
        IF(FM.GE.ZERO) THEN
          FF_L=FI(IJP)+DPX(IJP)*(XF-XC(IJP))+DPY(IJP)*(YF-YC(IJP))
        ELSE
          FF_L=FI(IJN)+DPX(IJN)*(XF-XC(IJN))+DPY(IJN)*(YF-YC(IJN))
        ENDIF
        FCFIE=FM*FF_L
C
      ELSE
C.......UDS/CDS blend
        FCFIE=FCFIE_CDS
      ENDIF
C
      CAN=-VSOL+MIN(FM,ZERO)
      CAP=-VSOL-MAX(FM,ZERO)
      FFIC=G*(FCFIE-FCFII)
      SU(IJP)=SU(IJP)-FFIC+FDFIE-FDFII
      SU(IJN)=SU(IJN)+FFIC-FDFIE+FDFII
C
      RETURN
      END
C###############################################################
      SUBROUTINE TEMP(K)
C###############################################################
C     Source terms and wall BC for the energy (temperature) equation.
C==============================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'rcont.inc'
      INCLUDE 'var.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'coef.inc'
      INCLUDE 'bound.inc'
      INCLUDE 'model.inc'
      DCOEF=VISC/PRANL
      DO IW=IWS(K)+1,IWS(K)+NWALI(K)
        IJP=IJPW(IW); IJB=IJW(IW)
        COEF=DCOEF*SRDW(IW)
        AP(IJP)=AP(IJP)+COEF
        SU(IJP)=SU(IJP)+COEF*T(IJB)
      END DO
      DO IW=IWAS(K)+1,IWAS(K)+NWALA(K)
        T(IJW(IW))=T(IJPW(IW))
      END DO
      RETURN
      END
C
C
C###############################################################
      SUBROUTINE KINE_SST(K)
C###############################################################
C     Source terms and wall BC for turbulent kinetic energy (k)
C     using the k-omega SST model (Menter 2003).
C
C     k-equation:
C       Pk = gamma_eff * min(mu_t*S^2, 10*beta*rho*k*omega)
C       Dk = beta* * rho * k * omega
C
C     Wall BC (viscous sublayer, y+ < ~11):
C       k_wall = 0 (Dirichlet)
C     Wall BC (log-layer, y+ > ~11):
C       Production balanced by dissipation (wall function)
C
C     gamma_eff = intermittency from gamma-Retheta model (if active)
C===============================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'logic.inc'
      INCLUDE 'rcont.inc'
      INCLUDE 'var.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'coef.inc'
      INCLUDE 'grad.inc'
      INCLUDE 'bound.inc'
      INCLUDE 'model.inc'
C
C.....UPDATE SST BLENDING FUNCTIONS F1, F2
      CALL CALC_F1F2(K)
C
C.....VOLUMETRIC SOURCES
      DO I=2,NIM
        DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
          S11=DUX(IJ); S22=DVY(IJ); S12=0.5*(DUY(IJ)+DVX(IJ))
          S2=2.*(S11**2+S22**2+2.*S12**2)
          IF(LAXIS) THEN
            RCR=4./(R(IJ)+R(IJ-NJ)+R(IJ-1)+R(IJ-NJ-1)+SMALL)
            S2=S2+2.*(V(IJ)*RCR)**2
          ENDIF
C
          MUTIJ=MAX(VIS(IJ)-VISC,ZERO)
          PKRAW=MUTIJ*S2
          PKLIM=10.*BETSTAR*DEN(IJ)*TE(IJ)*ED(IJ)
C
C         Intermittency correction (Langtry-Menter)
          IF(LCAL(IGAM)) THEN
            GAMEF=MIN(MAX(GAM(IJ),ZERO),1.)
          ELSE
            GAMEF=1.
          ENDIF
C
          GEN(IJ)=GAMEF*MIN(PKRAW,PKLIM)
          SU(IJ)=SU(IJ)+GEN(IJ)*VOL(IJ)
          AP(IJ)=AP(IJ)+BETSTAR*DEN(IJ)*ED(IJ)*VOL(IJ)
        END DO
      END DO
C
C.....WALL BOUNDARY CONDITIONS
      DO IW=IWS(K)+1,IWS(K)+NWAL(K)
        IJP=IJPW(IW); IJB=IJW(IW)
        IF(YPL(IW).LE.CTRANS) THEN
C         Viscous sublayer: k = 0 (Dirichlet)
          TE(IJB)=ZERO
          COEF=2.*VISC*SRDW(IW)
          AP(IJP)=AP(IJP)+COEF
          SU(IJP)=SU(IJP)+COEF*TE(IJB)
          SU(IJP)=SU(IJP)-GEN(IJP)*VOL(IJP)
        ELSE
C         Log layer: wall-function production
          CK=CMU25*SQRT(MAX(ZERO,TE(IJP)))
          TAU=VISW(IW)*((U(IJB)-U(IJP))*XTW(IW)
     *        +(V(IJB)-V(IJP))*YTW(IW))/DN(IW)
          GENW=ABS(TAU)*CK/(DN(IW)*CAPPA)
          SU(IJP)=SU(IJP)-GEN(IJP)*VOL(IJP)+GENW*VOL(IJP)
        ENDIF
      END DO
C
      RETURN
      END
C
C
C###############################################################
      SUBROUTINE DISE_SST(K)
C###############################################################
C     Source terms and wall BC for specific dissipation rate (omega)
C     using the k-omega SST model (Menter 2003).
C
C     omega-equation:
C       P_om  = gamma_sst * rho * S^2   (production)
C       D_om  = beta * rho * omega^2    (destruction)
C       CD_om = 2*(1-F1)*rho*sigma_om2/omega * grad(k).grad(omega)
C                                        (cross-diffusion from k-eps)
C
C     Wall BC (viscous sublayer):
C       omega_w = 60*nu/(beta1*y1^2)   (Wilcox 1988 sub-layer BC)
C     Wall BC (log-layer):
C       omega_w = sqrt(k)/(CMU25*kappa*y)
C===============================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'rcont.inc'
      INCLUDE 'var.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'coef.inc'
      INCLUDE 'grad.inc'
      INCLUDE 'bound.inc'
      INCLUDE 'model.inc'
C
C.....VOLUMETRIC SOURCES
      DO I=2,NIM
        DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
          F1P=F1SST(IJ); F1PC=1.-F1P
C         Blended production and destruction coefficients
          GAMBL=F1P*GAMSST1+F1PC*GAMSST2
          BETBL=F1P*BET1   +F1PC*BET2
C         Strain rate S^2
          S11=DUX(IJ); S22=DVY(IJ); S12=0.5*(DUY(IJ)+DVX(IJ))
          S2=2.*(S11**2+S22**2+2.*S12**2)
C         Production of omega: gamma*rho*S^2
          POMEG=GAMBL*DEN(IJ)*S2*VOL(IJ)
C         Destruction: beta*rho*omega^2 (linear in omega -> implicit)
          DOMEG=BETBL*DEN(IJ)*ED(IJ)*VOL(IJ)
C         Cross-diffusion term (only in k-eps zone, where F1<1)
          CDTERM=2.*F1PC*DEN(IJ)*SIGOM2/
     *      MAX(ED(IJ),SMALL)*MAX(CDKW(IJ),1.E-10)*VOL(IJ)
C
          SU(IJ)=SU(IJ)+POMEG+CDTERM
          AP(IJ)=AP(IJ)+BETBL*DEN(IJ)*VOL(IJ)
        END DO
      END DO
C
C.....WALL BOUNDARY CONDITIONS
      DO IW=IWS(K)+1,IWS(K)+NWAL(K)
        IJP=IJPW(IW); IJB=IJW(IW)
        IF(YPL(IW).LE.CTRANS) THEN
C         Viscous sublayer: omega = 60*nu/(beta1*y1^2) (Wilcox 1988)
          OMWALL=60.*VISC/(DEN(IJP)*BET1*DN(IW)**2)
          ED(IJB)=OMWALL
          SU(IJP)=OMWALL; AP(IJP)=1.
          AS(IJP)=0.; AN(IJP)=0.; AW(IJP)=0.; AE(IJP)=0.
        ELSE
C         Log layer: omega from log-law sqrt(k)/(CMU25*kappa*y)
          ED(IJP)=SQRT(MAX(ZERO,TE(IJP)))/(CMU25*CAPPA*DN(IW))
          SU(IJP)=ED(IJP); AP(IJP)=1.
          AS(IJP)=0.; AN(IJP)=0.; AW(IJP)=0.; AE(IJP)=0.
        ENDIF
      END DO
C
      RETURN
      END
C
C
C###############################################################
      SUBROUTINE CALC_F1F2(K)
C###############################################################
C     Computes SST blending functions F1 and F2 (Menter 2003).
C
C     F1 (wall-region blend): switches from k-omega (F1=1)
C        to k-epsilon (F1=0) in the outer boundary layer
C        arg1 = min[max(sqrt(k)/(beta*omega*y), 500*nu/(omega*y^2)),
C                   4*rho*sigma_om2*k/(CD_kw*y^2)]
C        F1 = tanh(arg1^4)
C
C     F2 (eddy-viscosity limiter): F2=1 in wake, 0 in freestream
C        arg2 = max[2*sqrt(k)/(beta*omega*y), 500*nu/(omega*y^2)]
C        F2 = tanh(arg2^2)
C
C     CD_kw = max(2*rho*sigma_om2/omega * (grad k).(grad omega), 1e-10)
C==============================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'var.inc'
      INCLUDE 'rcont.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'bound.inc'
      INCLUDE 'model.inc'
      INCLUDE 'grad.inc'
      REAL DKX(NXYA),DKY(NXYA),DOMX(NXYA),DOMY(NXYA)
C
      CALL SETIND(K)
      CALL GRADFI(K,TE,DKX,DKY)
      CALL GRADFI(K,ED,DOMX,DOMY)
C
      IJST=IJGR(K)+1; IJEN=IJGR(K)+NIJ
      DO IJ=IJST,IJEN
        F1SST(IJ)=1.; F2SST(IJ)=1.; CDKW(IJ)=0.
      END DO
C
      DO IW=IWS(K)+1,IWS(K)+NWAL(K)
        IJP=IJPW(IW)
        YW=MAX(DN(IW),SMALL)
        KVAL=MAX(TE(IJP),SMALL); OMVAL=MAX(ED(IJP),SMALL)
        NUVAL=VISC/DEN(IJP)
C
C       Cross-diffusion
        CDKWV=2.*DEN(IJP)*SIGOM2/OMVAL*
     *    (DKX(IJP)*DOMX(IJP)+DKY(IJP)*DOMY(IJP))
        CDKW(IJP)=MAX(CDKWV,1.E-10)
C
C       F1
        A1F=SQRT(KVAL)/(BETSTAR*OMVAL*YW)
        A2F=500.*NUVAL/(OMVAL*YW**2)
        A3F=4.*DEN(IJP)*SIGOM2*KVAL/(CDKW(IJP)*YW**2)
        ARG1=MIN(MAX(A1F,A2F),A3F)
        F1SST(IJP)=TANH(MIN(ARG1**4,100.))
C
C       F2
        B1F=2.*SQRT(KVAL)/(BETSTAR*OMVAL*YW)
        B2F=500.*NUVAL/(OMVAL*YW**2)
        ARG2=MIN(MAX(B1F,B2F),100.)
        F2SST(IJP)=TANH(ARG2**2)
      END DO
C
      RETURN
      END
C###############################################################
      SUBROUTINE MODVIS_SST(K)
C###############################################################
C     Computes effective viscosity using k-omega SST formulation.
C
C     mut = rho * a1 * k / max(a1*omega, |S|*F2)
C
C     The SST limiter (a1*omega vs |S|*F2) prevents excessive
C     eddy viscosity in stagnation regions (Kato-Launder fix).
C     Intermittency from gamma-Retheta model modulates mut.
C==============================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'logic.inc'
      INCLUDE 'rcont.inc'
      INCLUDE 'var.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'bound.inc'
      INCLUDE 'model.inc'
      INCLUDE 'grad.inc'
C
      CALL SETIND(K)
      CALL GRADFI(K,U,DUX,DUY)
      CALL GRADFI(K,V,DVX,DVY)
C
C.....EDDY VISCOSITY AT INTERIOR CELLS
      DO I=2,NIM
        DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
          VISOLD=VIS(IJ)
          S11=DUX(IJ); S22=DVY(IJ); S12=0.5*(DUY(IJ)+DVX(IJ))
          S2=2.*(S11**2+S22**2+2.*S12**2)
          SMAG=SQRT(MAX(S2,SMALL))
C
C         SST eddy viscosity denominator
          DENOM=MAX(A1SST*ED(IJ), SMAG*F2SST(IJ))
          MUTSST=DEN(IJ)*A1SST*TE(IJ)/(DENOM+SMALL)
C
C         Effective intermittency
          IF(LCAL(IGAM)) THEN
            GAMEF=MIN(MAX(GAM(IJ),ZERO),1.)
          ELSE
            GAMEF=1.
          ENDIF
C
          VISNEW=VISC+GAMEF*MUTSST
          VIS(IJ)=VISNEW*URF(IVIS)+VISOLD*(1.-URF(IVIS))
        END DO
      END DO
C
C.....WALL BOUNDARY: effective viscosity for wall-function shear stress
      DO IW=IWS(K)+1,IWS(K)+NWAL(K)
        IJB=IJW(IW); IJP=IJPW(IW)
        CK=CMU25*SQRT(MAX(ZERO,TE(IJP)))
        YPL(IW)=DEN(IJB)*CK*DN(IW)/VISC
        IF(YPL(IW).LE.CTRANS) THEN
          VISW(IW)=VISC
        ELSE
          VISCW=YPL(IW)*VISC*CAPPA/LOG(ELOG*YPL(IW))
          VISW(IW)=MAX(VISC,VISCW)
        ENDIF
        VIS(IJB)=VISW(IW)
      END DO
C
      RETURN
      END
C
C
C###############################################################
      SUBROUTINE CALCGAM(K)
C###############################################################
C     Source terms for the intermittency (gamma) transport equation.
C     Langtry & Menter, J. Turbomachinery 131, 2009.
C
C     gamma-equation:
C       d(rho*gamma)/dt + div(rho*U*gamma) =
C         P_gamma1 - E_gamma1 + P_gamma2 - E_gamma2
C         + div[(mu + mut/sigma_f)*grad(gamma)]
C
C     P_gamma1 = F_length * rho * S * gamma * (1 - CE2*gamma) * F_onset
C     E_gamma1 = CA2 * rho * Omega * gamma * F_turb
C     P_gamma2 = CE1 * P_gamma1
C     E_gamma2 = CE2 * CA2 * rho * Omega * gamma^2 * F_turb
C
C     F_onset: onset function based on Re_v and Re_theta_t
C     F_turb:  turbulence suppression: exp(-(RT/4)^2)
C     F_length: empirical correlation from Re_theta_t
C===============================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'logic.inc'
      INCLUDE 'rcont.inc'
      INCLUDE 'var.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'coef.inc'
      INCLUDE 'grad.inc'
      INCLUDE 'bound.inc'
      INCLUDE 'model.inc'
C
      DO I=2,NIM
        DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
          GAMIJ=MAX(GAM(IJ),1.E-6)
          RETIJ=MAX(RETHET(IJ),SMALL)
          MUIJ =VISC; DENIJ=DEN(IJ)
          MUTIJ=MAX(VIS(IJ)-VISC,ZERO)
C
C         Strain rate and vorticity
          S11=DUX(IJ); S22=DVY(IJ); S12=0.5*(DUY(IJ)+DVX(IJ))
          S2=2.*(S11**2+S22**2+2.*S12**2)
          SMAG=SQRT(MAX(S2,SMALL))
          OMGMAG=SMAG    ! strain-rate approx for |Omega|
C
C         Local vorticity Re_v = rho*y^2*S/mu
          YW=YC(IJ)      ! approximate wall distance
          REV=DENIJ*YW**2*SMAG/(MUIJ+SMALL)
C
C         Critical Re_theta_t (onset Re from Re_theta_tilde)
          RETC=MAX(0.1*RETIJ, RETIJ-
     *      (0.1*RETIJ**2-100.*RETIJ+1200.)*GAMIJ)
C
C         Onset functions
          RT=DENIJ*TE(IJ)/(MUIJ*MAX(ED(IJ),SMALL))
          FONSET1=REV/(2.193*RETC+SMALL)
          FONSET2=MIN(MAX(FONSET1,FONSET1**4),2.)
          FONSET3=MAX(1.-RT**3/6.25,0.)
          FONSET =MAX(FONSET2-FONSET3,0.)
C
C         F_length from Re_theta_tilde (Langtry-Menter 2009 Table 1)
          IF(RETIJ.LE.400.) THEN
            FLEN=398.19E-1-119.27E-4*RETIJ-132.57E-6*RETIJ**2
          ELSEIF(RETIJ.LE.596.) THEN
            FLEN=263.40-123.94E-2*RETIJ+194.55E-5*RETIJ**2
     *          -101.70E-8*RETIJ**3
          ELSEIF(RETIJ.LE.1200.) THEN
            FLEN=MAX(0.5-3.E-4*(RETIJ-596.),0.)
          ELSE
            FLEN=0.3188
          ENDIF
          FLEN=MAX(FLEN,0.0)
C
C         F_turb: turbulence-induced relaminarisation
          FTURB=EXP(-(RT/4.)**2)
C
C         Source terms
          PGAM1=FLEN*DENIJ*SMAG*GAMIJ*(1.-CE2TR*GAMIJ)*FONSET
          EGAM1=CA2TR*DENIJ*OMGMAG*GAMIJ*FTURB
          PGAM2=CE1TR*PGAM1
          EGAM2=CE2TR*CA2TR*DENIJ*OMGMAG*GAMIJ**2*FTURB
C
          NETSRC=(PGAM1-EGAM1+PGAM2-EGAM2)*VOL(IJ)
          IF(NETSRC.GE.0.) THEN
            SU(IJ)=SU(IJ)+NETSRC
          ELSE
            SU(IJ)=SU(IJ)+NETSRC
            AP(IJ)=AP(IJ)+ABS(NETSRC)/(GAMIJ+SMALL)
          ENDIF
        END DO
      END DO
C
C.....WALL BC: gamma = 0 at wall (no turbulence onset at wall)
      DO IW=IWS(K)+1,IWS(K)+NWAL(K)
        IJB=IJW(IW); IJP=IJPW(IW)
        GAM(IJB)=ZERO
        COEF=2.*VISC*SRDW(IW)
        AP(IJP)=AP(IJP)+COEF
        SU(IJP)=SU(IJP)+COEF*ZERO
      END DO
C
      RETURN
      END
C
C
C###############################################################
      SUBROUTINE CALCRET(K)
C###############################################################
C     Transport equation for transition onset Re_theta_tilde.
C     Langtry & Menter, J. Turbomachinery 131, 2009.
C
C     d(rho*Re_tht)/dt + div(rho*U*Re_tht) =
C       P_tht + div[sigma_th*(mu+mut)*grad(Re_tht)]
C
C     P_tht = c_tht * (rho/t_scale) * (Re_theta_corr - Re_tht)*(1-F_tht)
C     t_scale = 500*mu/(rho*U^2)   [convective time scale]
C     Re_theta_corr: empirical correlation F(Tu, lambda_theta)
C     F_tht: prevents equation from being active in boundary layer
C===============================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'logic.inc'
      INCLUDE 'rcont.inc'
      INCLUDE 'var.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'coef.inc'
      INCLUDE 'grad.inc'
      INCLUDE 'bound.inc'
      INCLUDE 'model.inc'
C
      DO I=2,NIM
        DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
          DENIJ=DEN(IJ); MUIJ=VISC
          UMAG=SQRT(U(IJ)**2+V(IJ)**2+SMALL)
          RETIJ=MAX(RETHET(IJ),SMALL)
C
C         Local turbulence intensity (%)
          TINT=SQRT(2.*TE(IJ)/3.)/(UMAG)
          TUPC=MAX(100.*TINT,0.027)
C
C         Re_theta_corr from turbulence intensity (Menter 2009 Eq. 2.2)
          IF(TUPC.LE.1.3) THEN
            RETHCOR=1173.51-589.43*TUPC+0.2196/TUPC**2
          ELSE
            RETHCOR=331.50*(TUPC-0.5658)**(-0.671)
          ENDIF
          RETHCOR=MAX(RETHCOR,20.)
C
C         Convective time scale: t = 500*mu/(rho*U^2)
          TSCALE=500.*MUIJ/(DENIJ*UMAG**2+SMALL)
C
C         F_tht: free-stream indicator (0 in BL, 1 outside)
          RT=DENIJ*TE(IJ)/(MUIJ*MAX(ED(IJ),SMALL))
          FWAKE=EXP(-(MAX(RETIJ,1.)/1.E5)**2)
          FTHT=MIN(MAX(FWAKE*EXP(-((YC(IJ)/(4.*TSCALE*UMAG)))**4),
     *        1.-((MAX(GAM(IJ)-1./CE2TR,0.)/(1.-1./CE2TR))**2)),1.)
C
C         Source: drive local Re_tht toward the correlation value
          PTHT=CTHT*DENIJ/TSCALE*(RETHCOR-RETIJ)*(1.-FTHT)*VOL(IJ)
C
          IF(PTHT.GE.0.) THEN
            SU(IJ)=SU(IJ)+PTHT
          ELSE
            SU(IJ)=SU(IJ)+PTHT
            AP(IJ)=AP(IJ)+ABS(PTHT)/(RETIJ+SMALL)
          ENDIF
        END DO
      END DO
C
C.....WALL BC: zero flux (Neumann) - Re_tht has no wall value
C     Handled by symmetry-like zero-gradient treatment at walls
      DO IW=IWS(K)+1,IWS(K)+NWAL(K)
        RETHET(IJW(IW))=RETHET(IJPW(IW))
      END DO
C
      RETURN
      END
C########################################################
      SUBROUTINE SETIND(K)
C########################################################
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      NI=NIGR(K); NJ=NJGR(K)
      IST=IGR(K); JST=JGR(K)
      NJM=NJ-1; NIM=NI-1; NIJ=NI*NJ
      RETURN
      END
C
C
C##########################################################
      SUBROUTINE PRINT(K,FI,HEDFI)
C##########################################################
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      DIMENSION FI(NXYA)
      CHARACTER*6 HEDFI
      CALL SETIND(K)
      WRITE(2,20) HEDFI
      IEND=0; NL=NI/12+1
      IF(MOD(NI,12).EQ.0) NL=NL-1
      DO L=1,NL
        IBEG=IEND+1; IEND=MIN(IBEG+11,NI)
        WRITE(2,'(3X,4HI = ,I3,11I10)') (I,I=IBEG,IEND)
        WRITE(2,*) '  J'
        DO J=NJ,1,-1
          WRITE(2,'(1X,I3,1P12E10.2)') J,
     *      (FI(LI(I+IST)+J),I=IBEG,IEND)
        END DO
      END DO
   20 FORMAT(2X,26('*-'),6X,A6,6X,26('-*'))
      RETURN
      END
C
C
C############################################################
      SUBROUTINE SIPSOL(FI,IFI,K)
C############################################################
C     Stone's Incomplete LU (SIP) solver.
C     See Ferziger-Peric 4th Ed., Sect. 5.3.4.
C============================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'logic.inc'
      INCLUDE 'rcont.inc'
      INCLUDE 'coef.inc'
      INCLUDE 'bound.inc'
      DIMENSION FI(NXYA)
      REAL LW(NXYA),LS(NXYA),LPR(NXYA),UE(NXYA),UN(NXYA),RES(NXYA)
      DATA UE,UN,RES /NXYA*0.,NXYA*0.,NXYA*0./
C
C.....ILU FACTORIZATION
      DO I=2,NIM
      DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
        LW(IJ)=AW(IJ)/(1.+ALFA*UN(IJ-NJ))
        LS(IJ)=AS(IJ)/(1.+ALFA*UE(IJ-1))
        P1=ALFA*LW(IJ)*UN(IJ-NJ)
        P2=ALFA*LS(IJ)*UE(IJ-1)
        LPR(IJ)=1./(AP(IJ)+P1+P2-LW(IJ)*UE(IJ-NJ)
     *           -LS(IJ)*UN(IJ-1)+SMALL)
        UN(IJ)=(AN(IJ)-P1)*LPR(IJ)
        UE(IJ)=(AE(IJ)-P2)*LPR(IJ)
      END DO; END DO
C
C.....INNER ITERATIONS
      DO L=1,NSW(IFI)
        RESAB=0.
        DO I=2,NIM
        DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
          RES(IJ)=SU(IJ)-AP(IJ)*FI(IJ)-AN(IJ)*FI(IJ+1)
     *      -AS(IJ)*FI(IJ-1)-AE(IJ)*FI(IJ+NJ)-AW(IJ)*FI(IJ-NJ)
        END DO; END DO
C
        DO I=IOCS(K)+1,IOCS(K)+NOC(K)
          RES(IJL(I))=RES(IJL(I))-AR(I)*FI(IJR(I))
          RES(IJR(I))=RES(IJR(I))-AL(I)*FI(IJL(I))
        END DO
C
        DO I=2,NIM
        DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
          RESAB=RESAB+ABS(RES(IJ))
          RES(IJ)=(RES(IJ)-LS(IJ)*RES(IJ-1)
     *             -LW(IJ)*RES(IJ-NJ))*LPR(IJ)
        END DO; END DO
C
        IF(L.EQ.1) RESOR(IFI)=RESAB
        RSM=RESAB/(RESOR(IFI)+SMALL)
C
        DO I=NIM,2,-1
        DO IJ=LI(I+IST)+NJM,LI(I+IST)+2,-1
          RES(IJ)=RES(IJ)-UN(IJ)*RES(IJ+1)-UE(IJ)*RES(IJ+NJ)
          FI(IJ)=FI(IJ)+RES(IJ)
        END DO; END DO
C
        IF(LTEST) WRITE(2,*) L,' INNER ITER RESAB= ',RESAB
        IF(RSM.LT.SOR(IFI)) RETURN
      END DO
      RETURN
      END
C
C
C############################################################
      SUBROUTINE GMRESSOL(FI,IFI,K)
C############################################################
C     Restarted GMRES(m) with ILU(0) preconditioner.
C     Saad & Schultz (1986), SIAM J. Sci. Stat. Comp.
C
C     Algorithm:
C       1. Compute preconditioned system: M^{-1}*A*x = M^{-1}*b
C          where M = ILU(0) factorization of A
C       2. Arnoldi process: build orthonormal Krylov basis
C          V_m = [v1, v2, ..., vm] using modified Gram-Schmidt
C       3. Minimize ||b - A*x||_2 over K_m using Givens rotations
C       4. Restart: x0 = x_m, repeat until convergence
C
C     Parameters:
C       NKRYL = Krylov subspace dimension (m) before restart
C       NSW(IFI) = max outer iterations (restarts)
C       SOR(IFI) = relative convergence tolerance
C============================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'logic.inc'
      INCLUDE 'rcont.inc'
      INCLUDE 'coef.inc'
      INCLUDE 'bound.inc'
      DIMENSION FI(NXYA)
C
C.....GMRES WORKSPACE
      REAL V(NXYA,NKRYL+1)     ! Krylov basis vectors
      REAL H(NKRYL+1,NKRYL)    ! upper Hessenberg matrix
      REAL CS(NKRYL),SN(NKRYL) ! Givens rotation cosines/sines
      REAL ETA(NKRYL+1)        ! RHS of least-squares problem
      REAL WORK(NXYA),Z(NXYA)  ! preconditioned residual, solution
C
C.....ILU(0) FACTORS (stored as in SIP)
      REAL LWG(NXYA),LSG(NXYA),LPRG(NXYA),UEG(NXYA),UNG(NXYA)
      DATA LWG,LSG,LPRG,UEG,UNG /5*NXYA*0./
C
C.....COMPUTE ILU(0) FACTORIZATION
      DO I=2,NIM
      DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
        LWG(IJ)=AW(IJ)/(1.+ALFA*UNG(IJ-NJ))
        LSG(IJ)=AS(IJ)/(1.+ALFA*UEG(IJ-1))
        P1=ALFA*LWG(IJ)*UNG(IJ-NJ)
        P2=ALFA*LSG(IJ)*UEG(IJ-1)
        LPRG(IJ)=1./(AP(IJ)+P1+P2-LWG(IJ)*UEG(IJ-NJ)
     *            -LSG(IJ)*UNG(IJ-1)+SMALL)
        UNG(IJ)=(AN(IJ)-P1)*LPRG(IJ)
        UEG(IJ)=(AE(IJ)-P2)*LPRG(IJ)
      END DO; END DO
C
C.....OUTER RESTART LOOP
      DO LOUT=1,NSW(IFI)
C
C.......COMPUTE RESIDUAL r0 = b - A*x
        DO I=2,NIM
        DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
          WORK(IJ)=SU(IJ)-AP(IJ)*FI(IJ)-AN(IJ)*FI(IJ+1)
     *      -AS(IJ)*FI(IJ-1)-AE(IJ)*FI(IJ+NJ)-AW(IJ)*FI(IJ-NJ)
        END DO; END DO
        DO I=IOCS(K)+1,IOCS(K)+NOC(K)
          WORK(IJL(I))=WORK(IJL(I))-AR(I)*FI(IJR(I))
          WORK(IJR(I))=WORK(IJR(I))-AL(I)*FI(IJL(I))
        END DO
C
C.......APPLY ILU(0) PRECONDITIONER: z = M^{-1} * r
        CALL ILUSOLVE(WORK,Z,LWG,LSG,LPRG,UEG,UNG,K)
C
C.......COMPUTE BETA = ||z||_2
        BETA=0.
        DO I=2,NIM
        DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
          BETA=BETA+Z(IJ)**2
        END DO; END DO
        BETA=SQRT(BETA)
C
        IF(LOUT.EQ.1) RESOR(IFI)=MAX(BETA,SMALL)
        IF(BETA/(RESOR(IFI)+SMALL).LT.SOR(IFI)) RETURN
        IF(LTEST) WRITE(2,*) 'GMRES restart',LOUT,' beta=',BETA
C
C.......INITIALIZE KRYLOV BASIS v1 = z/beta
        DO I=2,NIM
        DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
          V(IJ,1)=Z(IJ)/BETA
        END DO; END DO
C
C.......INITIALIZE ETA
        DO J=1,NKRYL+1
          ETA(J)=0.
        END DO
        ETA(1)=BETA
C
C.......ARNOLDI PROCESS
        M=0
        DO J=1,NKRYL
          M=J
C
C.........COMPUTE w = A*v_j (matrix-vector product)
          DO I=2,NIM
          DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
            WORK(IJ)=AP(IJ)*V(IJ,J)+AN(IJ)*V(IJ+1,J)
     *        +AS(IJ)*V(IJ-1,J)+AE(IJ)*V(IJ+NJ,J)+AW(IJ)*V(IJ-NJ,J)
          END DO; END DO
          DO I=IOCS(K)+1,IOCS(K)+NOC(K)
            WORK(IJL(I))=WORK(IJL(I))+AR(I)*V(IJR(I),J)
            WORK(IJR(I))=WORK(IJR(I))+AL(I)*V(IJL(I),J)
          END DO
C
C.........APPLY PRECONDITIONER: z = M^{-1} * w
          CALL ILUSOLVE(WORK,Z,LWG,LSG,LPRG,UEG,UNG,K)
C
C.........MODIFIED GRAM-SCHMIDT ORTHOGONALIZATION
          DO I=1,J
            H(I,J)=0.
            DO II=2,NIM
            DO IJ=LI(II+IST)+2,LI(II+IST)+NJM
              H(I,J)=H(I,J)+Z(IJ)*V(IJ,I)
            END DO; END DO
            DO II=2,NIM
            DO IJ=LI(II+IST)+2,LI(II+IST)+NJM
              Z(IJ)=Z(IJ)-H(I,J)*V(IJ,I)
            END DO; END DO
          END DO
C
C.........COMPUTE H(j+1,j) = ||z||
          H(J+1,J)=0.
          DO II=2,NIM
          DO IJ=LI(II+IST)+2,LI(II+IST)+NJM
            H(J+1,J)=H(J+1,J)+Z(IJ)**2
          END DO; END DO
          H(J+1,J)=SQRT(H(J+1,J))
C
C.........v_{j+1} = z / H(j+1,j)
          IF(H(J+1,J).GT.SMALL) THEN
            DO II=2,NIM
            DO IJ=LI(II+IST)+2,LI(II+IST)+NJM
              V(IJ,J+1)=Z(IJ)/H(J+1,J)
            END DO; END DO
          ENDIF
C
C.........APPLY PREVIOUS GIVENS ROTATIONS TO NEW COLUMN
          DO I=1,J-1
            TMP=CS(I)*H(I,J)+SN(I)*H(I+1,J)
            H(I+1,J)=-SN(I)*H(I,J)+CS(I)*H(I+1,J)
            H(I,J)=TMP
          END DO
C
C.........COMPUTE NEW GIVENS ROTATION
          DEN2=SQRT(H(J,J)**2+H(J+1,J)**2)
          IF(DEN2.GT.SMALL) THEN
            CS(J)=H(J,J)/DEN2; SN(J)=H(J+1,J)/DEN2
          ELSE
            CS(J)=1.; SN(J)=0.
          ENDIF
          H(J,J)=CS(J)*H(J,J)+SN(J)*H(J+1,J)
          H(J+1,J)=0.
          ETA(J+1)=-SN(J)*ETA(J)
          ETA(J)=CS(J)*ETA(J)
C
          IF(ABS(ETA(J+1))/(RESOR(IFI)+SMALL).LT.SOR(IFI)) GOTO 300
        END DO
C
C.......BACK-SUBSTITUTION: solve H*y = eta
  300   CONTINUE
        DO I=M,1,-1
          ETA(I)=ETA(I)
          DO JJ=I+1,M
            ETA(I)=ETA(I)-H(I,JJ)*ETA(JJ)
          END DO
          ETA(I)=ETA(I)/(H(I,I)+SMALL)
        END DO
C
C.......UPDATE SOLUTION: x = x0 + V_m * y
        DO I=2,NIM
        DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
          DO JJ=1,M
            FI(IJ)=FI(IJ)+ETA(JJ)*V(IJ,JJ)
          END DO
        END DO; END DO
C
      END DO   ! outer restart loop
C
      RETURN
      END
C
C
C############################################################
      SUBROUTINE ILUSOLVE(RHS,SOL,LW,LS,LPR,UE,UN,K)
C############################################################
C     Forward-backward substitution with ILU(0) factors.
C============================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      DIMENSION RHS(NXYA),SOL(NXYA)
      DIMENSION LW(NXYA),LS(NXYA),LPR(NXYA),UE(NXYA),UN(NXYA)
C     Forward substitution
      DO I=2,NIM
      DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
        SOL(IJ)=(RHS(IJ)-LS(IJ)*SOL(IJ-1)-LW(IJ)*SOL(IJ-NJ))*LPR(IJ)
      END DO; END DO
C     Backward substitution
      DO I=NIM,2,-1
      DO IJ=LI(I+IST)+NJM,LI(I+IST)+2,-1
        SOL(IJ)=SOL(IJ)-UN(IJ)*SOL(IJ+1)-UE(IJ)*SOL(IJ+NJ)
      END DO; END DO
      RETURN
      END
C########################################################
      SUBROUTINE INIT
C########################################################
C     Reads input parameters, grid data, initializes fields.
C     Extended for PIMPLE, SST, gamma-Retheta variables.
C========================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'logic.inc'
      INCLUDE 'rcont.inc'
      INCLUDE 'var.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'bound.inc'
      INCLUDE 'varold.inc'
      INCLUDE 'model.inc'
C
C.....READ INPUT DATA (.cin file)
C   Record  1: TITLE
C   Record  2: LREAD LWRITE LTEST LOUTS LOUTE LTIME KIN
C   Record  3: IMON JMON IPR JPR NPCOR NIGRAD
C   Record  4: SORMAX SLARGE ALFA
C   Record  5: DENS VISC PRANL
C   Record  6: GRAVX GRAVY BETA TH TC TREF
C   Record  7: UIN VIN PIN TIN TEIN EDIN ULID
C   Record  8: ITSTEP NOTT DT GAMT
C   Record  9: LCAL(1..NFI)
C   Record 10: URF(1..NFI)
C   Record 11: SOR(1..NFI)
C   Record 12: NSW(1..NFI)
C   Record 13: GDS(1..NFI)
C   Record 14: LSG(1..NGR)
C   Record 15: NOPIMPLE NPISO LSIMPLEC LGMRES ISCHEME ILIMIT
C   (then BCIN reads inlet values)
C
      READ(5,'(A50)') TITLE
      READ(5,*) LREAD,LWRITE,LTEST,LOUTS,LOUTE,LTIME,KIN
      READ(5,*) IMON,JMON,IPR,JPR,NPCOR,NIGRAD
      READ(5,*) SORMAX,SLARGE,ALFA
      READ(5,*) DENS,VISC,PRANL
      READ(5,*) GRAVX,GRAVY,BETA,TH,TC,TREF
      READ(5,*) UIN,VIN,PIN,TIN,TEIN,EDIN,ULID
      READ(5,*) ITSTEP,NOTT,DT,GAMT
      READ(5,*) (LCAL(I),I=1,NFI)
      READ(5,*) (URF(I),I=1,NFI)
      READ(5,*) (SOR(I),I=1,NFI)
      READ(5,*) (NSW(I),I=1,NFI)
      READ(5,*) (GDS(I),I=1,NFI)
      READ(5,*) (LSG(IK),IK=1,NGR)
C     PIMPLE/SIMPLEC/GMRES/scheme control line
      READ(5,*) NOPIMPLE,NPISO,LSIMPLEC,LGMRES,ISCHEME,ILIMIT
C
C.....READ GRID GEOMETRY
      READ(4) IA,(ITB(1,I),I=1,NXA),(ITB(2,I),I=1,NXA),
     *  (JTB(1,J),J=1,NYA),(JTB(2,J),J=1,NYA),
     *  (LI(I),I=1,NXA),(NIGR(K),K=1,NGR),(NJGR(K),K=1,NGR),
     *  (IGR(K),K=1,NGR),(JGR(K),K=1,NGR),(IJGR(K),K=1,NGR),
     *  NINA1,(NINL(K),K=1,NGR),(IIS(K),K=1,NGR),
     *  (IJI(I),I=1,NINA1),(IJPI(I),I=1,NINA1),
     *  (IJI1(I),I=1,NINA1),(IJI2(I),I=1,NINA1),
     *  NOT1,(NOUT(K),K=1,NGR),(IOS(K),K=1,NGR),
     *  (IJO(I),I=1,NOT1),(IJPO(I),I=1,NOT1),
     *  (IJO1(I),I=1,NOT1),(IJO2(I),I=1,NOT1),
     *  NWT1,(NWAL(K),K=1,NGR),(IWS(K),K=1,NGR),
     *  (IJW(I),I=1,NWT1),(IJPW(I),I=1,NWT1),
     *  (IJW1(I),I=1,NWT1),(IJW2(I),I=1,NWT1),
     *  (NWALI(K),K=1,NGR),(IWAS(K),K=1,NGR),(NWALA(K),K=1,NGR),
     *  NST1,(NSYM(K),K=1,NGR),(ISS(K),K=1,NGR),
     *  (IJS(I),I=1,NST1),(IJPS(I),I=1,NST1),
     *  (IJS1(I),I=1,NST1),(IJS2(I),I=1,NST1),
     *  NOCT1,(NOC(K),K=1,NGR),(IOCS(K),K=1,NGR),
     *  (IJL(I),I=1,NOCT1),(IJR(I),I=1,NOCT1),
     *  (IJOC1(I),I=1,NOCT1),(IJOC2(I),I=1,NOCT1)
C
      READ(4) (X(I),I=1,NXYA),(Y(I),I=1,NXYA),
     *  (XC(I),I=1,NXYA),(YC(I),I=1,NXYA),
     *  (FX(I),I=1,NXYA),(FY(I),I=1,NXYA),
     *  (VOL(I),I=1,NXYA),(SRDW(I),I=1,NWT1),
     *  (XTW(I),I=1,NWT1),(YTW(I),I=1,NWT1),
     *  (SRDS(I),I=1,NST1),(XNS(I),I=1,NST1),(YNS(I),I=1,NST1),
     *  (FOC(I),I=1,NOCT1)
      REWIND 4
      LAXIS=.FALSE.; IF(IA.EQ.1) LAXIS=.TRUE.
C
C.....CHECK MONITORING POINT
      IF(IMON.GT.NIGR(1)-1) IMON=NIGR(1)/2
      IF(JMON.GT.NJGR(1)-1) JMON=NJGR(1)/2
C
C.....DERIVED PARAMETERS
      URFU=1./(URF(IU)+SMALL); URFV=1./(URF(IV)+SMALL)
      DTR=1./MAX(DT,SMALL)
      IF(NOPIMPLE.LT.1) NOPIMPLE=1
      IF(NPISO.LT.1)    NPISO=1
C
C.....INITIALIZE DENSITY AND VISCOSITY
      DO IJ=1,NXYA
        VIS(IJ)=VISC; DEN(IJ)=DENS
        F1SST(IJ)=1.; F2SST(IJ)=1.; CDKW(IJ)=0.
      END DO
C
C.....INITIALIZE FIELD VARIABLES AT ALL GRID LEVELS
      DO IK=1,NGR
        CALL SETIND(IK)
        DO I=2,NIM
          DO IJ=LI(I+IST)+2,LI(I+IST)+NJM
            U(IJ)=UIN; V(IJ)=VIN; P(IJ)=PIN; T(IJ)=TIN
            TE(IJ)=TEIN
            ED(IJ)=EDIN/(BETSTAR*TEIN+SMALL)
            GAM(IJ)=0.
            RETHET(IJ)=1000.
            UO(IJ)=UIN;  VO(IJ)=VIN;  TO(IJ)=TIN
            TEO(IJ)=TEIN; EDO(IJ)=ED(IJ)
            GAMO(IJ)=0.; RETHETO(IJ)=1000.
            UOO(IJ)=UIN; VOO(IJ)=VIN; TOO(IJ)=TIN
            TEOO(IJ)=TEIN; EDOO(IJ)=ED(IJ)
            GAMOO(IJ)=0.; RETHETOO(IJ)=1000.
          END DO
        END DO
      END DO
C
C.....RADIUS: Y for axisymmetric, 1 for 2D planar
      IF(LAXIS) THEN
        DO IJ=1,NXYA
          R(IJ)=Y(IJ)
        END DO
      ELSE
        DO IJ=1,NXYA
          R(IJ)=1.
        END DO
      ENDIF
C
      RETURN
      END
C
C
C########################################################
      SUBROUTINE OUTIN
C########################################################
C     Prints title and parameters to output file.
C========================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'rcont.inc'
      INCLUDE 'logic.inc'
      INCLUDE 'varold.inc'
      INCLUDE 'model.inc'
C
      WRITE(2,'(A50)') TITLE
      WRITE(2,*) '================================================='
      WRITE(2,*) '  CAFFA v2.0 - PIMPLE/SST/gamma-Retheta'
      WRITE(2,*) '     DENSITY     : ',DENS
      WRITE(2,*) '     VISCOSITY   : ',VISC
      WRITE(2,*) '     SORMAX      : ',SORMAX
      WRITE(2,*) '     SIP ALFA    : ',ALFA
      WRITE(2,*) '     NOPIMPLE    : ',NOPIMPLE
      WRITE(2,*) '     NPISO       : ',NPISO
      IF(LSIMPLEC) WRITE(2,*) '     SIMPLEC ACTIVE'
      IF(LGMRES)   WRITE(2,*) '     GMRES SOLVER ACTIVE'
      IF(ISCHEME.EQ.1) WRITE(2,*) '     SCHEME: UDS/CDS blend'
      IF(ISCHEME.EQ.2) WRITE(2,*) '     SCHEME: QUICK'
      IF(ISCHEME.EQ.3) WRITE(2,*) '     SCHEME: linearUpwind'
      IF(ISCHEME.EQ.4) WRITE(2,*) '     SCHEME: linearUpwindV'
      IF(ILIMIT.EQ.1)  WRITE(2,*) '     LIMITER: cellMDlimiter'
      WRITE(2,*) '     k-omega SST + gamma-Retheta ACTIVE'
      IF(LAXIS) WRITE(2,*) '     AXISYMMETRIC'
C
      IF(LCAL(IEN)) THEN
        WRITE(2,*) '     PRANL:', PRANL
        WRITE(2,*) '     TH/TC/TREF: ',TH,TC,TREF
      ENDIF
C
      WRITE(2,*) '  URF: ',(URF(I),I=1,NFI)
      WRITE(2,*) '  SOR: ',(SOR(I),I=1,NFI)
      WRITE(2,*) '  NSW: ',(NSW(I),I=1,NFI)
      WRITE(2,*) '  GDS: ',(GDS(I),I=1,NFI)
      WRITE(2,*) '================================================='
C
      IF(LTIME) THEN
        WRITE(2,*) '     DT       = ',DT
        WRITE(2,*) '     ITSTEP   = ',ITSTEP
        WRITE(2,*) '     NOTT     = ',NOTT
        WRITE(2,*) '     GAMT     = ',GAMT
      ENDIF
C
      RETURN
      END
C
C
C########################################################
      SUBROUTINE SETDAT
C########################################################
C     Assigns values to variable indices and constants.
C========================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'rcont.inc'
      IU=1; IV=2; IP=3; IEN=4
      SMALL=1.E-20; GREAT=1.E+20; ONE=1.0; ZERO=0.
      FLOMOM=0.; FLOMAS=0.; FLOWEN=0.
      FLOWTE=0.; FLOWED=0.; FLOWGAM=0.; FLOWRET=0.
      RETURN
      END
C
C
C########################################################
      SUBROUTINE MODDAT
C########################################################
C     Turbulence model constants: k-omega SST (Menter 2003)
C     and gamma-Retheta (Langtry-Menter 2009).
C========================================================
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'model.inc'
      INCLUDE 'rcont.inc'
C
      ITE1=5; IED1=6; IVIS1=9
      ITE=5; IED=6; IGAM=7; IRET=8; IVIS=9
C
C.....k-omega SST constants (Menter 2003, Table 1)
C     Zone 1 (k-omega near wall):
      SIGK1 =0.85; SIGOM1=0.5
      BET1  =0.075
      GAMSST1=BET1/0.09-SIGOM1*0.41**2/SQRT(0.09)
C     Zone 2 (k-epsilon far field):
      SIGK2 =1.0;  SIGOM2=0.856
      BET2  =0.0828
      GAMSST2=BET2/0.09-SIGOM2*0.41**2/SQRT(0.09)
C     Shared:
      BETSTAR=0.09
      A1SST=0.31
C
C.....Wall-function / log-law constants
      CAPPA =0.41
      ELOG  =8.342
      CTRANS=11.63
      CMU   =0.09
      CMU25 =SQRT(SQRT(CMU))
C
C.....Scalar diffusion (temperature)
      SIGT  =0.85
      SIGTE =SIGK1
      SIGED =SIGOM1
C
C.....gamma-Retheta constants (Langtry-Menter 2009, Table 1)
      CA1TR=2.0; CA2TR=0.06
      CE1TR=1.0; CE2TR=50.
      CTHT=0.03; SIGF=1.0; SIGTH=2.0
C
      RETURN
      END
C###########################################################
      SUBROUTINE OUTRES(K)
C###########################################################
      INCLUDE 'param.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'logic.inc'
      INCLUDE 'rcont.inc'
      INCLUDE 'var.inc'
      INCLUDE 'model.inc'
      IF(LCAL(IU))  CALL PRINT(K,U,'U VEL.')
      IF(LCAL(IV))  CALL PRINT(K,V,'V VEL.')
      IF(LCAL(IP))  CALL PRINT(K,P,'PRESS.')
      IF(LCAL(IEN)) CALL PRINT(K,T,'TEMPER')
      IF(LCAL(ITE)) CALL PRINT(K,TE,'TURB K')
      IF(LCAL(IED)) CALL PRINT(K,ED,'OMEGA ')
      IF(LCAL(IGAM)) CALL PRINT(K,GAM,'GAMMA ')
      IF(LCAL(IRET)) CALL PRINT(K,RETHET,'RETHET')
      IF(LCAL(IVIS)) CALL PRINT(K,VIS,'EDDY V')
      RETURN
      END
C
C
C###################################################################
      SUBROUTINE POST(K,ICOUNT)
C###################################################################
C     Prepares and saves data for post-processing.
C===================================================================
      INCLUDE 'param.inc'
      INCLUDE 'geo.inc'
      INCLUDE 'logic.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'rcont.inc'
      INCLUDE 'var.inc'
      INCLUDE 'varold.inc'
      INCLUDE 'bound.inc'
      INCLUDE 'charac.inc'
      INCLUDE 'coef.inc'
      INCLUDE 'model.inc'
      CHARACTER DSN*3
C
      CALL SETIND(K)
C
C.....FILL O/C-GRID CUT BOUNDARY NODES
      DO I=2,NIM
        IF(ITB(1,I+IST).EQ.10) THEN
          IJB=LI(I+IST)+1; CALL FINDOC(IJB,IJB+1,K)
        ENDIF
        IF(ITB(2,I+IST).EQ.10) THEN
          IJB=LI(I+IST)+NJ; CALL FINDOC(IJB,IJB-1,K)
        ENDIF
      END DO
      DO J=2,NJM
        IF(JTB(1,J+JST).EQ.10) THEN
          IJB=LI(1+IST)+J; CALL FINDOC(IJB,IJB+NJ,K)
        ENDIF
        IF(JTB(2,J+JST).EQ.10) THEN
          IJB=LI(NI+IST)+J; CALL FINDOC(IJB,IJB-NJ,K)
        ENDIF
      END DO
C
C.....BOUNDARY MASS FLUXES FOR POST-PROCESSOR
      DO J=2,NJM
        IJ=LI(1+IST)+J
        RB=0.5*(R(IJ)+R(IJ-1))
        SX=(Y(IJ)-Y(IJ-1))*RB; SY=(X(IJ-1)-X(IJ))*RB
        F1(IJ)=DEN(IJ)*(U(IJ)*SX+V(IJ)*SY)
        IJ=LI(NIM+IST)+J
        RB=0.5*(R(IJ)+R(IJ-1))
        SX=(Y(IJ)-Y(IJ-1))*RB; SY=(X(IJ-1)-X(IJ))*RB
        F1(IJ)=DEN(IJ+NJ)*(U(IJ+NJ)*SX+V(IJ+NJ)*SY)
      END DO
      DO I=2,NIM
        IJ=LI(I+IST)+1
        RB=0.5*(R(IJ)+R(IJ-NJ))
        SX=(Y(IJ-NJ)-Y(IJ))*RB; SY=(X(IJ)-X(IJ-NJ))*RB
        F2(IJ)=DEN(IJ)*(U(IJ)*SX+V(IJ)*SY)
        IJ=LI(I+IST)+NJM
        RB=0.5*(R(IJ)+R(IJ-NJ))
        SX=(Y(IJ-NJ)-Y(IJ))*RB; SY=(X(IJ)-X(IJ-NJ))*RB
        F2(IJ)=DEN(IJ+1)*(U(IJ+1)*SX+V(IJ+1)*SY)
      END DO
C
C.....DISSIPATION FIELD
      DO IJ=IJGR(K)+1,IJGR(K)+NIJ
        AP(IJ)=BETSTAR*ED(IJ)*TE(IJ)
      END DO
C
C.....CORNER VALUES
      IJ=LI(1+IST)+1
      U(IJ)=U(IJ+1); V(IJ)=V(IJ+1); T(IJ)=T(IJ+1)
      TE(IJ)=TE(IJ+1); AP(IJ)=AP(IJ+1); P(IJ)=P(IJ+1)
      GAM(IJ)=GAM(IJ+1); RETHET(IJ)=RETHET(IJ+1)
      IJ=LI(1+IST)+NJ
      U(IJ)=U(IJ-1); V(IJ)=V(IJ-1); T(IJ)=T(IJ-1)
      TE(IJ)=TE(IJ-1); AP(IJ)=AP(IJ-1); P(IJ)=P(IJ-1)
      GAM(IJ)=GAM(IJ-1); RETHET(IJ)=RETHET(IJ-1)
      IJ=LI(NI+IST)+1
      U(IJ)=U(IJ+1); V(IJ)=V(IJ+1); T(IJ)=T(IJ+1)
      TE(IJ)=TE(IJ+1); AP(IJ)=AP(IJ+1); P(IJ)=P(IJ+1)
      GAM(IJ)=GAM(IJ+1); RETHET(IJ)=RETHET(IJ+1)
      IJ=LI(NI+IST)+NJ
      U(IJ)=U(IJ-1); V(IJ)=V(IJ-1); T(IJ)=T(IJ-1)
      TE(IJ)=TE(IJ-1); AP(IJ)=AP(IJ-1); P(IJ)=P(IJ-1)
      GAM(IJ)=GAM(IJ-1); RETHET(IJ)=RETHET(IJ-1)
C
C.....WRITE POST-PROCESSING FILE
      IF(ICOUNT.LT.10)   WRITE(DSN,'(I1,2H  )') ICOUNT
      IF(ICOUNT.GE.10)   WRITE(DSN,'(I2,1H )') ICOUNT
      IF(ICOUNT.GE.100)  WRITE(DSN,'(I3)')      ICOUNT
      WRITE(FILPOS,'(A6,1H.,A3)') NAME,DSN
      OPEN (UNIT=8,FILE=FILPOS,FORM='UNFORMATTED'); REWIND 8
C
      IJST=IJGR(K)+1; IJEN=IJGR(K)+NIJ
      WRITE(8) ITIM,TIME,NI,NJ,NIM,NJM,NIJ,
     *  (X(IJ),IJ=IJST,IJEN),(Y(IJ),IJ=IJST,IJEN),
     *  (XC(IJ),IJ=IJST,IJEN),(YC(IJ),IJ=IJST,IJEN),
     *  (F1(IJ),IJ=IJST,IJEN),(F2(IJ),IJ=IJST,IJEN),
     *  (U(IJ),IJ=IJST,IJEN),(V(IJ),IJ=IJST,IJEN),
     *  (P(IJ),IJ=IJST,IJEN),(T(IJ),IJ=IJST,IJEN),
     *  (TE(IJ),IJ=IJST,IJEN),(AP(IJ),IJ=IJST,IJEN),
     *  (GAM(IJ),IJ=IJST,IJEN),(RETHET(IJ),IJ=IJST,IJEN)
      CLOSE(UNIT=8)
C
C.....RESET BOUNDARY MASS FLUXES
      DO J=2,NJM
        F1(LI(1+IST)+J)=0.; F1(LI(NIM+IST)+J)=0.
      END DO
      DO I=2,NIM
        F2(LI(I+IST)+1)=0.; F2(LI(I+IST)+NJM)=0.
      END DO
      RETURN
      END
C
C
C###################################################################
      SUBROUTINE SRES(K)
C###################################################################
C     Writes restart file (extended for SST/gamma-Retheta).
C===================================================================
      INCLUDE 'param.inc'
      INCLUDE 'logic.inc'
      INCLUDE 'indexc.inc'
      INCLUDE 'var.inc'
      INCLUDE 'varold.inc'
      INCLUDE 'bound.inc'
      INCLUDE 'charac.inc'
      INCLUDE 'model.inc'
      WRITE(FILRES,'(A6,3H.re,I1)') NAME,K
      OPEN (UNIT=3,FILE=FILRES,FORM='UNFORMATTED'); REWIND 3
      IJST=IJGR(K)+1; IJEN=IJGR(K)+NIGR(K)*NJGR(K)
      WRITE(3) K,IJST,IJEN,ITIM,TIME,
     *  (F1(IJ),IJ=IJST,IJEN),(F2(IJ),IJ=IJST,IJEN),
     *  (U(IJ),IJ=IJST,IJEN),(V(IJ),IJ=IJST,IJEN),
     *  (P(IJ),IJ=IJST,IJEN),(T(IJ),IJ=IJST,IJEN),
     *  (TE(IJ),IJ=IJST,IJEN),(ED(IJ),IJ=IJST,IJEN),
     *  (GAM(IJ),IJ=IJST,IJEN),(RETHET(IJ),IJ=IJST,IJEN),
     *  (FMOC(I),I=IOCS(K)+1,IOCS(K)+NOC(K))
      IF(LTIME) WRITE(3)
     *  (UO(IJ),IJ=IJST,IJEN),(VO(IJ),IJ=IJST,IJEN),
     *  (TO(IJ),IJ=IJST,IJEN),(TEO(IJ),IJ=IJST,IJEN),
     *  (EDO(IJ),IJ=IJST,IJEN)
      CLOSE(UNIT=3)
      RETURN
      END
C
C
C###################################################################
      SUBROUTINE FINDOC(IJB,IJN,K)
C###################################################################
      INCLUDE 'param.inc'
      INCLUDE 'bound.inc'
      INCLUDE 'var.inc'
      INCLUDE 'model.inc'
      DO IOC=IOCS(K)+1,IOCS(K)+NOC(K)
        IF(IJN.EQ.IJL(IOC).OR.IJN.EQ.IJR(IOC)) THEN
          U(IJB)=U(IJR(IOC))*FOC(IOC)+U(IJL(IOC))*(1.-FOC(IOC))
          V(IJB)=V(IJR(IOC))*FOC(IOC)+V(IJL(IOC))*(1.-FOC(IOC))
          P(IJB)=P(IJR(IOC))*FOC(IOC)+P(IJL(IOC))*(1.-FOC(IOC))
          T(IJB)=T(IJR(IOC))*FOC(IOC)+T(IJL(IOC))*(1.-FOC(IOC))
          TE(IJB)=TE(IJR(IOC))*FOC(IOC)+TE(IJL(IOC))*(1.-FOC(IOC))
          ED(IJB)=ED(IJR(IOC))*FOC(IOC)+ED(IJL(IOC))*(1.-FOC(IOC))
          GAM(IJB)=GAM(IJR(IOC))*FOC(IOC)+GAM(IJL(IOC))*(1.-FOC(IOC))
          RETHET(IJB)=RETHET(IJR(IOC))*FOC(IOC)
     *      +RETHET(IJL(IOC))*(1.-FOC(IOC))
        ENDIF
      END DO
      RETURN
      END
C
C---------------------------------------------------------------
C     User-supplied boundary conditions and output routines.
C---------------------------------------------------------------
      INCLUDE 'user.f'
C---------------------------------------------------------------

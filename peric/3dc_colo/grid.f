      PROGRAM EXPA
C###################################################################
C#         GENERATION OF RECTILINEAR GRIDS                         #
C#         FOR THE MULTIGRID FLOW PREDICTION CODE                  #
C#         Z. Lilek, M. Peric, Institut fuer Schiffbau, 1995       #
C###################################################################
C     NGIT is the number of grid levels
C     NICV is the number of cells in X-direction in the coarsest grid
C     NJCV is the number of cells in Y-direction in the coarsest grid
C     NKCV is the number of cells in Z-direction in the coarsest grid
      PARAMETER (NGIT=4,NICV=8,NJCV=8,NKCV=8,
     *          NX=NICV*2**(NGIT-1)+2,NY=NJCV*2**(NGIT-1)+2,
     *          NZ=NKCV*2**(NGIT-1)+2,
     *          NXY=NX*NY,NXZ=NX*NZ,NYZ=NY*NZ,NXYZ=NXY*NZ,
     *          NXA=NICV*(2**NGIT-1)+2*NGIT,NYA=NJCV*(2**NGIT-1)+2*NGIT,
     *          NZA=NKCV*(2**NGIT-1)+2*NGIT,
     *          NXYA=NICV*NJCV*(4**NGIT-1)/3+2*(NXA+NYA-2*NGIT),
     *          NXZA=NICV*NKCV*(4**NGIT-1)/3+2*(NXA+NZA-2*NGIT),
     *          NYZA=NJCV*NKCV*(4**NGIT-1)/3+2*(NYA+NZA-2*NGIT),
     *          NXYZA=NICV*NJCV*NKCV*(8**NGIT-1)/7+
     *          2*(4**NGIT-1)/3*(NICV*NJCV+NICV*NKCV+NJCV*NKCV)+
     *          4*(NXA+NYA+NZA-4*NGIT))
      COMMON /COOR/ F(NXYZA),X(NXA),Y(NYA),Z(NZA),XG(NXA),
     *       YG(NYA),ZG(NZA),XALL(NXA),YALL(NYA),ZALL(NZA)
      COMMON /PARAM/ NI,NJ,NK,NIM,NJM,NKM,NIGIT(NGIT),NJGIT(NGIT),
     *       NKGIT(NGIT),IGIT(NGIT),JGIT(NGIT),KGIT(NGIT),IJKGIT(NGIT),
     *       KG1
      common /logic/ LOB,LOT,LOS,LON,LOW,LOE
      LOGICAL LOB,LOT,LOS,LON,LOW,LOE
      COMMON /BC/ LBS(NXZA),LBN(NXZA),LBW(NYZA),LBE(NYZA),
     *            LBB(NXYA),LBT(NXYA),
     *            ISBIJ(NGIT),ISBIK(NGIT),ISBJK(NGIT)
      LOGICAL LPLOT
      CHARACTER*10 FILIN,FILOUT,FILRES
C
C.....OPEN FILES
C
      PRINT *, ' ENTER:  INPUT FILE NAME '
      READ(*,5) FILIN
      PRINT *, ' ENTER: OUTPUT FILE NAME '
      READ(*,5) FILOUT
      PRINT *, ' ENTER: RESULT FILE NAME '
      READ(*,5) FILRES
    5 FORMAT(A10)
      OPEN (UNIT=1,FILE=FILIN)
      OPEN (UNIT=2,FILE=FILOUT)
      OPEN (UNIT=4,FILE=FILRES)
      REWIND 1
      REWIND 2
      REWIND 4
C
C.....GENERATE ONE GRID
C     You can choose to enter data for the generation of any grid between level 1 and 
C     level NGIT (the finest grid). 
C
      PRINT *, ' ENTER GRID LEVEL FOR WHICH DATA WILL BE GIVEN:  '
      READ(1,*) KG1
      CALL GRIDN
C
C.....REFINE GRID TO THE  FINEST LEVEL
C     If the grid generation level was not already the finest level (NGIT), then the 
C     generated grid will be first refined up to the finest level. The expansion/contraction
C     factor will be kept constant, but because the total number of cells for the same 
C     length doubles, the expansion factor becomes square root of the expansion factor of 
C     the coarser grid.
C
      DO 50 K=KG1+1,NGIT
   50 CALL GRIDF
C
C.....DEFINE ALL COARSER GRIDS
C     Once the grid at the finest level is defined, all coarse grids are defined by 
C     merging two cells in each direction from the next finer grid.
C
      CALL GRIDM
C
C.....SET BOUNDARY CONDITION FOR EACH BOUNDARY
C
      CALL SETB
C
C
C.....STORE GRID DATA
C
      WRITE(4,*) LOB,LOT,LOS,LON,LOW,LOE,LBS,LBN,LBW,LBE,
     *           LBB,LBT,ISBIJ,ISBIK,ISBJK,
     *           NIGIT,NJGIT,NKGIT,IGIT,JGIT,KGIT,IJKGIT 
      WRITE(4,*) XALL,YALL,ZALL
C
      STOP
      END
C
C####################################################################
C#                GENERATION OF NEW GRID                            #
C####################################################################
      SUBROUTINE GRIDN
      PARAMETER (NGIT=4,NICV=8,NJCV=8,NKCV=8,
     *          NX=NICV*2**(NGIT-1)+2,NY=NJCV*2**(NGIT-1)+2,
     *          NZ=NKCV*2**(NGIT-1)+2,
     *          NXY=NX*NY,NXZ=NX*NZ,NYZ=NY*NZ,NXYZ=NXY*NZ,
     *          NXA=NICV*(2**NGIT-1)+2*NGIT,NYA=NJCV*(2**NGIT-1)+2*NGIT,
     *          NZA=NKCV*(2**NGIT-1)+2*NGIT,
     *          NXYA=NICV*NJCV*(4**NGIT-1)/3+2*(NXA+NYA-2*NGIT),
     *          NXZA=NICV*NKCV*(4**NGIT-1)/3+2*(NXA+NZA-2*NGIT),
     *          NYZA=NJCV*NKCV*(4**NGIT-1)/3+2*(NYA+NZA-2*NGIT),
     *          NXYZA=NICV*NJCV*NKCV*(8**NGIT-1)/7+
     *          2*(4**NGIT-1)/3*(NICV*NJCV+NICV*NKCV+NJCV*NKCV)+
     *          4*(NXA+NYA+NZA-4*NGIT))
      COMMON /COOR/ F(NXYZA),X(NXA),Y(NYA),Z(NZA),XG(NXA),
     *       YG(NYA),ZG(NZA),XALL(NXA),YALL(NYA),ZALL(NZA)
      COMMON /PARAM/ NI,NJ,NK,NIM,NJM,NKM,NIGIT(NGIT),NJGIT(NGIT),
     *       NKGIT(NGIT),IGIT(NGIT),JGIT(NGIT),KGIT(NGIT),IJKGIT(NGIT),
     *       KG1
      common /logic/ LOB,LOT,LOS,LON,LOW,LOE
      LOGICAL LOB,LOT,LOS,LON,LOW,LOE
      COMMON /BC/ LBS(NXZA),LBN(NXZA),LBW(NYZA),LBE(NYZA),
     *            LBB(NXYA),LBT(NXYA),
     *            ISBIJ(NGIT),ISBIK(NGIT),ISBJK(NGIT)
      DIMENSION YY(500),E(200)
C
C.....CALCULATION OF COORDINATES FOR ONE DIRECTION
C
      PRINT *, ' X-coordinates'
C
C     In each direction, solution domain can be split in two subdomains with cell size
C     increasing (with a constant expansion factor) in the first subdomain and then 
C     reducing (with a constant contraction factor, equal to the reciprocal value of 
C     the expansion factor from the first subdomain). For a uniform grid, choose one
C     subdomain and set the expansion factor to 1.0
C
      DO 200 LL=1,3
      PRINT *, ' Number of subdomains?'
      READ(1,*) NSUB
      NP=1
C
C.....INPUT DATA FOR ONE SUBDOMAIN
C
      DO 100 L=1,NSUB
    5 PRINT *, ' Starting and ending coordinate, number of CV?'
      READ(1,*) XS,XE,N
      IF(L.EQ.1) THEN
        PRINT *, ' ENTER EXPANSION FACTOR: '
        READ(1,*) G
      ELSE
        G=1./G
      ENDIF
C     Solution domain length in this coordinate direction:
      B=XE-XS
C
C.....CALCULATE WIDTH OF THE FIRST CELL AT THE START OF SUBDOMAIN
C     If the expansion factor is 1.0, the width of all cells is the same and equal to B/N; 
C     if the expansion factor is greater or smaller than 1.0, we need to determine the 
C     width of the first cell such that the sum of widths of all cells equals the width of
C     the subdomain, B. A little bit of math (series with DX_i+1 = DX_i*G, where DX_i is the
C     width of the i-th cell and G is the expansion/contraction factor)...
C     
      S=1.
      DO I=1,N-1
        S=S+G**I
      END DO
      A=B/S
C
C.....CALCULATE WIDTH OF EACH CELL IN THE SUBDOMAIN, F(I)
C     When the width of the first cell, A, is known, the width of the second cell is A*G,
C     the width of the third cell is (A*G)*G and so on...
C
      IST=NP
      NP=NP+N
      F(1)=A
      DO 20 I=2,N
   20 F(I)=A*G**(I-1)
C
C.....CALCULATE COODINATES OF GRID POINTS WITHIN CURRENT SUBDOMAIN
C     With known width of each cell, F(I), and the known starting coordinate, XS, the 
C     coordinates of each grid line (CV boundary) can be easily computed as the coordinate
C     of the previous grid line + cell width. Gril line coordinates are first computed as 
C     YY(I) and then copied to X(I), Y(J) or Z(K), depending on which coordinate is 
C     being considered (LL=1 corresponds to X-direction, 2 to Y and 3 to Z direction)
C
      YY(IST)=XS
      DO 40 I=1,N
      II=IST+I
   40 YY(II)=YY(II-1)+F(I)
  100 CONTINUE
C
C.....FINISH CURRENT SUBDOMAIN BY STORING GRID LINE COORDINATES IN CORRECT ARRAYS
C
      NP=NP+1
      YY(NP)=YY(NP-1)
C
C.....X-direction: NI is the number of cells + 2 storage locations for boundary nodes
      IF(LL.EQ.1) THEN
      NI=NP
      NIM=NI-1
      DO 120 I=1,NI
  120 X(I)=YY(I)
C
C.....Y-direction: NJ is the number of cells + 2 storage locations for boundary nodes
      PRINT *, ' Y - Coordinates'
      ELSEIF(LL.EQ.2) THEN
      NJ=NP
      NJM=NJ-1
      DO 125 J=1,NJ
  125 Y(J)=YY(J)
C
C.....Z-direction: NK is the number of cells + 2 storage locations for boundary nodes
      PRINT *, ' Z - Coordinates'
      ELSEIF(LL.EQ.3) THEN
      NK=NP
      NKM=NK-1
      DO 135 K=1,NK
  135 Z(K)=YY(K)
      ENDIF
C
  200 CONTINUE
      RETURN
      END
C
C####################################################################
C#              REFINING COARSE GRID                                #
C####################################################################
      SUBROUTINE GRIDF
      PARAMETER (NGIT=4,NICV=8,NJCV=8,NKCV=8,
     *          NX=NICV*2**(NGIT-1)+2,NY=NJCV*2**(NGIT-1)+2,
     *          NZ=NKCV*2**(NGIT-1)+2,
     *          NXY=NX*NY,NXZ=NX*NZ,NYZ=NY*NZ,NXYZ=NXY*NZ,
     *          NXA=NICV*(2**NGIT-1)+2*NGIT,NYA=NJCV*(2**NGIT-1)+2*NGIT,
     *          NZA=NKCV*(2**NGIT-1)+2*NGIT,
     *          NXYA=NICV*NJCV*(4**NGIT-1)/3+2*(NXA+NYA-2*NGIT),
     *          NXZA=NICV*NKCV*(4**NGIT-1)/3+2*(NXA+NZA-2*NGIT),
     *          NYZA=NJCV*NKCV*(4**NGIT-1)/3+2*(NYA+NZA-2*NGIT),
     *          NXYZA=NICV*NJCV*NKCV*(8**NGIT-1)/7+
     *          2*(4**NGIT-1)/3*(NICV*NJCV+NICV*NKCV+NJCV*NKCV)+
     *          4*(NXA+NYA+NZA-4*NGIT))
      COMMON /COOR/ F(NXYZA),X(NXA),Y(NYA),Z(NZA),XG(NXA),
     *       YG(NYA),ZG(NZA),XALL(NXA),YALL(NYA),ZALL(NZA)
      COMMON /PARAM/ NI,NJ,NK,NIM,NJM,NKM,NIGIT(NGIT),NJGIT(NGIT),
     *       NKGIT(NGIT),IGIT(NGIT),JGIT(NGIT),KGIT(NGIT),IJKGIT(NGIT),
     *       KG1
      common /logic/ LOB,LOT,LOS,LON,LOW,LOE
      LOGICAL LOB,LOT,LOS,LON,LOW,LOE
      COMMON /BC/ LBS(NXZA),LBN(NXZA),LBW(NYZA),LBE(NYZA),
     *            LBB(NXYA),LBT(NXYA),
     *            ISBIJ(NGIT),ISBIK(NGIT),ISBJK(NGIT)
C
C     The coordinates of grid lines at the previous level are copied to XG, YG, ZG
C     arrays, and NI, NJ and NK from previous level are denotes as NIG, NJG and NKG.
C     Note that the number of cells in each direction is NI-2, NJ-2 and NK-2, respectively.
      DO 10 I=1,NI
   10 XG(I)=X(I)
      DO 20 J=1,NJ
   20 YG(J)=Y(J)
      DO 30 K=1,NK
   30 ZG(K)=Z(K)
      NIG=NI
      NJG=NJ
      NKG=NK
C
C.....CALCULATE FINE GRID PARAMETERS
C     Number of cells is doubled, plus 2 boundary nodes (see Figure)
C
      NI=(NIG-2)*2+2
      NJ=(NJG-2)*2+2
      NK=(NKG-2)*2+2
      NIM=NI-1
      NJM=NJ-1
      NKM=NK-1
C
C.....REFINE X-COORDINATES
C
C     First grid line, width of the first cell (labeled as DLE - see loop description)
      X(1)=XG(1)
      DLE=XG(2)-XG(1)
      DO 300 IG=2,NIG-2
C     East side of coarse cell -> X(I); width of coarse cell around node P: DPL (equal to
C     the width of cell around node E for previous IG); width of next cell around node 
C     E -> DLE;expansion factor for fine grid, FX, equals square root of expansion factor on 
C     coarse grid (which is DLE/DLP); width of the first finer cell is DLP1, with of the 
C     second cell is DLP2=DLP1*FX, their sum is DLP1+DLP1*FX = DLP, hence DLP1 = DLP/(1.0+FX)
        I=2*IG-1
        X(I)=XG(IG)
        DLP=DLE
        DLE=XG(IG+1)-XG(IG)
        FX=SQRT(DLE/DLP)
        DLP1=DLP/(1.0+FX)
        X(I-1)=X(I-2)+DLP1
  300 CONTINUE
C     The last cell does not have east neighbor, but the expansion factor is the same as 
C     in the previous cell, i.e. FX; thus, the width of the first fine cell is DLE*FX (both
C     DLE and FX as defined in the last pass through the loop)...
      DLP1=DLE/(1.0+FX)
      X(I+1)=X(I)+DLP1
      X(NIM)=XG(NIG-1)
      X(NI)=X(NIM)
C
C.....REFINE Y-COORDINATES
C
C     Everything is analogous to what was done for X-coordinate direction (DLN instead of DLE)...
      Y(1)=YG(1)
      DLN=YG(2)-YG(1)
      DO 400 JG=2,NJG-2
        J=2*JG-1
        Y(J)=YG(JG)
        DLP=DLN
        DLN=YG(JG+1)-YG(JG)
        FY=SQRT(DLN/DLP)
        DLP1=DLP/(1.0+FY)
        Y(J-1)=Y(J-2)+DLP1
  400 CONTINUE
      DLP1=DLN/(1.0+FY)
      Y(J+1)=Y(J)+DLP1
      Y(NJM)=YG(NJG-1)
      Y(NJ)=Y(NJM)
C
C.....REFINE Z-COORDINATES
C
C     Everything is analogous to what was done for X-coordinate direction (DLT instead of DLE)...
      Z(1)=ZG(1)
      DLT=ZG(2)-ZG(1)
      DO 500 KG=2,NKG-2
        K=2*KG-1
        Z(K)=ZG(KG)
        DLP=DLT
        DLT=ZG(KG+1)-ZG(KG)
        FZ=SQRT(DLT/DLP)
        DLP1=DLP/(1.0+FZ)
        Z(K-1)=Z(K-2)+DLP1
  500 CONTINUE
      DLP1=DLT/(1.0+FZ)
      Z(K+1)=Z(K)+DLP1
      Z(NKM)=ZG(NKG-1)
      Z(NK)=Z(NKM)
C
C     The latest parameters NI, NJ and NK are for the finest grid; they remain saved in 
C     memory and always refer to the finest grid level.
C
      RETURN
      END
C
C####################################################################
C#                GENERATE COARSE GRIDS FROM THE FINEST GRID        #
C####################################################################
      SUBROUTINE GRIDM
      PARAMETER (NGIT=4,NICV=8,NJCV=8,NKCV=8,
     *          NX=NICV*2**(NGIT-1)+2,NY=NJCV*2**(NGIT-1)+2,
     *          NZ=NKCV*2**(NGIT-1)+2,
     *          NXY=NX*NY,NXZ=NX*NZ,NYZ=NY*NZ,NXYZ=NXY*NZ,
     *          NXA=NICV*(2**NGIT-1)+2*NGIT,NYA=NJCV*(2**NGIT-1)+2*NGIT,
     *          NZA=NKCV*(2**NGIT-1)+2*NGIT,
     *          NXYA=NICV*NJCV*(4**NGIT-1)/3+2*(NXA+NYA-2*NGIT),
     *          NXZA=NICV*NKCV*(4**NGIT-1)/3+2*(NXA+NZA-2*NGIT),
     *          NYZA=NJCV*NKCV*(4**NGIT-1)/3+2*(NYA+NZA-2*NGIT),
     *          NXYZA=NICV*NJCV*NKCV*(8**NGIT-1)/7+
     *          2*(4**NGIT-1)/3*(NICV*NJCV+NICV*NKCV+NJCV*NKCV)+
     *          4*(NXA+NYA+NZA-4*NGIT))
      COMMON /COOR/ F(NXYZA),X(NXA),Y(NYA),Z(NZA),XG(NXA),
     *       YG(NYA),ZG(NZA),XALL(NXA),YALL(NYA),ZALL(NZA)
      COMMON /PARAM/ NI,NJ,NK,NIM,NJM,NKM,NIGIT(NGIT),NJGIT(NGIT),
     *       NKGIT(NGIT),IGIT(NGIT),JGIT(NGIT),KGIT(NGIT),IJKGIT(NGIT),
     *       KG1
      common /logic/ LOB,LOT,LOS,LON,LOW,LOE
      LOGICAL LOB,LOT,LOS,LON,LOW,LOE
      COMMON /BC/ LBS(NXZA),LBN(NXZA),LBW(NYZA),LBE(NYZA),
     *            LBB(NXYA),LBT(NXYA),
     *            ISBIJ(NGIT),ISBIK(NGIT),ISBJK(NGIT)
C
C.....DEFINE CONTROL PARAMETERS
C
C     Parameters NI, NJ and NK of the finest grid are the latest ones from the previous
C     step (refinement up to the finest level). These are numbers of nodes in each 
C     direction - equal to the number of cells +2 boundary nodes... These parameters for 
C     coarser grids are also defined as the number of cells + 2, whereas the number of
C     cells at each coarser grid level is equal to the number of cells at the finer level
C     divided by 2... NIGIT(K) is NI for the grid at level K, etc.
      NIGIT(NGIT)=NI
      NJGIT(NGIT)=NJ
      NKGIT(NGIT)=NK
      DO 230 K=NGIT-1,1,-1
      NIGIT(K)=(NIGIT(K+1)-2)/2+2
      NJGIT(K)=(NJGIT(K+1)-2)/2+2
      NKGIT(K)=(NKGIT(K+1)-2)/2+2
  230 CONTINUE
C
C     IGIT(K) is the sum of of NI-parameter for all previous grid levels;
C     JGIT(K) is the sum of of NJ-parameter for all previous grid levels;
C     KGIT(K) is the sum of of NK-parameter for all previous grid levels;
C     IJKGIT(K) is the sum of all nodes for all previous grid levels; number of nodes
C     at each grid level is NI*NJ*NK (includes boundary nodes where boundary values
C     are stored).
C     IALL is the sum of of NI-parameter for all grid levels;
C     JALL is the sum of of NJ-parameter for all grid levels;
C     KALL is the sum of of NK-parameter for all grid levels;
      IGIT(1)=0
      JGIT(1)=0
      KGIT(1)=0
      IJKGIT(1)=0
      DO 240 K=2,NGIT
        IGIT(K)=IGIT(K-1)+NIGIT(K-1)
        JGIT(K)=JGIT(K-1)+NJGIT(K-1)
        KGIT(K)=KGIT(K-1)+NKGIT(K-1)
  240 IJKGIT(K)=IJKGIT(K-1)+NIGIT(K-1)*NJGIT(K-1)*NKGIT(K-1)
      IALL=IGIT(NGIT)+NI
      JALL=JGIT(NGIT)+NJ
      KALL=KGIT(NGIT)+NK
C
C.....FINAL DEFINITION OF GRIDS AT ALL LEVELS
C     Grid at level NGIT-1 contains every second grid line of the finest grid;
C     Grid at level NGIT-2 contains every fourth grid line of the finest grid;
C     Grid at level L contains every 2**(NGIT-L)th grid line of the finest grid...
C     Grid line coordinates are stored in single arrays for all levels, XALL,  
C     YALL and ZALL, starting with grid level 1. For example, in X-direction, the
C     coordinates for grid level L start at IGIT(L)+1 and end at IGIT(L)+NIGIT(L).
C     The analogous procedure applies for the other two coordinates.
C
C     Loop over all grid levels
C
      DO 270 L=1,NGIT
        ISTEP=2**(NGIT-L)
        IGI=IGIT(L)
        IGJ=JGIT(L)
        IGK=KGIT(L)
C
C.....X-direction
C
        DO 250 I=1,NI,ISTEP
          IGI=IGI+1
          XALL(IGI)=X(I)
  250   CONTINUE
        IF(L.NE.NGIT) XALL(IGI+1)=XALL(IGI)
C
C.....Y-direction
C
        DO 260 J=1,NJ,ISTEP
          IGJ=IGJ+1
          YALL(IGJ)=Y(J)
  260   CONTINUE
        IF(L.NE.NGIT) YALL(IGJ+1)=YALL(IGJ)
C
C.....Z-direction
C
        DO 265 K=1,NK,ISTEP
          IGK=IGK+1
          ZALL(IGK)=Z(K)
  265   CONTINUE
        IF(L.NE.NGIT) ZALL(IGK+1)=ZALL(IGK)
C
  270 CONTINUE
C
      RETURN
      END
C
C
C#######################################################################
      SUBROUTINE  SETB
C#######################################################################
C     Here boundary condition types are assigned to boundary cell faces:
C     1 - Inlet boundary type
C     2 - Outlet boundary type
C     3 - Symmetry plane boundary type
C     4 - Wall boundary type (fixed wall, zero velocity)
C     41 - Moving wall boundary type (moving lid in a lid-driven cavity flow)
C     Logical variables LOB, LOT, LOS, LON, LOW, LOE are used to identify whether
C     there are outlet boundary types at bottom, top, south, north, west and east
C     boundaries, respectively.
c
      PARAMETER (NGIT=4,NICV=8,NJCV=8,NKCV=8,
     *          NX=NICV*2**(NGIT-1)+2,NY=NJCV*2**(NGIT-1)+2,
     *          NZ=NKCV*2**(NGIT-1)+2,
     *          NXY=NX*NY,NXZ=NX*NZ,NYZ=NY*NZ,NXYZ=NXY*NZ,
     *          NXA=NICV*(2**NGIT-1)+2*NGIT,NYA=NJCV*(2**NGIT-1)+2*NGIT,
     *          NZA=NKCV*(2**NGIT-1)+2*NGIT,
     *          NXYA=NICV*NJCV*(4**NGIT-1)/3+2*(NXA+NYA-2*NGIT),
     *          NXZA=NICV*NKCV*(4**NGIT-1)/3+2*(NXA+NZA-2*NGIT),
     *          NYZA=NJCV*NKCV*(4**NGIT-1)/3+2*(NYA+NZA-2*NGIT),
     *          NXYZA=NICV*NJCV*NKCV*(8**NGIT-1)/7+
     *          2*(4**NGIT-1)/3*(NICV*NJCV+NICV*NKCV+NJCV*NKCV)+
     *          4*(NXA+NYA+NZA-4*NGIT))
      COMMON /COOR/ F(NXYZA),X(NXA),Y(NYA),Z(NZA),XG(NXA),
     *       YG(NYA),ZG(NZA),XALL(NXA),YALL(NYA),ZALL(NZA)
      COMMON /PARAM/ NI,NJ,NK,NIM,NJM,NKM,NIGIT(NGIT),NJGIT(NGIT),
     *       NKGIT(NGIT),IGIT(NGIT),JGIT(NGIT),KGIT(NGIT),IJKGIT(NGIT),
     *       KG1
      common /logic/ LOB,LOT,LOS,LON,LOW,LOE
      LOGICAL LOB,LOT,LOS,LON,LOW,LOE
      COMMON /BC/ LBS(NXZA),LBN(NXZA),LBW(NYZA),LBE(NYZA),
     *            LBB(NXYA),LBT(NXYA),
     *            ISBIJ(NGIT),ISBIK(NGIT),ISBJK(NGIT)
C
C     Boundary types are defined first for the coarsest level...
C
      NI=NIGIT(1)
      NJ=NJGIT(1)
      NK=NKGIT(1)
      NIJ=NI*NJ
C
C....SET TYPES OF BOUNDARY CONDITIONS
C    
C.....BOTTOM: How many boundary types on bottom boundary?
      READ(1,*) NBTB
C
C     LB - boundary type; IS, IE: start and end cell index I for this boundary type;
C     JS, JE: start and end cell index J for this boundary type;
C     Boundary type is assigned to each cell face in the bottom boundary; array LBB(IJ)
C     defines boundary type for each face (I,J), stored in a one-dimensional manner,
C     first in J-direction along line IS, then proceding to IS+1, IS+2 etc. up to IE
      DO 60 N=1,NBTB
        READ(1,*) LB,IS,IE,JS,JE
        IF(LB.EQ.2) LOB = .TRUE.
        DO 55 I=IS,IE
          II=(I-1)*NJ
          DO 55 J=JS,JE
            IJ=II+J
            LBB(IJ)=LB
   55     CONTINUE
   60   CONTINUE
C     
C.....TOP: How many boundary types on bottom boundary?
      READ(1,*) NBTT
      DO 70 N=1,NBTT
        READ(1,*) LB,IS,IE,JS,JE
        IF(LB.EQ.2) LOT=.TRUE.
        DO 65 I=IS,IE
          II=(I-1)*NJ
          DO 65 J=JS,JE
            IJ=II+J
            LBT(IJ)=LB
   65     CONTINUE
   70   CONTINUE
C     
C.....SOUTH: How many boundary types on bottom boundary?
      READ(1,*) NBTS
      DO 80 N=1,NBTS
        READ(1,*) LB,IS,IE,KS,KE
        IF(LB.EQ.2) LOS=.TRUE.
        DO 75 I=IS,IE
          II=(I-1)*NK
          DO 75 K=KS,KE
            IK=II+K
            LBS(IK)=LB
   75     CONTINUE
   80   CONTINUE
C     
C.....NORTH: How many boundary types on bottom boundary?
      READ(1,*) NBTN
      DO 90 N=1,NBTN
        READ(1,*) LB,IS,IE,KS,KE
        IF(LB.EQ.2) LON=.TRUE.
        DO 85 I=IS,IE
          II=(I-1)*NK
          DO 85 K=KS,KE
            IK=II+K
            LBN(IK)=LB
   85     CONTINUE
   90   CONTINUE
C     
C.....WEST: How many boundary types on bottom boundary?
      READ(1,*) NBTW
      DO 100 N=1,NBTW
        READ(1,*) LB,JS,JE,KS,KE
        IF(LB.EQ.2) LOW=.TRUE.
        DO 95 J=JS,JE
          JJ=(J-1)*NK
          DO 95 K=KS,KE
            JK=JJ+K
            LBW(JK)=LB
   95     CONTINUE
  100   CONTINUE
C
C.....EAST: How many boundary types on bottom boundary?
      READ(1,*) NBTE
      DO 110 N=1,NBTE
        READ(1,*) LB,JS,JE,KS,KE
        IF(LB.EQ.2) LOE=.TRUE.
        DO 105 J=JS,JE
          JJ=(J-1)*NK
          DO 105 K=KS,KE
            JK=JJ+K
            LBE(JK)=LB
  105     CONTINUE
  110   CONTINUE
C
C.....ISBIJ(L) defines the number of nodes in (I,J) plane for all grid levels up to L-1
C.....ISBIK(L) defines the number of nodes in (I,J) plane for all grid levels up to L-1
C.....ISBIJ(L) defines the number of nodes in (I,J) plane for all grid levels up to L-1

      ISBIJ(1)=0
      ISBIK(1)=0
      ISBJK(1)=0
      DO 150 MGR=2,NGIT
        NI=NIGIT(MGR-1)
        NJ=NJGIT(MGR-1)
        NK=NKGIT(MGR-1)
        NIJ=NI*NJ
        NIK=NI*NK
        NJK=NJ*NK
        ISBIJ(MGR)=ISBIJ(MGR-1)+NIJ 
        ISBIK(MGR)=ISBIK(MGR-1)+NIK 
        ISBJK(MGR)=ISBJK(MGR-1)+NJK 
  150 CONTINUE
C
C.....DEFINE BOUNDARY TYPES FOR ALL FINER GRIDS
C
      DO 200 MGR=1,NGIT-1
C
C     Coarse grid parameters
        NI=NIGIT(MGR)
        NJ=NJGIT(MGR)
        NK=NKGIT(MGR)
        ISTIJG=ISBIJ(MGR)
        ISTIKG=ISBIK(MGR)
        ISTJKG=ISBJK(MGR)
C
C     Fine grid parameters
        ISTIJF=ISBIJ(MGR+1)
        ISTIKF=ISBIK(MGR+1)
        ISTJKF=ISBJK(MGR+1)
C
C     Assign boundary types for boundary faces of finer grids according to types set 
C     at the coarsest grid level
        CALL SETGF(LBB,NI,NJ,ISTIJG,ISTIJF)
        CALL SETGF(LBT,NI,NJ,ISTIJG,ISTIJF)
        CALL SETGF(LBS,NI,NK,ISTIKG,ISTIKF)
        CALL SETGF(LBN,NI,NK,ISTIKG,ISTIKF)
        CALL SETGF(LBW,NJ,NK,ISTJKG,ISTJKF)
        CALL SETGF(LBE,NJ,NK,ISTJKG,ISTJKF)
 200  CONTINUE
      RETURN
      END
C
C
      SUBROUTINE SETGF(LFI,NIG,NJG,ISTG,ISTF)
      DIMENSION LFI(1)
C
C.....This soubroutine works in one plane, which can be (I,J) or (I,K) or (J,K) plane,
C     depending on the parameters passed on to it (see calling statements)
C     NJF is the number of nodes in the finer grid for the direction defined by NJG 
C     (number of cells in coarse grid + 2 boundary nodes)
      NJF=(NJG-2)*2+2
      NIMG=NIG-1
      NJMG=NJG-1
C
C     Loop over cell faces (boundary indices 1 and NIG, and 1 and NJG, are not relevant
C     II defines number of nodes (including boundary nodes) along line defined by NJG 
C     for all lines up to I-1. Coarse grid face has the index IJG; it contains 4 fine
C     grid faces. The lowest fine-grid face index is IJF; the next one is IJF+1, the 
C     other two are offset by NJF because they are on the east side of the first row...
C
      DO 10 I=2,NIMG
        II=(I-1)*NJG
        IF=I*2-2
        IIF=(IF-1)*NJF
        DO 10 J=2,NJMG
          IJG=ISTG+II+J
          IJF=ISTF+IIF+2*J-2
          LFI(IJF)=LFI(IJG)
          LFI(IJF+1)=LFI(IJG)
          LFI(IJF+NJF)=LFI(IJG)
          LFI(IJF+NJF+1)=LFI(IJG)
   10 CONTINUE
C
      RETURN
      END

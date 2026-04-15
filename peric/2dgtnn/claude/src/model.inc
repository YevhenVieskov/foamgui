C==========================================================
C     model.inc  -  turbulence model constants
C     k-omega SST (Menter 2003) + gamma-Retheta (Langtry 2009)
C==========================================================
C     Variable indices
      COMMON /MDLC/ ITE1,IED1,IVIS1,
C     SST sigma constants (zone1/zone2)
     *  SIGK1,SIGK2,SIGOM1,SIGOM2,
C     SST beta constants
     *  BET1,BET2,BETSTAR,
C     SST gamma production constants
     *  GAMSST1,GAMSST2,
C     SST other
     *  A1SST,CAPPA,ELOG,CTRANS,CMU25,CMU,
C     Diffusion for scalars
     *  SIGT,SIGTE,SIGED,
C     SST blending functions and cross-diffusion
     *  F1SST(NXYA),F2SST(NXYA),CDKW(NXYA),
C     Gamma-Retheta constants
     *  CA1TR,CA2TR,CE1TR,CE2TR,CTHT,SIGF,SIGTH

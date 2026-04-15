C##########################################################
      PARAMETER (NXYA=200000, NGR=5, NINA=500, NOT=500, NWT=5000,
     *           NST=500, NOCT=500, NFI=30, NGM=150)
C##########################################################
C     NFI=30 for extended variable set
C
      INTEGER IU,IV,IP,IPIMPLE,IEN,IK,IOMEGA,IGAMMA,IRET,INUT
      INTEGER IPROD,IDEST,IF1,IF2,IF3,IBLEND1,IBLEND2
      INTEGER ISCHEME, ILIMITER
      PARAMETER (IU=1, IV=2, IP=3, IPIMPLE=4, IEN=5, IK=6, 
     *           IOMEGA=7, IGAMMA=8, IRET=9, INUT=10)
      PARAMETER (IPROD=11, IDEST=12, IF1=13, IF2=14, IF3=15,
     *           IBLEND1=16, IBLEND2=17, ISCHEME=18, ILIMITER=19)
C
C     Convection scheme selection
C     1 = UDS, 2 = CDS, 3 = QUICK, 4 = linearUpwind, 5 = linearUpwindV
      INTEGER ICONV_SCHEME
      PARAMETER (ICONV_SCHEME=4)
C
C     Gradient limiter selection
C     1 = none, 2 = cellMDLimited, 3 = Venkatakrishnan, 4 = BarthJespersen
      INTEGER IGRAD_LIMITER
      PARAMETER (IGRAD_LIMITER=2)
C
C     Turbulence model selection
      INTEGER ITURB
      PARAMETER (ITURB=4)
C     1 = k-epsilon, 2 = k-omega, 3 = k-omega SST, 4 = SST-gamma-Re_theta
C
C     Pressure-velocity coupling algorithm selection
      INTEGER IALGO
      PARAMETER (IALGO=4)
C     1 = SIMPLE, 2 = SIMPLEC, 3 = PISO, 4 = PIMPLE
C
C     Linear solver selection
      INTEGER LSOLVER
      PARAMETER (LSOLVER=2)
C     1 = SIP, 2 = GMRES, 3 = ICCG
C
C     GMRES parameters
      INTEGER MAXIT_GMRES, RESTART, PREC_TYPE
      PARAMETER (MAXIT_GMRES=1000, RESTART=50, PREC_TYPE=1)
C
C     PIMPLE control parameters
      INTEGER N_CORR_PIMPLE, N_NONORTH_CORR
      REAL PIMPLE_URF, SIMPLEC_FACTOR
      PARAMETER (N_CORR_PIMPLE=3, N_NONORTH_CORR=2)
      PARAMETER (PIMPLE_URF=0.9, SIMPLEC_FACTOR=0.8)
C
C     Turbulence model constants
      REAL ALPHA1, ALPHA2, BETA1, BETA2, BETA_STAR
      REAL SIGMA_K1, SIGMA_K2, SIGMA_OMEGA1, SIGMA_OMEGA2
      REAL A1, C_LIM, CA1, CA2, CE1, CE2, C_SEP, C_THETA
      REAL SIGMA_GAMMA, SIGMA_RETHETA
      
      PARAMETER (ALPHA1=5.0/9.0, ALPHA2=0.44)
      PARAMETER (BETA1=0.075, BETA2=0.0828, BETA_STAR=0.09)
      PARAMETER (SIGMA_K1=0.85, SIGMA_K2=1.0)
      PARAMETER (SIGMA_OMEGA1=0.5, SIGMA_OMEGA2=0.856)
      PARAMETER (A1=0.31, C_LIM=10.0)
      PARAMETER (CA1=2.0, CA2=0.06, CE1=1.0, CE2=50.0)
      PARAMETER (C_SEP=2.0, C_THETA=0.03)
      PARAMETER (SIGMA_GAMMA=1.0, SIGMA_RETHETA=1.0)
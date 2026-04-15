C==========================================================
C     rcont.inc  -  real control parameters
C==========================================================
      COMMON /RCNT/ URF(NFI),GDS(NFI),SOR(NFI),NSW(NFI),
     *  DENS,VISC,PRANL,GRAVX,GRAVY,BETA,TH,TC,TREF,
     *  UIN,VIN,PIN,TIN,TEIN,EDIN,ULID,
     *  FLOMOM,FLOMAS,FLOWEN,FLOWTE,FLOWED,FLOWGAM,FLOWRET,
     *  ITSTEP,NOTT,DT,DTR,GAMT,SORMAX,SLARGE,ALFA,
     *  SMALL,GREAT,ONE,ZERO,RESOR(NFI),RNOR(NFI),
     *  URFU,URFV,NPCOR,NIGRAD,
     *  NOPIMPLE,NPISO,ISCHEME,ILIMIT,
     *  IU,IV,IP,IEN,ITE,IED,IGAM,IRET,IVIS,
     *  IMON,JMON,IPR,JPR,KIN,IJPR

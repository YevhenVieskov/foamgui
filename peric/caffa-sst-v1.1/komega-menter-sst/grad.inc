      REAL*8 DPX,DPY,
     *       DUX,DUY,
     *       DVX,DVY,
     *       DTEX,DTEY,
     *       DEDX,DEDY
     
      REAL*8 DFXO,DFYO

      COMMON /GRAD/ DPX(NXYA),DPY(NXYA),
     *              DUX(NXYA),DUY(NXYA),
     *              DVX(NXYA),DVY(NXYA),
     *              DTEX(NXYA),DTEY(NXYA),
     *              DEDX(NXYA),DEDY(NXYA)

      COMMON /GROLD/ DFXO(NXYA),DFYO(NXYA)

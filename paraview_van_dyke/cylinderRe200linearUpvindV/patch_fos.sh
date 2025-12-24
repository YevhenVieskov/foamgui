startTime=0
endTime=400
purgeWrite=20
writeInterval=0.5
writeIntervalForces=0.25
executeInterval=1
magUInf=1
lRef=1
Aref=1
cutplane_fname="FOcuttingPlane"
probes_fname="FOprobesCylinder"
path_fos="./system/FOs"


change_record_parameters(){
    local filename="$1"
    local object="$2"
    foamDictionary "$path_fos/$filename"   -entry "$object.timeStart"        -set  "$startTime"
    foamDictionary "$path_fos/$filename"   -entry "$object.timeEnd"          -set  "$endTime"
    foamDictionary "$path_fos/$filename"   -entry "$object.executeInterval"  -set  "$executeInterval"
    foamDictionary "$path_fos/$filename"   -entry "$object.writeInterval"    -set  "$writeInterval"
}

#Edit controlDict change fvScheme, fvSolutions

#Edit ControlDict include files
change_record_parameters  FOturbulenceFields  turbulenceFields1
change_record_parameters  FOQ Q1
change_record_parameters  FOadd add1
change_record_parameters  FOcomponents components1
change_record_parameters  FOcontinuityError continuityError1
change_record_parameters  FOCourantNo CourantNo1
change_record_parameters  FOddt ddt1
change_record_parameters  FOddt2 ddt21
change_record_parameters  FOdiv div1
change_record_parameters  FOdiv div2
change_record_parameters  FOenstrophy enstrophy1
change_record_parameters  FOfieldAverage fieldAverage
change_record_parameters  FOflowType flowType1
change_record_parameters  FOflux flux1
change_record_parameters  FOgrad grad1
change_record_parameters  FOgrad grad2
change_record_parameters  FOhistogram histogram1
change_record_parameters  FOLambda2 Lambda21
change_record_parameters  FOLambVector LambVector1
change_record_parameters  FOlog log1
change_record_parameters  FOpow pow1
change_record_parameters  FOnorm norm_U_L1
change_record_parameters  FOnorm norm_U_L2
change_record_parameters  FOnorm norm_U_Lp
change_record_parameters  FOnorm norm_U_max
change_record_parameters  FOnorm norm_U_composite
change_record_parameters  FOnorm norm_k_field
change_record_parameters  FOsubtract subtract1
change_record_parameters  FOvalueAverage valueAverage1
change_record_parameters  FOvolFieldValue volFieldValue1_none_none
change_record_parameters  FOmag mag1
change_record_parameters  FOmag mag2
change_record_parameters  FOmagSqr magSqr1
change_record_parameters  FOmagSqr magSqr2
change_record_parameters  FOmassFlow inMassFlow
change_record_parameters  FOmassFlow outMassFlow
change_record_parameters  FOmomentum momentum1
change_record_parameters  FOmomentumError continuityError1
change_record_parameters  FOnearWallFields nearWallFields1
change_record_parameters  FOPecletNo PecletNo1
change_record_parameters  FOpressure pressure1
change_record_parameters  FOpressure pressure2
change_record_parameters  FOpressure pressure3
change_record_parameters  FOpressure pressure4
change_record_parameters  FOsolverInfo solverInfo1
change_record_parameters  FOstreamFunction streamFunction1
change_record_parameters  FOvolFieldValue volFieldValue1_none_none
change_record_parameters  FOvolFieldValue volFieldValue1_min_none
change_record_parameters  FOvolFieldValue volFieldValue1_max_none
change_record_parameters  FOvolFieldValue volFieldValue1_sum_none
change_record_parameters  FOvolFieldValue volFieldValue1_sumMag_none
change_record_parameters  FOvolFieldValue volFieldValue1_average_none
change_record_parameters  FOvolFieldValue volFieldValue1_volAverage_none
change_record_parameters  FOvolFieldValue volFieldValue1_volIntegrate_none
change_record_parameters  FOvolFieldValue volFieldValue1_CoV_none
change_record_parameters  FOvolFieldValue volFieldValue1_min_none_cellzone
change_record_parameters  FOvolFieldValue volFieldValue1_max_none_cellzone
change_record_parameters  FOvolFieldValue volFieldValue1_sum_none_cellzone
change_record_parameters  FOvolFieldValue volFieldValue1_sumMag_none_cellzone
change_record_parameters  FOvolFieldValue volFieldValue1_average_none_cellzone
change_record_parameters  FOvolFieldValue volFieldValue1_volAverage_none_cellzone
change_record_parameters  FOvolFieldValue volFieldValue1_volIntegrate_none_cellzone
change_record_parameters  FOvolFieldValue volFieldValue1_CoV_none_cellzone
change_record_parameters  FOvorticity vorticity1
change_record_parameters  FOwallShearStress wallShearStress1
change_record_parameters  FOwallShearStress magWallShearStress1
change_record_parameters  FOwriteCellCentres writeCellCentres1
change_record_parameters  FOwriteCellVolumes writeCellVolumes1
change_record_parameters  FOyPlus yPlus1
change_record_parameters  FOzeroGradient zeroGradient1
change_record_parameters  FOzeroGradient zeroGradient2
change_record_parameters  FOminMax minmaxdomain1
change_record_parameters  FOgraphFunctionObject residualGraph1
change_record_parameters  FOgraphFunctionObject forceCoeffsGraph1
change_record_parameters  "$cutplane_fname" surfaces
change_record_parameters  "$probes_fname" probes


change_record_parameters  FOforces  forces_object1
change_record_parameters  FOforces  forceCoeffs_object1

foamDictionary "$path_fos/FOforces"   -entry forceCoeffs_object1.magUInf        -set  "$magUInf"
foamDictionary "$path_fos/FOforces"   -entry forceCoeffs_object1.lRef           -set  "$lRef"
foamDictionary "$path_fos/FOforces"   -entry forceCoeffs_object1.Aref           -set  "$Aref"

foamDictionary "$path_fos/FOforces"   -entry forces_object1.writeInterval       -set  "$writeIntervalForces"
foamDictionary "$path_fos/FOforces"   -entry forceCoeffs_object1.writeInterval  -set  "$writeIntervalForces"

foamDictionary "$path_fos/$probes_fname"   -entry probes.writeInterval    -set  "$writeIntervalForces"

foamDictionary "$path_fos/FOgraphFunctionObject"   -entry residualGraph1.writeControl        -set  "writeTime"
foamDictionary "$path_fos/FOgraphFunctionObject"   -entry forceCoeffsGraph1.writeControl     -set  "writeTime"
foamDictionary "$path_fos/FOgraphFunctionObject"   -entry residualGraph1.writeInterval       -set  "-1"
foamDictionary "$path_fos/FOgraphFunctionObject"   -entry forceCoeffsGraph1.writeInterval    -set  "-1"



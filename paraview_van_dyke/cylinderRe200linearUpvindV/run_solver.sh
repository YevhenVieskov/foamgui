#!/bin/bash

#mesh_dir=$1
#potential_dir=$2
#steady_dir=$3
#unsteady_dir=$4
#/bin/bash

nprocs=4

foamDictionary   system/decomposeParDict -entry numberOfSubdomains -set $nprocs

rm -rf 0 > /dev/null 2>&1

cp -r 0.org 0

#cp ./system/fvSchemes.potential ./system/fvSchemes
#cp ./system/fvSolution.potential ./system/fvSolution
#potentialFoam  -initialiseUBCs -writep -writePhi
setFields  | tee log.setFields_init

cp ./system/fvSchemes.init ./system/fvSchemes
cp ./system/fvSolution.petc ./system/fvSolution

decomposePar

mpirun -np $nprocs pimpleFoam   -parallel | tee log.solver



reconstructPar

#rm -rf process*








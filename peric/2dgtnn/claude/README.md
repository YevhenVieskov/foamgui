# CAFFA v2.0 — Enhanced CFD Solver

**Based on:** Ferziger, Perić & Street, *Computational Methods for Fluid Dynamics*, Springer, 4th Ed. 2020  
**Original:** M. Perić & M. Schmid, Hamburg 1997 (v1.3, k-omega model)

---

## What is New in v2.0

| Feature | Description |
|---|---|
| **PIMPLE algorithm** | OpenFOAM-style: `NOPIMPLE` outer + `NPISO` inner correctors |
| **SIMPLEC coupling** | Modified Rhie-Chow with AP−ΣNB denominator (Vandoormaal & Raithby 1984) |
| **GMRES(m) solver** | Restarted GMRES with ILU(0) preconditioner (Saad & Schultz 1986) |
| **k-ω SST model** | Menter 2003 with F1/F2 blending, production limiter, sublayer BC |
| **γ-Reθ model** | Langtry-Menter 2009 transitional model (2 extra PDEs) |
| **QUICK scheme** | Leonard 1979, 3rd-order upwind-biased convection |
| **linearUpwind** | Gradient-based face reconstruction (scalar fields) |
| **linearUpwindV** | Gradient-based face reconstruction (vector, consistent tensor) |
| **cellMDlimiter** | Barth-Jespersen multidimensional slope limiter (OpenFOAM-style) |

---

## File Structure

```
caffa_v2.0/
├── src/
│   ├── caffa.f             ← Complete main source (2633 lines)
│   ├── user.f              ← User BCs (original, copy per case)
│   ├── param.inc           ← Array dimensions
│   ├── indexc.inc          ← Grid index common block
│   ├── logic.inc           ← Logical control variables
│   ├── rcont.inc           ← Real control parameters (extended)
│   ├── var.inc             ← Field variables (U,V,P,T,k,ω,γ,Reθ,μt)
│   ├── geo.inc             ← Geometry arrays
│   ├── varold.inc          ← Previous time-step fields
│   ├── coef.inc            ← Linear system coefficients
│   ├── grad.inc            ← Gradient arrays
│   ├── bound.inc           ← Boundary index arrays
│   ├── model.inc           ← SST + γ-Reθ constants & blending
│   └── charac.inc          ← Character variables (filenames)
├── test/
│   ├── test_caffa_fortuno.f90  ← Unit tests (Fortuno framework)
│   ├── test_caffa_pfunit.f90   ← Unit tests (pFUnit framework)
│   └── test_caffa_ftnunit.f90  ← Unit tests (Ftnunit framework)
├── cases/
│   ├── foil00.cin          ← Control input (foil case)
│   ├── foil00.gin          ← Grid generator input
│   └── foil00.pin          ← Post-processor input
└── README.md
```

---

## New `.cin` Control File Format

All original records unchanged. **Add one new line** after `LSG`:

```
NOPIMPLE  NPISO  LSIMPLEC  LGMRES  ISCHEME  ILIMIT
```

| Parameter | Type | Description |
|---|---|---|
| `NOPIMPLE` | INT | Number of outer PIMPLE correctors (1 = SIMPLE/PISO) |
| `NPISO` | INT | Number of inner PISO correctors (1 = SIMPLE) |
| `LSIMPLEC` | LOGICAL | `.TRUE.` to enable SIMPLEC pressure coupling |
| `LGMRES` | LOGICAL | `.TRUE.` to use GMRES instead of SIP for U,V |
| `ISCHEME` | INT | 1=UDS/CDS blend, 2=QUICK, 3=linearUpwind, 4=linearUpwindV |
| `ILIMIT` | INT | 0=no limiter, 1=cellMDlimiter on gradients |

### Example (PIMPLE + QUICK + cellMDlimiter):
```
3  2  F  F  2  1     NOPIMPLE NPISO LSIMPLEC LGMRES ISCHEME ILIMIT
```

### Example (PISO + SIMPLEC + GMRES):
```
1  3  T  T  1  0     NOPIMPLE NPISO LSIMPLEC LGMRES ISCHEME ILIMIT
```

### Variable indices (NFI = 11):
```
IU=1  IV=2  IP=3  IEN=4  ITE=5  IED=6  IGAM=7  IRET=8  IVIS=9
```

### `LCAL`, `URF`, `SOR`, `NSW`, `GDS` now have 11 entries:
```
T T T F T T T T T F F        (LCAL: U V P T k omega gamma Retheta vis - -)
0.6 0.6 0.1 0.8 0.7 0.7 0.9 0.9 1.0 0.0 0.0   (URF)
0.1 0.1 0.001 0.01 0.1 0.1 0.1 0.1 0.0 0.0 0.0  (SOR)
1 1 20 1 3 3 3 3 0 0 0       (NSW)
0.5 0.5 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0     (GDS)
```

---

## Algorithm Details

### PIMPLE (OpenFOAM-style)
```
FOR each outer iteration LS = 1..LSG(KGR):
  FOR LOUTER = 1..NOPIMPLE:
    1. CALCUV  → solve U*, V* (momentum predictor)
    FOR LPISO = 1..NPISO:
      2. CALCP   → pressure correction p', correct U,V,F,p
    END FOR
  END FOR
  3. CALCSC(T), CALCSC(k), CALCSC(ω), CALCSC(γ), CALCSC(Reθ)
  4. MODVIS_SST → update μt
```

### SIMPLEC (Vandoormaal & Raithby 1984)
In `FLUXM`: face pressure coefficient uses `APeff = AP − ΣNB`  
instead of SIMPLE's `APeff = AP`. This gives stronger p-v coupling
and faster convergence without under-relaxation of pressure.

### GMRES(m) with ILU(0)
- Krylov dimension: `NKRYL = 50` (set in `param.inc`)
- Preconditioner: same ILU(0) pattern as SIP solver
- Restart: after m=NKRYL steps, restart from current solution
- Convergence: relative residual < `SOR(IFI)`

### k-ω SST (Menter 2003)
- Zone 1 (near-wall): σ_k1=0.85, σ_ω1=0.5, β1=0.075
- Zone 2 (far-field): σ_k2=1.0, σ_ω2=0.856, β2=0.0828
- Blending: F1=tanh(arg1⁴), F2=tanh(arg2²)
- Production limiter: Pk = γ_eff·min(μt·S², 10·β*·ρ·k·ω)
- Wall BC: k=0 (sublayer), ω=60ν/(β1·y1²) (sublayer)

### γ-Reθ Transitional Model (Langtry-Menter 2009)
- Transport: γ (intermittency) + Re_θ̃ (onset Re)
- F_onset from local Re_v and Re_θ_t correlation
- F_length from empirical Re_θ̃ table
- γ modulates SST production: Pk→γ·Pk

---

## Compilation

```bash
# gfortran
gfortran -O2 -o caffa caffa.f

# Intel ifort
ifort -O2 -o caffa caffa.f

# With OpenMP (future extension)
gfortran -O2 -fopenmp -o caffa caffa.f
```

---

## Unit Tests

### Fortuno (modern Fortran, CMake-integrated)
```bash
git clone https://github.com/fortuno-repos/fortuno
cd test && gfortran -I/path/to/fortuno test_caffa_fortuno.f90 -lfortuno -o test_fortuno
./test_fortuno
```

### pFUnit (NASA, parallel-capable)
```bash
git clone https://github.com/Goddard-Fortran-Ecosystem/pFUnit
cd test && gfortran -I/path/to/pfunit test_caffa_pfunit.f90 -lpfunit -o test_pfunit
./test_pfunit
```

### Ftnunit (lightweight, single-file)
```bash
cd test && gfortran test_caffa_ftnunit.f90 -o test_ftnunit
./test_ftnunit
```

### Tests Covered
| Test | Description |
|---|---|
| QUICK symmetry | Face value equals CDS on uniform mesh |
| linearUpwind linearity | Linear field reconstructed exactly |
| cellMDlimiter bounds | ψ ∈ [0,1], limited grad ≤ unlimited |
| GMRES convergence | Poisson system residual < tol |
| Mass conservation | Inlet = outlet flux to machine precision |
| SST F1 bounds | F1 ∈ [0,1], F1→1 near wall |
| gamma-Retheta | γ ∈ [0,1], Re_θ̃ > 0 |
| SIMPLEC vs SIMPLE | Same converged solution, faster SIMPLEC |
| PISO correctors | Tighter mass balance with more correctors |
| Wall BC k | k=0 at wall (sublayer) |
| Wall BC omega | ω = 60ν/(β1·y1²) in sublayer |

---

## References

1. Ferziger, Perić, Street — *Computational Methods for Fluid Dynamics*, Springer 2020
2. Menter (2003) — Two-equation eddy-viscosity turbulence models for engineering applications, AIAA-J
3. Langtry & Menter (2009) — Correlation-based transition modeling, J. Turbomachinery 131
4. Saad & Schultz (1986) — GMRES: A generalized minimal residual algorithm, SIAM J. Sci. Stat. Comp.
5. Vandoormaal & Raithby (1984) — Enhancements of the SIMPLE method, Num. Heat Transfer 7
6. Barth & Jespersen (1989) — Design and application of upwind schemes, AIAA-89-0366
7. Leonard (1979) — A stable and accurate convective modelling procedure, CMAME

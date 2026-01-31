import numpy as np

class CaffaCase:
    def __init__(self):
        # --- 1. General Control ---
        self.title = "Default CAFFA Simulation"
        self.logical_control = {
            'LREAD': False, 'LWRITE': True, 'LTEST': False, 
            'LOUTS': True, 'LOUTE': True, 'LTIME': False, 'KIN': 1
        }
        
        # --- 2. Monitoring & Numerics ---
        self.monitor = {'IMON': 5, 'JMON': 5, 'IPR': 1, 'JPR': 1}
        self.solver_params = {'NPCOR': 1, 'NIGRAD': 1, 'SORMAX': 1e-4, 'SLARGE': 1e20, 'ALFA': 0.7}
        
        # --- 3. Physics (Properties) ---
        self.physics = {
            'DENS': 1.0, 'VISC': 0.001, 'PRANL': 0.7,
            'GRAVX': 0.0, 'GRAVY': 0.0, 'BETA': 0.0,
            'TH': 300.0, 'TC': 300.0, 'TREF': 300.0
        }
        
        # --- 4. Initial Fields ---
        self.init_fields = {
            'UIN': 0.0, 'VIN': 0.0, 'PIN': 0.0, 
            'TIN': 300.0, 'TEIN': 0.001, 'EDIN': 0.001, 'ULID': 1.0
        }
        
        # --- 5. Time Control ---
        self.time_control = {
            'ITSTEP': 100, 'NOTT': 10, 'DT': 0.1, 'GAMT': 1.0
        }
        
        # --- 6. Equation Control (LCAL) ---
        # Indices in Fortran: IU=1, IV=2, IP=3, IEN=4, ITE=5, IED=6
        self.lcal = [True, True, True, False, False, False] 
        
        # --- 7. Under-Relaxation (URF) ---
        self.urf = [0.7, 0.7, 0.3, 0.9, 0.7, 0.7] # U, V, P, T, k, omega
        
        # --- 8. Linear Solver Settings (SOR, NSW) ---
        self.sor = [0.1] * 6
        self.nsw = [1, 1, 5, 1, 1, 1]
        
        # --- 9. Discretization Schemes (GDS) ---
        self.gds = [1.0] * 6 # 1.0 = CDS, 0.0 = UDS
        
        # Grid Levels (LSG)
        self.lsg = [10, 10, 10, 10] # Max iter per grid level

    def set_physics_model(self, model_type):
        """Configure LCAL flags based on model selection (Laminar vs k-omega)."""
        if model_type == "Laminar":
            self.lcal[4] = False # ITE (k)
            self.lcal[5] = False # IED (omega)
        elif model_type == "k-omega":
            self.lcal[4] = True
            self.lcal[5] = True
    
    def write_cin_file(self, filename):
        """Generates the .cin input file matching INIT subroutine in caffa.f"""
        with open(filename, 'w') as f:
            # 1. Title
            f.write(f"{self.title: <50}\n")
            
            # 2. Logicals
            logicals = [self.logical_control[k] for k in ['LREAD', 'LWRITE', 'LTEST', 'LOUTS', 'LOUTE', 'LTIME']]
            log_str = " ".join(["T" if x else "F" for x in logicals])
            f.write(f"{log_str} {self.logical_control['KIN']}\n")
            
            # 3. Indices
            f.write(f"{self.monitor['IMON']} {self.monitor['JMON']} {self.monitor['IPR']} {self.monitor['JPR']} {self.solver_params['NPCOR']} {self.solver_params['NIGRAD']}\n")
            
            # 4. Numerics
            f.write(f"{self.solver_params['SORMAX']} {self.solver_params['SLARGE']} {self.solver_params['ALFA']}\n")
            
            # 5. Density/Visc
            f.write(f"{self.physics['DENS']} {self.physics['VISC']} {self.physics['PRANL']}\n")
            
            # 6. Gravity/Temp
            f.write(f"{self.physics['GRAVX']} {self.physics['GRAVY']} {self.physics['BETA']} {self.physics['TH']} {self.physics['TC']} {self.physics['TREF']}\n")
            
            # 7. Initial Fields
            f.write(f"{self.init_fields['UIN']} {self.init_fields['VIN']} {self.init_fields['PIN']} {self.init_fields['TIN']} {self.init_fields['TEIN']} {self.init_fields['EDIN']} {self.init_fields['ULID']}\n")
            
            # 8. Time
            f.write(f"{self.time_control['ITSTEP']} {self.time_control['NOTT']} {self.time_control['DT']} {self.time_control['GAMT']}\n")
            
            # 9. LCAL
            lcal_str = " ".join(["T" if x else "F" for x in self.lcal])
            f.write(f"{lcal_str}\n")
            
            # 10. URF
            f.write(" ".join(map(str, self.urf)) + "\n")
            
            # 11. SOR
            f.write(" ".join(map(str, self.sor)) + "\n")
            
            # 12. NSW
            f.write(" ".join(map(str, self.nsw)) + "\n")
            
            # 13. GDS
            f.write(" ".join(map(str, self.gds)) + "\n")
            
            # 14. LSG (Just writing first 4 for demo)
            f.write(" ".join(map(str, self.lsg)) + "\n")

    def run_dummy_simulation(self):
        """Mock simulation for GUI visualization."""
        # Create a sample 2D grid solution
        ni, nj = 40, 20
        grid = np.zeros((ni, nj, 3))
        x = np.linspace(0, 2, ni)
        y = np.linspace(0, 1, nj)
        xx, yy = np.meshgrid(x, y, indexing='ij')
        
        # Simple lid-driven cavity like flow mock
        u = yy * self.init_fields['ULID'] 
        v = np.sin(np.pi * xx) * np.sin(np.pi * yy) * 0.1
        p = np.cos(np.pi * xx) * self.init_fields['DENS']
        
        return xx, yy, u, v, p
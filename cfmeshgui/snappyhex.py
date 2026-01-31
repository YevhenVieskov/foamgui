"""
Update the OpenFoamGUI class in main.py to use these new validators and the dictionary structure.

1. Update __init__ Data Structure: Replace the self.mesh_data in the GUI with a structure mirroring snappyHexMeshDict.
"""
# Internal Data Structure (snappyHexMeshDict style)
        self.mesh_data = {
            "Controls": {
                "castellatedMesh": True,
                "snap": True,
                "addLayers": False
            },
            "Geometry": {
                # In a real app, these would be populated dynamically
                "motorBike.obj": {"type": "triSurfaceMesh", "file": "motorBike.obj"}
            },
            "Castellated Controls": {
                "maxGlobalCells": 2000000,
                "minRefinementCells": 10,
                "locationInMesh": [3.0, 3.0, 0.43],
                "nCellsBetweenLevels": 3
            },
            "Snap Controls": {
                "nSmoothPatch": 3,
                "tolerance": 2.0,
                "nSolveIter": 30,
                "nRelaxIter": 5
            }
        }
		
#2. Update run_validation method: Connect the button to the new SnappyValidator.
def run_validation(self):
        # Construct the full config object for validation
        # We need to map the flat GUI structure back to the OpenFOAM nested structure
        full_config = {
            "controls": self.mesh_data["Controls"],
            "geometry": self.mesh_data["Geometry"],
            "castellatedMeshControls": {
                **self.mesh_data["Castellated Controls"],
                # Hardcoded for demo, normally from another GUI tab
                "features": [{"file": "motorBike.eMesh", "level": 6}],
                "refinementSurfaces": {"motorBike.obj": {"level": [5, 6]}}
            },
            "snapControls": self.mesh_data["Snap Controls"],
            "addLayersControls": {}
        }
        
        is_valid, errors = SnappyValidator.validate(full_config)
        
        if is_valid:
            QMessageBox.information(self, "Validation", "snappyHexMeshDict is Valid!")
            return full_config  # Return valid config for usage
        else:
            QMessageBox.warning(self, "Validation Failed", "\n".join(errors))
            return None

# 3. Update run_meshing method: This now writes the file and chains blockMesh -> snappyHexMesh.
def run_meshing(self):
        config = self.run_validation()
        if not config:
            return

        self.log_viewer.clear()
        
        # 1. Generate Dictionary
        try:
            SnappyGenerator.generate_file(config)
            self.log_viewer.append(">> system/snappyHexMeshDict generated successfully.")
        except Exception as e:
            self.log_viewer.append(f"<span style='color:red'>Error generating file: {str(e)}</span>")
            return

        # 2. Run OpenFOAM (Chained)
        # Note: We use a simple shell chain here. 
        # In production, use QProcess.finished signals to chain them cleanly.
        
        self.log_viewer.append(">> Starting blockMesh...")
        
        # Windows command for demo (mocking the calls)
        # Linux: cmd = "blockMesh && snappyHexMesh -overwrite"
        
        # MOCK COMMAND for visualization
        cmd = (
            "python -c \""
            "import time; "
            "print('Running blockMesh...'); time.sleep(1); "
            "print('blockMesh done.'); "
            "print('Running snappyHexMesh...'); "
            "print('Refining surfaces...'); time.sleep(1); "
            "print('Snapping to surface...'); time.sleep(1); "
            "print('Mesh generation complete.');\""
        )
        
        self.process.start(cmd)
		



import os

class SnappyValidator:
    """Validates specific snappyHexMesh rules."""
    
    @staticmethod
    def validate(config):
        errors = []
        
        # 1. Check Switches
        controls = config.get("controls", {})
        if not all(k in controls for k in ["castellatedMesh", "snap", "addLayers"]):
            errors.append("Missing main control switches (castellatedMesh, snap, addLayers).")

        # 2. Geometry Validation
        geometry = config.get("geometry", {})
        if not geometry:
            errors.append("Geometry dictionary cannot be empty.")
        for name, details in geometry.items():
            if "file" in details and not details["file"].endswith(".stl"):
                errors.append(f"Geometry '{name}': File must be an .stl")

        # 3. Refinement Levels (Min <= Max)
        castellated = config.get("castellatedMeshControls", {})
        features = castellated.get("features", [])
        for feat in features:
            if feat.get("level", 0) < 0:
                errors.append(f"Feature level cannot be negative.")

        surfaces = castellated.get("refinementSurfaces", {})
        for surf, params in surfaces.items():
            level = params.get("level", [0, 0])
            if isinstance(level, list) and len(level) == 2:
                if level[0] > level[1]:
                    errors.append(f"Surface '{surf}': Min level ({level[0]}) > Max level ({level[1]}).")
            else:
                errors.append(f"Surface '{surf}': Level must be [min, max].")

        # 4. Location in Mesh
        loc = castellated.get("locationInMesh", [])
        if len(loc) != 3:
            errors.append("locationInMesh must be a coordinate point [x, y, z].")

        return len(errors) == 0, errors

class SnappyGenerator:
    """Generates the OpenFOAM dictionary file."""
    
    @staticmethod
    def _dict_to_foam(data, indent=0):
        """Recursively converts Python dict to OpenFOAM syntax."""
        lines = []
        indent_str = "    " * indent
        
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"\n{indent_str}{key}")
                lines.append(f"{indent_str}{{")
                lines.extend(SnappyGenerator._dict_to_foam(value, indent + 1))
                lines.append(f"{indent_str}}}")
            elif isinstance(value, list):
                # Handle simplified list formatting for vectors/levels
                val_str = " ".join(map(str, value))
                lines.append(f"{indent_str}{key} ({val_str});")
            elif isinstance(value, bool):
                val_str = "on" if value else "off"
                lines.append(f"{indent_str}{key} {val_str};")
            else:
                lines.append(f"{indent_str}{key} {value};")
                
        return lines

    @staticmethod
    def generate_file(config, filepath="system/snappyHexMeshDict"):
        header = [
            "/*--------------------------------*- C++ -*----------------------------------*\\",
            "| =========                 |                                                 |",
            "| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |",
            "|  \\    /   O peration     | Version:  v2506                                 |",
            "|   \\  /    A nd           | Website:  www.openfoam.com                      |",
            "|    \\/     M anipulation  |                                                 |",
            "\\*---------------------------------------------------------------------------*/",
            "FoamFile",
            "{",
            "    version     2.0;",
            "    format      ascii;",
            "    class       dictionary;",
            "    object      snappyHexMeshDict;",
            "}",
            "// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //",
            ""
        ]
        
        body = SnappyGenerator._dict_to_foam(config)
        
        # Ensure system directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, "w") as f:
            f.write("\n".join(header))
            f.write("\n".join(body))
            f.write("\n\n// ************************************************************************* //")
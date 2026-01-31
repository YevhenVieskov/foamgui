import pytest
import os
import numpy as np
from caffa_io import CaffaIO

def test_readme_parsing(tmp_path):
    """Test automatic extraction of metadata from README."""
    readme_content = """
    ======================================================================
    CAFFA -- Computer-Aided Fluid Flow Analysis; Version 1.3, June 1997
    ======================================================================
    This version contains the k-omega turbulence model.
    Author: Milovan.Peric@t-online.de
    """
    f = tmp_path / "Readme"
    f.write_text(readme_content)
    
    io = CaffaIO()
    meta = io.parse_readme(str(f))
    
    assert meta["version"] == "1.3" [cite: 414]
    assert "k-omega Turbulence" in meta["models"] [cite: 414]
    assert "Milovan.Peric" in meta["author"] [cite: 191]

def test_dummy_mesh_generation():
    """Verify fallback mesh generation."""
    io = CaffaIO()
    grid = io.import_real_mesh("non_existent.grd")
    assert grid.n_points > 0
    assert grid.n_cells > 0

def test_binary_record_reader(tmp_path):
    """Writes a fake Fortran record and reads it back."""
    import struct
    f_path = tmp_path / "test.bin"
    
    # Create a Fortran record: [Length=4][Data=4][Length=4]
    # Writing integer 42
    with open(f_path, 'wb') as f:
        f.write(struct.pack('i', 4))  # Header
        f.write(struct.pack('i', 42)) # Data
        f.write(struct.pack('i', 4))  # Footer
        
    io = CaffaIO()
    with open(f_path, 'rb') as f:
        data = io.read_fortran_record(f)
        val = struct.unpack('i', data)[0]
        assert val == 42
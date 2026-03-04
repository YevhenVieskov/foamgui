"""
Unit Tests for CAFFA Parser
"""

import pytest
import tempfile
import os
from gui.caffa_parser import CAFFAParser

class TestCAFFAParser:
    """Test cases for CAFFAParser"""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance"""
        return CAFFAParser()
    
    @pytest.fixture
    def sample_output_file(self):
        """Create sample CAFFA output file"""
        content = """
        TITLE FOR THE PROBLEM SOLVED
        =====================================================
        
           FLUID DENSITY     : 1.225
           DYNAMIC VISCOSITY : 1.7894e-05
           CONVERGENCE CRIT. : 1.0000e-05
           SIP-PARAMETER     : 0.7
        
           K-OMEGA TURBULENCE MODEL WITH WALL FUNCTIONS
        
           UNDER-RELAXATION FOR U: 0.7000
           UNDER-RELAXATION FOR V: 0.7000
           UNDER-RELAXATION FOR P: 0.3000
        
        GRID  CYCLE  ITER    I------ABSOLUTE RESIDUAL SOURCE SUMS--------I    I------FIELD VALUES AT MONITORING LOCATION(  1,  1,  1)--I
                              UMOM      VMOM      MASS      ENER      KINE      DISE           U         V         P         T        TE        ED
          1    1     1    1.234E-03 1.234E-03 1.234E-03 1.234E-03 1.234E-03 1.234E-03    1.000E+00 0.000E+00 0.000E+00 3.000E+02 1.000E-03 1.000E-03
          1    1     2    5.678E-04 5.678E-04 5.678E-04 5.678E-04 5.678E-04 5.678E-04    1.000E+00 0.000E+00 0.000E+00 3.000E+02 1.000E-03 1.000E-03
          1    1     3    1.234E-04 1.234E-04 1.234E-04 1.234E-04 1.234E-04 1.234E-04    1.000E+00 0.000E+00 0.000E+00 3.000E+02 1.000E-03 1.000E-03
        
             *** CALCULATION FINISHED - SEE RESULTS ***
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.out', delete=False) as f:
            f.write(content)
            return f.name
    
    def test_parse_metadata(self, parser, sample_output_file):
        """Test metadata parsing"""
        data = parser.parse_output_file(sample_output_file)
        
        assert 'metadata' in data
        assert data['metadata']['density'] == 1.225
        assert data['metadata']['viscosity'] == 1.7894e-05
        assert data['metadata']['convergence_criterion'] == 1.0e-05
        assert data['metadata']['turbulence_model'] == 'k-omega'
    
    def test_parse_residuals(self, parser, sample_output_file):
        """Test residual parsing"""
        data = parser.parse_output_file(sample_output_file)
        
        assert 'residuals' in data
        assert len(data['residuals']) == 3
        assert data['residuals'][0]['iteration'] == 1
        assert data['residuals'][0]['u_momentum'] == 1.234e-03
    
    def test_parse_convergence(self, parser, sample_output_file):
        """Test convergence parsing"""
        data = parser.parse_output_file(sample_output_file)
        
        assert 'convergence_info' in data
        assert data['convergence_info']['converged'] == True
    
    def test_parse_nonexistent_file(self, parser):
        """Test parsing nonexistent file"""
        with pytest.raises(IOError):
            parser.parse_output_file('/nonexistent/file.out')
    
    def test_variable_names(self, parser):
        """Test variable names"""
        assert parser.variable_names['U'] == 'X-Velocity'
        assert parser.variable_names['V'] == 'Y-Velocity'
        assert parser.variable_names['P'] == 'Pressure'
    
    def teardown_method(self, method):
        """Cleanup after each test"""
        pass

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
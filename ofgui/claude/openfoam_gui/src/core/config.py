"""
Application configuration management
"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class AppConfig:
    """Application configuration manager"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._get_default_config_path()
        self.config = self._load_config()
        
    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        home = Path.home()
        config_dir = home / '.openfoam_gui'
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / 'config.json')
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        default_config = {
            'openfoam_path': '/opt/openfoam2506',
            'default_solver': 'simpleFoam',
            'mesh_quality_criteria': {
                'maxNonOrtho': 70,
                'maxBoundarySkewness': 20,
                'maxInternalSkewness': 4,
                'maxConcave': 80,
                'minVol': 1e-13,
                'minTetQuality': 1e-15,
                'minArea': -1,
                'minTwist': 0.05,
                'minDeterminant': 0.001,
                'minFaceWeight': 0.05,
                'minVolRatio': 0.01,
                'minTriangleTwist': -1
            },
            'recent_cases': [],
            'max_recent_cases': 10,
            'theme': 'dark',
            'auto_save': True,
            'auto_save_interval': 300,  # seconds
            'real_time_monitoring': True,
            'monitoring_interval': 1.0,  # seconds
            'plot_history_length': 1000
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                print(f"Error loading config: {e}")
        
        return default_config
    
    def save(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value
        self.save()
    
    def add_recent_case(self, case_path: str):
        """Add case to recent cases list"""
        recent = self.config.get('recent_cases', [])
        if case_path in recent:
            recent.remove(case_path)
        recent.insert(0, case_path)
        recent = recent[:self.config.get('max_recent_cases', 10)]
        self.set('recent_cases', recent)

"""Case tree widget for browsing OpenFOAM case structure"""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt
from pathlib import Path


class CaseTreeWidget(QTreeWidget):
    """Tree widget for displaying case structure"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderLabel("Case Structure")
        self.case_path = None
        
    def load_case(self, case_path: str):
        """Load case directory structure"""
        self.clear()
        self.case_path = Path(case_path)
        
        root = QTreeWidgetItem(self, [self.case_path.name])
        root.setExpanded(True)
        
        self._add_directory(root, self.case_path)
    
    def _add_directory(self, parent_item: QTreeWidgetItem, directory: Path):
        """Recursively add directory contents"""
        try:
            items = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name))
            for item in items:
                if item.name.startswith('.'):
                    continue
                    
                tree_item = QTreeWidgetItem(parent_item, [item.name])
                
                if item.is_dir():
                    tree_item.setExpanded(item.name in ['0', 'constant', 'system'])
                    if item.name not in ['processor0', 'processor1']:  # Skip processor dirs
                        self._add_directory(tree_item, item)
        except PermissionError:
            pass

from PySide6.QtWidgets import QWidget, QLayout, QVBoxLayout
from PySide6.QtWidgets import QHBoxLayout, QLabel
from PySide6.QtCore import Qt

class SummaryWidget(QWidget):
    def __init__(self, project_manager, button_text, checked_items=None):
        super().__init__()
        self.project_manager = project_manager
        if checked_items is None:
            checked_items = []
        
        
        self.layout = QVBoxLayout(self)

        # Title
        self.title = QLabel("Summary: ")
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)
        
        summarylayout = QHBoxLayout()
        summarylayout.setSpacing(10)  # space between items
        summarylayout.setContentsMargins(0, 0, 0, 0)


        
        print("handling summary",button_text.strip().lower() )
        if button_text.strip().lower() == "verify":
            for value in checked_items:
                slabel = QLabel()
                sicon = '✅'
                
                slabel.setText(f"{value}: {sicon}")
                slabel.setStyleSheet(
                    f"color: {'green'}; font-weight: bold;")
                summarylayout.addWidget(slabel)
        
        else:
            for key, value in self.project_manager.default_states.items():
                slabel = QLabel()
                sicon = '✅' if value else '❌'
                if button_text.strip().lower() == "generate documentation":
                    
                    if key == "Schematic_PDF" or  key == "PCB_PDF"  or  key == "Images"  or  key == "3D_file"  :
                        slabel.setText(f"{key}: {sicon}")
                        slabel.setStyleSheet(
                            f"color: {'green' if value else 'red'}; font-weight: bold;")
                        summarylayout.addWidget(slabel)
                        
                        
                elif button_text.strip().lower() == "generate production files":
                    
                    if key == "BOM" or  key == "Gerber"  or  key == "Placement"  or  key == "Drill"  :
                        slabel.setText(f"{key}: {sicon}")
                        slabel.setStyleSheet(
                            f"color: {'green' if value else 'red'}; font-weight: bold;")
                        summarylayout.addWidget(slabel)
                        
                    
                
        self.layout.addLayout(summarylayout)
        self.setLayout(self.layout)
import os
import sys
import datetime

from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QMainWindow, QFileDialog,
    QWidget, QCheckBox, QVBoxLayout, QLineEdit, QPushButton, QTreeWidget,
    QTreeWidgetItem, QLabel, QMessageBox, QGroupBox, QRadioButton
)
from PySide6.QtCore import Qt


class VerifyWidgetui(QWidget):
    def __init__(self, project_manager=None):
        super().__init__()
        self.project_manager = project_manager
        
        #styles sheet definitins for the project
        self.setStyleSheet("""
            mQWidget {
                font-family: Arial;
                font-size: 14px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #888;
                border-radius: 6px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        #all items stored in a vbox layout

        layout = QVBoxLayout(self) #main layout

        self.summaryWidget = QWidget()

        #create a small vertical box where checklist will be placed
        group_box = QGroupBox("Tick Verified Items")
        group_box.setStyleSheet("QGroupBox { font-weight: bold; }")
        
        self.checklistlayout = QVBoxLayout()
        
        #checkboxTitle = QLabel("Select Document Option")
        
        self.sch_reviewed_cb = QCheckBox("Schematic review checklist Completed")
        self.polarity_cb = QCheckBox("Ensure all Ics and Diodes have Pin/Polarity indicators")
        self.drc_cb = QCheckBox("Ensure no DRC present in the project")
        self.footprint_cb = QCheckBox("Confirm footprint selection for all components")
        self.documented_cb = QCheckBox("Ensure full documentation is generated")
        self.testpoint_cb = QCheckBox("Add Testpoints on power and communication lines")
        self.production_cb = QCheckBox("Regenerate all the Production Files")
        self.BOM_cb = QCheckBox("Populate all Bom Manufacturer Part #\n Ensure availability of componenets")
                
        # Add checkboxes to layout
        self.checklistlayout.addWidget(self.sch_reviewed_cb)
        self.checklistlayout.addWidget(self.polarity_cb)
        self.checklistlayout.addWidget(self.drc_cb)
        self.checklistlayout.addWidget(self.footprint_cb)
        self.checklistlayout.addWidget(self.documented_cb)
        self.checklistlayout.addWidget(self.testpoint_cb)
        self.checklistlayout.addWidget(self.production_cb)
        self.checklistlayout.addWidget(self.BOM_cb)
        
        group_box.setLayout(self.checklistlayout)
        
        
        # Project completed button
        self.generate_btn = QPushButton("Save") #save project state of verification
        self.generate_btn.clicked.connect(self.onProjectCompleted)


        layout.addWidget(group_box)
        layout.addSpacing(10)
        layout.addWidget( self.summaryWidget)
        layout.addSpacing(5)
        layout.addWidget(self.generate_btn, alignment=Qt.AlignCenter)
        
            
    def onProjectCompleted(self):
        checked_items = []
                        
        if self.sch_reviewed_cb.isChecked():
            checked_items.append("schematic")
            
            
        if self.polarity_cb.isChecked():
            checked_items.append("Polarities")
            

        if self.drc_cb.isChecked():
            #checked_items.append("images")
            checked_items.append("DRC check")
   
            
        if self.footprint_cb.isChecked():
            checked_items.append("Footprint selection")
            # Extract base name again if needed

        if self.documented_cb.isChecked():
            checked_items.append("Documentation")
            # Extract base name again if needed
 
        if self.testpoint_cb.isChecked():
            checked_items.append("TestPoints")
            # Extract base name again if needed
 
        if self.production_cb.isChecked():
            checked_items.append("Production Files")
            # Extract base name again if needed
        if self.BOM_cb.isChecked():
            checked_items.append("BOM Updated")
            # Extract base name again if needed
        
        self.project_manager.verification_checklist = checked_items
        
        summarylayout = QHBoxLayout()
        summarylayout.setSpacing(10)  # space between items
        summarylayout.setContentsMargins(0, 0, 0, 0)

        for value in checked_items:
            slabel = QLabel()
            sicon = '✅'
            
            slabel.setText(f"{value}: {sicon}")
            slabel.setStyleSheet(
                f"color: {'green'}; font-weight: bold;")
            summarylayout.addWidget(slabel)
        
        self.summaryWidget.setLayout(summarylayout)
        if len(checked_items) == 8:
            self.project_manager.default_states["Verified"] = True
            QMessageBox.information(
            self,
            "Project Completed",
            "All selected items have been verified and the project is marked as completed."
        )
       
        else:
            #self.project_manager.default_states["Verified"] = False
        
            print("Project Completed with items:", checked_items) 
        
        
        self.project_manager.project_progress_status.emit(self.project_manager.default_states)  
        
        

        

        #Generation of the documents
    # def handle_pcb_image_checkbox(self):
    #     img_dir = os.path.join(self.project_path, "DOCUMENTATION", "Images")
    #     os.makedirs(img_dir, exist_ok=True)

    #     os.makedirs(os.path.join(self.project_path, img_dir), exist_ok=True)

    #     QMessageBox.warning(
    #         self,
    #         "Notice",
    #         "You will have to generate the PNG image manually.\n"
    #         "Go to View → 3D Viewer, Export Image.\n"
    #         "I have made an 'Image' folder for you!"
    #     )

    #     self.pcb_img_cb.setChecked(False)

        
        


# Run for testing
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VerifyWidgetui()
    window.resize(400, 250)
    window.show()
    sys.exit(app.exec())
import os
import sys
import datetime

from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QMainWindow, QFileDialog,
    QWidget, QCheckBox, QVBoxLayout, QLineEdit, QPushButton, QTreeWidget,
    QTreeWidgetItem, QLabel, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt
from ProjectState import ProjectManager #statemanagement and synchronization.
from docgenerators import DocGeneratorKiCLI
from global_project_manager import project_manager

class DocumentationGenerationWidget(QWidget):
    def __init__(self, status_dot=None, status_label=None, project_name=None, project_path=None):
        super().__init__()
        self.project_name = project_name
        self.project_path = project_path
        self.dot = status_dot
        self.status_label = status_label
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

        #create a small vertical box where checklist will be placed
        group_box = QGroupBox("Select Export Options")
        checklistlayout = QVBoxLayout()
        
        #checkboxTitle = QLabel("Select Document Option")
        
        self.sch_pdf_cb = QCheckBox("Schematic PDF")
        self.pcb_pdf_cb = QCheckBox("PCB Layout PDF")
        self.pcb_img_cb = QCheckBox("PCB Images")
        
        
        # Add checkboxes to layout
        checklistlayout.addWidget(self.sch_pdf_cb)
        checklistlayout.addWidget(self.pcb_pdf_cb)
        checklistlayout.addWidget(self.pcb_img_cb)
        
        group_box.setLayout(checklistlayout)
        self.summary_label = QLabel(" We are going to generate....")
        self.summary_label.setAlignment(Qt.AlignCenter)
        # Generate button
        generate_btn = QPushButton("Generate")
        generate_btn.clicked.connect(self.generate_report)


        layout.addWidget(group_box)
        layout.addSpacing(10)
        layout.addWidget(self.summary_label)
        layout.addSpacing(5)
        layout.addWidget(generate_btn, alignment=Qt.AlignCenter)

    def generate_report(self):
        checked_items = []
        if self.sch_pdf_cb.isChecked():
            checked_items.append("schematic PDF")
            #call documet generation for sch_pdf from docgenerator.py
            gen = DocGeneratorKiCLI()
            gen.test_cli()
            #set the project_name.kicad_sch
            #TODO: IF GET_OS() == "WSL" or "Linux"
            #sets path to the schematic file
            self.myprojectsch_path = os.path.join(self.project_path, "SRC", self.project_name)
            # TODO: check if it is present
            #set path to the output directory
            self.sch_pdf_output_path = os.path.join(self.project_path, "DOCUMENTATION", "Schematic_pdf", "schematic.pdf")
            gen.generate_sch_pdf(schematic_path = self.project_path, output_pdf = self.sch_pdf_output_path)
        
        if self.pcb_pdf_cb.isChecked():
            checked_items.append("PCB PDF")
        if self.pcb_img_cb.isChecked():
            checked_items.append("images")

        if checked_items:
            summary = "Ready to generate: " + ", ".join(checked_items) + "."
        else:
            summary = "No options selected."

        self.summary_label.setText(summary)
        #Generation of the documents


        
        


# Run for testing
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DocumentationGenerationWidget()
    window.resize(400, 250)
    window.show()
    sys.exit(app.exec())
    
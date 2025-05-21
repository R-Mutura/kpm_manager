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
        print(self.project_name)
        print(self.project_path)
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
        self.pcb_step_cb = QCheckBox("PCB 3D-STEP")
        self.pcb_vrml_cb = QCheckBox("PCB 3D-VRML")
        
        self.pcb_img_cb.clicked.connect(self.handle_pcb_image_checkbox)
        
        #        
        
        # Add checkboxes to layout
        checklistlayout.addWidget(self.sch_pdf_cb)
        checklistlayout.addWidget(self.pcb_pdf_cb)
        checklistlayout.addWidget(self.pcb_img_cb)
        checklistlayout.addWidget(self.pcb_step_cb)
        checklistlayout.addWidget(self.pcb_vrml_cb)
        
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
        gen = DocGeneratorKiCLI()
        gen.test_cli()
        # 1. Locate the SRC folder
        src_path = None
        for root, dirs, _ in os.walk(self.project_path):
            if "SRC" in dirs:
                src_path = os.path.join(root, "SRC")
                break
        if not src_path:
            print("❌ SRC folder not found.")
            QMessageBox.critical(self, "Error", "❌ SRC folder not found.")
            return
        
        # 2. Recursively search for *.kicad_pro
        project_file = None
        for root, _, files in os.walk(src_path):
            for file in files:
                if file.endswith(".kicad_pro"):
                    project_file = os.path.join(root, file)
                    break
            if project_file:
                break

        if not project_file:
            print("❌ .kicad_pro file not found in SRC.")
            QMessageBox.critical(self, "Error", "❌ .kicad_pro file not found in SRC.")
            return

        if self.sch_pdf_cb.isChecked():
            checked_items.append("schematic PDF")
            #call documet generation for sch_pdf from docgenerator.py
            # 3. Extract base name and check for matching .kicad_sch
            base_name = os.path.splitext(os.path.basename(project_file))[0]
            sch_file_name = f"{base_name}.kicad_sch"
            sch_file_path = os.path.join(os.path.dirname(project_file), sch_file_name)

            if not os.path.exists(sch_file_path):
                print(f"❌ Matching schematic file '{sch_file_name}' not found.")
                QMessageBox.critical(self, "Error", f"❌ Matching schematic file '{sch_file_name}' not found.")
                return
            # 4. Set output path: <project_root>/DOCUMENTATION/Schematic_pdf/<projectname>_SCHPDF.pdf
            output_dir = os.path.join(self.project_path, "DOCUMENTATION", "Schematic_pdf")
            os.makedirs(output_dir, exist_ok=True)
            output_pdf_path = os.path.join(output_dir, f"{base_name}_SCHPDF.pdf")
            
            
            # 5. Call the generator
            try:
                gen.generate_sch_pdf(schematic_path=sch_file_path, output_pdf=output_pdf_path)
                QMessageBox.information(self, "Success", f"✅ PDF generated successfully:\n{output_pdf_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error Generating PDF", str(e))
                
                
        if self.pcb_pdf_cb.isChecked():
            checked_items.append("PCB PDF")
            # Extract base name again if needed
            base_name = os.path.splitext(os.path.basename(project_file))[0]
            pcb_file_name = f"{base_name}.kicad_pcb"
            pcb_file_path = os.path.join(os.path.dirname(project_file), pcb_file_name)
            
            if not os.path.exists(pcb_file_path):
                print(f"❌ Matching PCB file '{pcb_file_name}' not found.")
                QMessageBox.critical(self, "Error", f"❌ Matching PCB file '{pcb_file_name}' not found.")
                return

            # Output path for PCB PDF
            output_dir = os.path.join(self.project_path, "DOCUMENTATION", "PCB_pdf")
            os.makedirs(output_dir, exist_ok=True)
            output_pdf_path = os.path.join(output_dir, f"{base_name}_Top_PCBPDF.pdf")

            # Call the generator
            try:
                gen.generate_pcb_pdf_front(pcb_path=pcb_file_path, output_pdf=output_pdf_path)
                QMessageBox.information(self, "Success", f"✅ PCB PDF generated successfully:\n{output_pdf_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error Generating PCB PDF", str(e))
            
            output_pdf_path = os.path.join(output_dir, f"{base_name}_Bot_PCBPDF.pdf")

            # Call the generator
            try:
                gen.generate_pcb_pdf_bottom(pcb_path=pcb_file_path, output_pdf=output_pdf_path)
                QMessageBox.information(self, "Success", f"✅ PCB PDF generated successfully:\n{output_pdf_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error Generating PCB PDF", str(e))
 
            
            
        if self.pcb_img_cb.isChecked():
            #checked_items.append("images")
            QMessageBox.warning(self, "You will have to generate the PNG imaged manually\n Go to View → 3D Viewer, Export Image \n I have made an Image folder for you!")
            # Extract base name again if needed
        
        if self.pcb_step_cb.isChecked():
            #checked_items.append("images")
            checked_items.append("STEP FILE")
            # Extract base name again if needed
            base_name = os.path.splitext(os.path.basename(project_file))[0]
            pcb_file_name = f"{base_name}.kicad_pcb"
            pcb_file_path = os.path.join(os.path.dirname(project_file), pcb_file_name)
            
            if not os.path.exists(pcb_file_path):
                print(f"❌ Matching PCB file '{pcb_file_name}' not found.")
                QMessageBox.critical(self, "Error", f"❌ Matching PCB file '{pcb_file_name}' not found.")
                return

            # Output path for PCB PDF
            output_dir = os.path.join(self.project_path, "DOCUMENTATION", "Step")
            os.makedirs(output_dir, exist_ok=True)
            output_step_path = os.path.join(output_dir, f"{base_name}.step")

            try:
                gen.generate_step(pcb_path=pcb_file_path, output_step=output_step_path)
                QMessageBox.information(self, "Success", f"✅ 3D STEP generated successfully:\n{output_step_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error Generating 3D STEP", str(e))
                    
            
        if self.pcb_vrml_cb.isChecked():
            checked_items.append("3D VRML FILE")
            # Extract base name again if needed
            base_name = os.path.splitext(os.path.basename(project_file))[0]
            pcb_file_name = f"{base_name}.kicad_pcb"
            pcb_file_path = os.path.join(os.path.dirname(project_file), pcb_file_name)
            
            if not os.path.exists(pcb_file_path):
                print(f"❌ Matching PCB file '{pcb_file_name}' not found.")
                QMessageBox.critical(self, "Error", f"❌ Matching PCB file '{pcb_file_name}' not found.")
                return

            # Output path for PCB PDF
            output_dir = os.path.join(self.project_path, "DOCUMENTATION", "VRML")
            os.makedirs(output_dir, exist_ok=True)
            output_vrml_path = os.path.join(output_dir, f"{base_name}.wrl")

            try:
                gen.generate_vrml(pcb_path=pcb_file_path, output_vrml=output_vrml_path)
                QMessageBox.information(self, "Success", f"✅ 3D STEP generated successfully:\n{output_vrml_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error Generating 3D VRML", str(e))
            
        if checked_items:
            summary = "Ready to generate: " + ", ".join(checked_items) + "."
        else:
            summary = "No options selected."

        self.summary_label.setText(summary)
        #Generation of the documents
    def handle_pcb_image_checkbox(self):
        img_dir = os.path.join(self.project_path, "DOCUMENTATION", "Images")
        os.makedirs(img_dir, exist_ok=True)

        os.makedirs(os.path.join(self.project_path, img_dir), exist_ok=True)

        QMessageBox.warning(
            self,
            "Notice",
            "You will have to generate the PNG image manually.\n"
            "Go to View → 3D Viewer, Export Image.\n"
            "I have made an 'Image' folder for you!"
        )

        self.pcb_img_cb.setChecked(False)

        
        


# Run for testing
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DocumentationGenerationWidget()
    window.resize(400, 250)
    window.show()
    sys.exit(app.exec())
    
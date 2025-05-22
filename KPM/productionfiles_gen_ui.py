import os
import sys
import datetime

from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QMainWindow, QFileDialog,
    QWidget, QCheckBox, QVBoxLayout, QLineEdit, QPushButton, QTreeWidget,
    QTreeWidgetItem, QLabel, QMessageBox, QGroupBox, QRadioButton
)
from PySide6.QtCore import Qt
from productionFileGen import ProductionFilesGeneratorKICLI

#manage log levels easily
from ui_elements.loglevel_logic import CustomLogger
# Get the singleton instance
log_manager = CustomLogger()


class ProductionFilesGeneratorWidget(QWidget):
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
        group_box = QGroupBox("Select Production File Options:")
        self.checklistlayout = QVBoxLayout()
        
        #checkboxTitle = QLabel("Select Document Option")
        
        self.production_bom_cb = QCheckBox("Bill of Material (BOM)")
        self.production_gbr_cb = QCheckBox("Gerber Files")
        self.production_plc_cb = QCheckBox("Placement/Position Files (CSV)")
        self.production_drill_cb = QCheckBox("PCB drill file")
        self.production_stack_cb = QCheckBox("Stack`up Files")
        self.production_stack_cb.setVisible(False) #these are not functional yet
        self.production_dxf_cb = QCheckBox("PCB DXF")
        self.production_dxf_cb.setVisible(False)   #these are not functional yet
        
        
        
        
        # Add checkboxes to layout
        self.checklistlayout.addWidget(self.production_bom_cb)
        self.checklistlayout.addWidget(self.production_gbr_cb)
        self.checklistlayout.addWidget(self.production_plc_cb)
        self.checklistlayout.addWidget(self.production_drill_cb) #
        self.checklistlayout.addWidget(self.production_dxf_cb)
        self.checklistlayout.addWidget(self.production_stack_cb)  # 
        
        
        group_box.setLayout(self.checklistlayout)
        self.summary_label = QLabel(" Production Files Simmary: ")
        self.summary_label.setAlignment(Qt.AlignCenter)
        # Generate button
        generate_btn = QPushButton("Generate")
        generate_btn.clicked.connect(self.generate_production_report)


        layout.addWidget(group_box)
        layout.addSpacing(10)
        layout.addWidget(self.summary_label)
        layout.addSpacing(5)
        layout.addWidget(generate_btn, alignment=Qt.AlignCenter)
        
    
    def generate_production_report(self):
        checked_items = []
        genProduction = ProductionFilesGeneratorKICLI()
        genProduction.test_cli()
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

        if self.production_bom_cb.isChecked():
            checked_items.append("BOM(csv)") 
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
            output_dir = os.path.join(self.project_path, "Production_Files", "Bill_of_Materials")
            os.makedirs(output_dir, exist_ok=True)
            output_bom_path = os.path.join(output_dir, f"{base_name}_BOM.csv")
            
            
            # 5. Call the generator
            try:
                genProduction.generate_bom(sch_path=sch_file_path, output_dir=output_bom_path)
                if log_manager.get_log_level() == "High" or log_manager.get_log_level() == "Medium":
                    QMessageBox.information(self, "Success", f"✅ PDF generated successfully:\n{output_bom_path}")
            except Exception as e:
                if log_manager.get_log_level() == "High" or log_manager.get_log_level() == "Medium":
                    QMessageBox.critical(self, "Error Generating PDF", str(e))
                
                
        if self.production_gbr_cb.isChecked():
            checked_items.append("Gerber files")
            # Extract base name again if needed
            base_name = os.path.splitext(os.path.basename(project_file))[0]
            pcb_file_name = f"{base_name}.kicad_pcb"
            pcb_file_path = os.path.join(os.path.dirname(project_file), pcb_file_name)
            
            if not os.path.exists(pcb_file_path):
                print(f"❌ Matching PCB file '{pcb_file_name}' not found.")
                QMessageBox.critical(self, "Error", f"❌ Matching PCB file '{pcb_file_name}' not found.")
                return

            # Output path for PCB PDF
            output_dir = os.path.join(self.project_path, "Production_Files", "Gerber")
            os.makedirs(output_dir, exist_ok=True)
            output_gbr_path = output_dir

            # Call the generator
            try:
                genProduction.generate_gerber(pcb_path=pcb_file_path, output_dir=output_gbr_path)
                if log_manager.get_log_level() == "High" or log_manager.get_log_level() == "Medium":
                    QMessageBox.information(self, "Success", f"✅ PCB Gerber files generated successfully:\n{output_gbr_path}")
            except Exception as e:
                if log_manager.get_log_level() == "High" or log_manager.get_log_level() == "Medium":
                    QMessageBox.critical(self, "Error Generating Gerber Files", str(e))
            
            
        if self.production_plc_cb.isChecked():
            checked_items.append("Position Placement Files")
            # Extract base name again if needed
            base_name = os.path.splitext(os.path.basename(project_file))[0]
            pcb_file_name = f"{base_name}.kicad_pcb"
            mypcb_file_path = os.path.join(os.path.dirname(project_file), pcb_file_name)
            
            if not os.path.exists(mypcb_file_path):
                print(f"❌ Matching PCB file '{pcb_file_name}' not found.")
                QMessageBox.critical(self, "Error", f"❌ Matching PCB file '{pcb_file_name}' not found.")
                return
        
            # Output path for PCB PDF
            output_dir = os.path.join(self.project_path, "Production_Files", "Placement_Files")
            os.makedirs(output_dir, exist_ok=True)
            output_plc_path = os.path.join(output_dir, f"{base_name}_cpl.csv")

            # Call the generator
            try:
                genProduction.generate_placement(pcb_path=mypcb_file_path, output_dir=output_plc_path)
                if log_manager.get_log_level() == "High" or log_manager.get_log_level() == "Medium":
                    QMessageBox.information(self, "Success", f"✅ Placement files generated successfully:\n{output_plc_path}")
            except Exception as e:
                if log_manager.get_log_level() == "High" or log_manager.get_log_level() == "Medium":
                    QMessageBox.critical(self, "Error Generating Placement Files", str(e))
            
            
        if self.production_drill_cb.isChecked():
            #checked_items.append("images")
            checked_items.append("Drill files")
            # Extract base name again if needed
            base_name = os.path.splitext(os.path.basename(project_file))[0]
            pcb_file_name = f"{base_name}.kicad_pcb"
            pcb_file_path = os.path.join(os.path.dirname(project_file), pcb_file_name)
            
            if not os.path.exists(pcb_file_path):
                print(f"❌ Matching PCB file '{pcb_file_name}' not found.")
                QMessageBox.critical(self, "Error", f"❌ Matching PCB file '{pcb_file_name}' not found.")
                return

            # Output path for PCB PDF
            output_dir = os.path.join(self.project_path, "Production_Files", "Drill")
            os.makedirs(output_dir, exist_ok=True)
            #output_step_path = os.path.join(output_dir, f"{base_name}.step")
            output_drill_path = output_dir

            try:
                genProduction.generate_drill(pcb_path=pcb_file_path, output_dir=output_drill_path)
                if log_manager.get_log_level() == "High" or log_manager.get_log_level() == "Medium":
                    geBox.information(self, "Success", f"✅ Drill files generated successfully:\n{output_drill_path}")
            except Exception as e:
                if log_manager.get_log_level() == "High" or log_manager.get_log_level() == "Medium":
                    QMessageBox.critical(self, "Error Generating Drill Files", str(e))
                    
            
        if self.production_dxf_cb.isChecked():
            checked_items.append("DXF Files")
            # Extract base name again if needed
            base_name = os.path.splitext(os.path.basename(project_file))[0]
            pcb_file_name = f"{base_name}.kicad_pcb"
            pcb_file_path = os.path.join(os.path.dirname(project_file), pcb_file_name)
            
            if not os.path.exists(pcb_file_path):
                print(f"❌ Matching PCB file '{pcb_file_name}' not found.")
                QMessageBox.critical(self, "Error", f"❌ Matching PCB file '{pcb_file_name}' not found.")
                return

            # Output path for PCB PDF
            output_dir = os.path.join(self.project_path, "Production_Files", "VRML")
            os.makedirs(output_dir, exist_ok=True)
            output_dxf_path = os.path.join(output_dir, f"{base_name}.dxf")

            try:
                genProduction.generate_dxf(pcb_path=pcb_file_path, output_dir=output_dxf_path)
                if log_manager.get_log_level() == "High" or log_manager.get_log_level() == "Medium":
                    QMessageBox.information(self, "Success", f"✅ DXF File generated successfully:\n{output_dxf_path}")
            except Exception as e:
                if log_manager.get_log_level() == "High" or log_manager.get_log_level() == "Medium":
                    QMessageBox.critical(self, "Error Generating DXF File ", str(e))
            
        if checked_items:
            summary = "Ready to generate: " + ", ".join(checked_items) + "."
        else:
            summary = "No options selected."

        self.summary_label.setText(summary)
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
    window = ProductionFilesGenerator()
    window.resize(400, 250)
    window.show()
    sys.exit(app.exec())
    
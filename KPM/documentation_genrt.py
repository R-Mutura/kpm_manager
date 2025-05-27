import os
import sys
import datetime

from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QMainWindow, QFileDialog,
    QWidget, QCheckBox, QVBoxLayout, QLineEdit, QPushButton, QTreeWidget,
    QTreeWidgetItem, QLabel, QMessageBox, QGroupBox, QRadioButton
)
from PySide6.QtCore import Qt


#from ProjectState import ProjectManager #statemanagement and synchronization.
from docgenerators import DocGeneratorKiCLI
from global_project_manager import project_manager
from ui_elements.loglevel_logic import CustomLogger
# Get the singleton instance
log_manager = CustomLogger()


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

        self.summaryWidget = QWidget()

        #create a small vertical box where checklist will be placed
        group_box = QGroupBox("Select Export Options")
        self.checklistlayout = QVBoxLayout()
        
        #checkboxTitle = QLabel("Select Document Option")
        
        self.sch_pdf_cb = QCheckBox("Schematic PDF")
        self.pcb_pdf_cb = QCheckBox("PCB Layout PDF")
        self.pcb_img_cb = QCheckBox("PCB Images")
        self.pcb_step_cb = QCheckBox("PCB 3D-STEP")
        self.pcb_vrml_cb = QCheckBox("PCB 3D-VRML")
        
        #radio buttons for image format
        self.pcb_img_cb.stateChanged.connect(self.toggle_image_format_options)
        # --- Image Format Selection ---
        self.image_format_box = QGroupBox("Select Image Format")
        image_format_layout = QHBoxLayout()
        #        
        self.radio_png = QRadioButton("PNG")
        self.radio_jpg = QRadioButton("JPG")
        self.radio_png.setChecked(True)  # Default
        image_format_layout.addWidget(self.radio_png)
        image_format_layout.addWidget(self.radio_jpg)

        self.image_format_box.setLayout(image_format_layout)
        self.image_format_box.setVisible(False)  # 👈 Start hidden
        #end of radio button
        
        # --- Image Orientation Selection ---
        self.image_orientation_cb_box = QGroupBox("Select Image Orientation")
        image_orientation_layout = QVBoxLayout()
        
        self.img_orientation_top = QCheckBox("Top")
        self.img_orientation_bot = QCheckBox("Bottom")
        self.img_orientation_iso_top = QCheckBox("Isometric_Top")
        self.img_orientation_iso_bot = QCheckBox("Isometric_Bottom")
        
        #set top and bottom as default to be automatically checked
        self.img_orientation_top.setChecked(True)
        self.img_orientation_bot.setChecked(True)  # Default
        
        image_orientation_layout.addWidget(self.img_orientation_top)
        image_orientation_layout.addWidget(self.img_orientation_bot)
        image_orientation_layout.addWidget(self.img_orientation_iso_top)
        image_orientation_layout.addWidget(self.img_orientation_iso_bot)
        
        #add the image orientation layout to the group box
        self.image_orientation_cb_box.setLayout(image_orientation_layout)
        #set the image orientation layout to be hidden
        self.image_orientation_cb_box.setVisible(False)  # 👈 Start hidden
        
        #end of image orientation
        # Add checkboxes to layout
        self.checklistlayout.addWidget(self.sch_pdf_cb)
        self.checklistlayout.addWidget(self.pcb_pdf_cb)
        self.checklistlayout.addWidget(self.pcb_img_cb)
        self.checklistlayout.addWidget(self.image_format_box)  # 👈 Add below image checkbox
        self.checklistlayout.addWidget(self.image_orientation_cb_box) # 👈 Add below image orientation selection 
        self.checklistlayout.addWidget(self.pcb_step_cb)
        self.checklistlayout.addWidget(self.pcb_vrml_cb)
        
        group_box.setLayout(self.checklistlayout)
        self.summary_label = QLabel(" We are going to generate....")
        self.summary_label.setAlignment(Qt.AlignCenter)
        # Generate button
        generate_btn = QPushButton("Generate")
        generate_btn.clicked.connect(self.generate_report)


        layout.addWidget(group_box)
        layout.addSpacing(10)
        layout.addWidget( self.summaryWidget)
        layout.addSpacing(5)
        layout.addWidget(generate_btn, alignment=Qt.AlignCenter)
        
    
    def on_successful_generation(self, name: str, state: bool):
        # Update internal state
        if name in project_manager.default_states:
            project_manager.default_states[name] = state
        else:
            print(f"Warning: '{name}' not in default_states")
        

    def toggle_image_format_options(self, state):
        self.image_format_box.setVisible(bool(state))
        self.image_orientation_cb_box.setVisible(bool(state))
        #self.image_format_box.setVisible(True)
        self.image_format_box.updateGeometry()
        self.image_format_box.repaint()
        self.checklistlayout.activate() #
        #self.image_format_box.updateGeometry()
    
    def generate_report(self):
        checked_items = []
        gen = DocGeneratorKiCLI(KICAD_CLI=project_manager.kicad_cli, project_name = project_manager.get_project_name(), project_path=project_manager.get_project_path())
        
        #gen.test_cli()
        print("here are the project_mager_intems",project_manager.kicad_cli, project_manager.get_project_name(), project_manager.get_project_path())
        print("here are the project_mager_items 2",self.project_name, self.project_path)
        print("dicts", project_manager.default_states)
        print("**here are the project_mager_intems 3:",project_manager.kicad_cli, project_manager.get_project_name(), project_manager.get_project_path())
       
        
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
                
                if log_manager.get_log_level() == "High" or log_manager.get_log_level() == "Medium":
                    QMessageBox.information(self, "Success", f"✅ PDF generated successfully:\n{output_pdf_path}")
                self.on_successful_generation(name="Schematic_PDF", state=True)
            except Exception as e:
                if log_manager.get_log_level() == "High" or log_manager.get_log_level() == "Medium":
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
                if log_manager.get_log_level() == "High" or log_manager.get_log_level() == "Medium":
                    QMessageBox.information(self, "Success", f"✅ PCB PDF generated successfully:\n{output_pdf_path}")
                self.on_successful_generation(name="PCB_PDF", state=True)
            except Exception as e:
                if log_manager.get_log_level() == "High" or log_manager.get_log_level() == "Medium":
                    QMessageBox.critical(self, "Error Generating PCB PDF", str(e))
            
            output_pdf_path = os.path.join(output_dir, f"{base_name}_Bot_PCBPDF.pdf")

            # Call the generator
            try:
                gen.generate_pcb_pdf_bottom(pcb_path=pcb_file_path, output_pdf=output_pdf_path)
                if log_manager.get_log_level() == "High" or log_manager.get_log_level() == "Medium":
                    QMessageBox.information(self, "Success", f"✅ PCB PDF generated successfully:\n{output_pdf_path}")
            except Exception as e:
                if log_manager.get_log_level() == "High" or log_manager.get_log_level() == "Medium":
                    QMessageBox.critical(self, "Error Generating PCB PDF", str(e))
 
            
            
        if self.pcb_img_cb.isChecked():
            checked_items.append("images")
            # Extract base name again if needed
            base_name = os.path.splitext(os.path.basename(project_file))[0]
            pcb_file_name = f"{base_name}.kicad_pcb"
            mypcb_file_path = os.path.join(os.path.dirname(project_file), pcb_file_name)
            
            if not os.path.exists(mypcb_file_path):
                print(f"❌ Matching PCB file '{pcb_file_name}' not found.")
                QMessageBox.critical(self, "Error", f"❌ Matching PCB file '{pcb_file_name}' not found.")
                return
            
            # Choose image format
            image_format = "png" if self.radio_png.isChecked() else "jpg"
            
            # Output path for PCB image
            output_dir = os.path.join(self.project_path, "DOCUMENTATION", "Images")
            os.makedirs(output_dir, exist_ok=True)
            # Orientation checkboxes and their labels
            orientations = {
                self.img_orientation_top: "Top",
                self.img_orientation_bot: "Bottom",
                self.img_orientation_iso_top: "IsoTop",
                self.img_orientation_iso_bot: "IsoBottom"
            }
            for checkbox, orientation in orientations.items():
                if checkbox.isChecked():
                    output_image_path = os.path.join(output_dir, f"{base_name}_{orientation}.{image_format}")
                    try:
                        gen.generate_pcb_render(
                            pcb_path=mypcb_file_path,
                            orientation=orientation,
                            output_img=output_image_path
                        )
                        print(f"✅ Image generated: {output_image_path}")
                        if log_manager.get_log_level() == "High" or log_manager.get_log_level() == "Medium":
                            QMessageBox.information(self, "Success", f"✅ Image generated: {output_image_path}")
                        self.on_successful_generation(name="Images", state=True)
                    except Exception as e:
                        if log_manager.get_log_level() == "High" or log_manager.get_log_level() == "Medium":
                            QMessageBox.critical(self, "Error Generating Image", str(e))
            # output_images_path = os.path.join(output_dir, f"{base_name}_top.{image_format}")
            # # Call the generator
            # #output_images_path = os.path.join(output_dir, f"{base_name}_{orientation}.{image_format}")
           
            # try:
            #     gen.generate_pcb_render(pcb_path=mypcb_file_path, output_img=output_images_path)
            #     QMessageBox.information(self, "Success", f"✅ Images generated successfully:\n{output_images_path}")
            # except Exception as e:
            #     QMessageBox.critical(self, "Error Generating 3D images", str(e))
        
        
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
                if log_manager.get_log_level() == "High" or log_manager.get_log_level() == "Medium":
                    QMessageBox.information(self, "Success", f"✅ 3D STEP generated successfully:\n{output_step_path}")
                self.on_successful_generation(name="3D_file", state=True)
            except Exception as e:
                if log_manager.get_log_level() == "High" or log_manager.get_log_level() == "Medium":
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
                if log_manager.get_log_level() == "High" or log_manager.get_log_level() == "Medium":
                    QMessageBox.information(self, "Success", f"✅ 3D STEP generated successfully:\n{output_vrml_path}")
                self.on_successful_generation(name="3D_file", state=True)
            except Exception as e:
                if log_manager.get_log_level() == "High" or log_manager.get_log_level() == "Medium":
                    QMessageBox.critical(self, "Error Generating 3D VRML", str(e))
        #
        # if checked_items:
        #     summary = "Updated Summary " + ", ".join(checked_items) + "."
        # else:
        #     summary = "No options selected."

        # self.summary_label.setText(summary)
        #geenration summary
        
        summarylayout = QHBoxLayout()
        summarylayout.setSpacing(10)  # space between items
        summarylayout.setContentsMargins(0, 0, 0, 0)

        for key, value in project_manager.default_states.items():
            slabel = QLabel()
            sicon = '✅' if value else '❌'
            if key == "Schematic_PDF" or  key == "PCB_PDF"  or  key == "Images"  or  key == "3D_file"  :
                slabel.setText(f"{key}: {sicon}")
                slabel.setStyleSheet(
                    f"color: {'green' if value else 'red'}; font-weight: bold;")
                summarylayout.addWidget(slabel)
        
        self.summaryWidget.setLayout(summarylayout)
        #layout.addWidget( self.summaryWidget)

        project_manager.update_document_tree.emit()#update the project tree
        project_manager.project_progress_status.emit(project_manager.default_states)

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
    window = DocumentationGenerationWidget()
    window.resize(400, 250)
    window.show()
    sys.exit(app.exec())
    
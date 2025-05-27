from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton,
    QFileDialog, QLineEdit, QHBoxLayout, QApplication, QGroupBox,
    QMessageBox
)
import sys
import os
from PySide6.QtCore import Qt


class SettingsWidget(QWidget):
    def __init__(self, project_manager=None, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager #will be used to set project settings later
        self.setWindowTitle("KiCad Project Manager Settings")
        print("the cli path is:", self.project_manager)
        self.layout = QVBoxLayout(self)

        # KiCad Installation Directory
        self.kicad_bin_path_toggle  = QPushButton("KiCad Installation Directory ▸")
        self.kicad_bin_path_toggle.setCheckable(True)
        self.kicad_bin_path_toggle.setChecked(False)
        self.kicad_bin_path_toggle.clicked.connect(self.toggle_kicad_path_group)
        self.layout.addWidget(self.kicad_bin_path_toggle)
        
        # Group box (initially hidden)
        self.kicad_path_group = QGroupBox()
        self.kicad_path_group.setVisible(False)
        self.kicad_path_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 6px;
                margin-top: 6px;
                padding: 10px;
            }
        """)
        
        path_v_alyout = QVBoxLayout()
        group_layout = QHBoxLayout()
        
        
        self.kicad_bin_path_edit = QLineEdit()
        self.kicad_bin_path_button = QPushButton("Browse KiCad Path")
        self.kicad_bin_path_button.clicked.connect(self.select_kicad_bin_path)
        self.kicad_bin_path_edit.setPlaceholderText(r"C:\Program Files\KiCad\<version>\bin")
        self.kicad_bin_path_edit.setToolTip("Path to the KiCad installation directory, e.g., C:\\Program Files\\KiCad\\9.0\\bin")
        self.select_kicad_path_button = QPushButton("Select")
        self.select_kicad_path_button.setFixedWidth(200)
        self.select_kicad_path_button.clicked.connect(self.onSet_kicad_bin_path)
        current_ki_cad_path = self.project_manager.get_kicad_cli()
        if current_ki_cad_path:
            self.kicad_bin_path_edit.setText(f"Current Kicad Dir: {current_ki_cad_path}")
        
        group_layout.addWidget(self.kicad_bin_path_edit)
        group_layout.addWidget(self.kicad_bin_path_button, alignment=Qt.AlignCenter)
        path_v_alyout.addLayout(group_layout)
        path_v_alyout.addWidget(self.select_kicad_path_button)
        #group_layout.addWidget(self.select_kicad_path_button)
        self.kicad_path_group.setLayout(path_v_alyout)
        
        self.layout.addWidget(self.kicad_path_group)
        
        # Library Directory

        # Stub Buttons (just show placeholder messages)
        stub_buttons = {
            "library": self.stub_function,
            "Page Layout": self.stub_function,
            "Net Settings": self.stub_function,
            "Design Rules": self.stub_function,
            "Simulation Config": self.stub_function,
            "Project Metadata": self.stub_function,
        }

        for label, func in stub_buttons.items():
            btn = QPushButton(label)
            btn.clicked.connect(func)
            self.layout.addWidget(btn)

        # Optional: Add spacing at the bottom
        self.layout.addStretch()
    
    def toggle_kicad_path_group(self):
        visible = self.kicad_bin_path_toggle.isChecked()
        self.kicad_path_group.setVisible(visible)
        # Update arrow direction
        if visible:
            self.kicad_bin_path_toggle.setText("KiCad Installation Directory ▼")
        else:
            self.kicad_bin_path_toggle.setText("KiCad Installation Directory ▸")

    def select_kicad_bin_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select KiCad Installation Directory")
        if path:
            self.kicad_bin_path_edit.setText(path)

    def _labeled_path_field(self, label_text, line_edit, button):
        layout = QVBoxLayout()
        label = QLabel(label_text)
        h_layout = QHBoxLayout()
        h_layout.addWidget(line_edit)
        h_layout.addWidget(button)
        layout.addWidget(label)
        layout.addLayout(h_layout)
        return layout

    def select_kicad_bin_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select KiCad Installation Directory")
        if path:
            self.kicad_bin_path_edit.setText(path)

    def onSet_kicad_bin_path(self):
        mypath = self.kicad_bin_path_edit.text().strip()
        if not mypath:
            print("No KiCad path provided.")
            QMessageBox.critical(self, "Error", "Please provide a valid KiCad installation path.")
            return
        
        #check if path is valid and contains kicad-cli.exe
        mypath = os.path.normpath(mypath)
        if not os.path.isdir(mypath):
            QMessageBox.critical(self, "Error", f"The path does not exist:\n{mypath}")
            return
        
        cli_exe = os.path.join(mypath, "kicad-cli.exe")
        
        
        if not os.path.isfile(cli_exe):
            QMessageBox.critical(self, "Error", f"'kicad-cli.exe' not found in the selected path:\n{mypath}")
            return
        if not os.access(cli_exe, os.X_OK):
            QMessageBox.critical(self, "Error", f"'kicad-cli.exe' is not executable:\n{cli_exe}")
            return
        
        bom_scripting_py = os.path.join(mypath, "scripting", "plugins", "bom_csv_grouped_by_value.py")
        if not os.path.isfile(bom_scripting_py):
            QMessageBox.critical(self, "Error", f"'bom_csv_grouped_by_value.py' not found in the scripting plugins directory:\n{os.path.join(mypath, 'scripting', 'plugins')}")
            return
        
        if not os.access(bom_scripting_py, os.R_OK):
            QMessageBox.critical(self, "Error", f"'bom_csv_grouped_by_value.py' is not readable:\n{bom_scripting_py}")
            return
        # If all checks pass
        QMessageBox.information(self, "Success", f"Valid KiCad path set:\n{cli_exe} \nand BOM script:\n{bom_scripting_py}")
        # Here you can store the path in your project manager or settings   
        if self.project_manager:
            #self.project_manager.set_kicad_cli(cli_exe, bom_scripting_py)
            
            pass #self.project_manager.save_kicad_paths_signal.emit(cli_exe, bom_scripting_py)#nothing connects to it as of now
        else:
            print(", storing path locally.")
            
            
        self.kicad_cli_path = cli_exe  # store it if needed
        print("KiCad CLI set to:", self.kicad_cli_path)
        self.kicad_bin_path_edit.setText(f"Current Kicad Dir: {self.kicad_cli_path}")
    
    
    def stub_function(self):
        sender = self.sender()
        label = sender.text()
        print(f"{label}: Functionality to be added later.")

    def stylesheet(self):
        return """
        QWidget {
            background-color: #f7f7f7;
            font-family: 'Segoe UI', sans-serif;
            font-size: 11pt;
        }
        QPushButton {
            background-color: #3498db;
            color: white;
            padding: 6px 12px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        QLineEdit {
            padding: 6px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        """
        
# Standalone testing
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SettingsWidget()
    win.resize(500, 300)
    win.show()
    sys.exit(app.exec())

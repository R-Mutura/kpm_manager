import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QFileDialog, QVBoxLayout, QDialog, QHBoxLayout
)
from PySide6.QtCore import QSettings


class PathSelectorPopup(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Kicad-cli.exe Path")
        
        self.resize(400, 150)

        self.selected_path =""
        # Create layout and widgets
        self.label = QLabel("No path selected", self)
        self.select_button = QPushButton("Browse...", self)
        self.save_button = QPushButton("Save")
        self.cancel_button = QPushButton("Cancel")

        self.select_button.clicked.connect(self.browse_path)
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        # Layout
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_button)
        btn_layout.addWidget(self.cancel_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.addWidget(self.select_button)
        layout.addLayout(btn_layout)


        # Load saved path
        # self.settings = QSettings("MyCompany", "MyApp")
        # saved_path = self.settings.value("executable_path", "")
        # if saved_path:
        #     self.label.setText(f"Saved path: {saved_path}")

        
    def browse_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "KiCAD-CLI.exe File Executable")
        if path:
            self.selected_path = path
            self.label.setText(f"Saved path: {self.selected_path}")
            
            #self.label.setText(f"Selected: {path}")
            #self.settings.setValue("executable_path", path)
    def get_selected_path(self):
        return self.selected_path


if __name__ == "__main__":
    app = QApplication(sys.argv)
    popup = PathSelectorPopup()
    popup.show()
    sys.exit(app.exec())
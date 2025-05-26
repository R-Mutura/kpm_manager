from PySide6.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton,
    QFileDialog, QLineEdit, QHBoxLayout, QApplication
)
import sys

class SettingsWidget(QWidget):
    def __init__(self, project_manager=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("KiCad Project Settings")
        self.layout = QVBoxLayout(self)

        # KiCad Installation Directory
        self.kicad_bin_path_edit = QLineEdit()
        self.kicad_bin_path_button = QPushButton("Select KiCad Installation Directory")
        self.kicad_bin_path_button.clicked.connect(self.select_kicad_bin_path)

        self.layout.addLayout(self._labeled_path_field("KiCad Installation Directory", self.kicad_bin_path_edit, self.kicad_bin_path_button))

        # Library Directory
        self.library_path_edit = QLineEdit()
        self.library_path_button = QPushButton("Select Library Path")
        self.library_path_button.clicked.connect(self.select_library_path)

        self.layout.addLayout(self._labeled_path_field("Library Path", self.library_path_edit, self.library_path_button))

        # Stub Buttons (just show placeholder messages)
        stub_buttons = {
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

    def select_library_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select KiCad Library Directory")
        if path:
            self.library_path_edit.setText(path)

    def stub_function(self):
        sender = self.sender()
        label = sender.text()
        print(f"{label}: Functionality to be added later.")

# Standalone testing
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SettingsWidget()
    win.resize(500, 300)
    win.show()
    sys.exit(app.exec())

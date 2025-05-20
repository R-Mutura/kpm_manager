import sys
import os
from qtpy.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel, QFileDialog, QMessageBox
)

class FolderCreator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Folder Creator")
        self.resize(400, 100)

        # Layouts
        layout = QVBoxLayout()
        input_layout = QHBoxLayout()

        # Folder path input
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Enter folder path...")

        # Browse button
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_folder)

        # Add to layout
        input_layout.addWidget(QLabel("Folder:"))
        input_layout.addWidget(self.path_input)
        input_layout.addWidget(browse_btn)

        # Create button
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_folder)

        # Assemble full layout
        layout.addLayout(input_layout)
        layout.addWidget(create_btn)
        self.setLayout(layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.path_input.setText(folder)

    def create_folder(self):
        path = self.path_input.text().strip()
        if not path:
            QMessageBox.warning(self, "Warning", "Please enter or select a folder path.")
            return

        try:
            if not os.path.exists(path):
                os.makedirs(path)
                QMessageBox.information(self, "Success", f"Folder created:\n{path}")
            else:
                QMessageBox.information(self, "Info", f"Folder already exists:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create folder:\n{str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = FolderCreator()
    win.show()
    sys.exit(app.exec_())


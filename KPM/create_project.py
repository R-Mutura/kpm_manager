import os
import sys
import datetime

from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QMainWindow, QFileDialog,
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QTreeWidget,
    QTreeWidgetItem, QLabel, QMessageBox
)

from PySide6.QtCore import Qt
# from ProjectState import project_manager #statemanagement and synchronization.
from global_project_manager import project_manager

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QTreeWidget,
    QTreeWidgetItem, QLabel, QMessageBox
)
from PySide6.QtCore import Qt


class CreateProjectWidget(QWidget):
    def __init__(self, status_dot=None, status_label=None):
        super().__init__()
        self.dot = status_dot
        self.status_label = status_label

        layout = QVBoxLayout(self)

        # Project folder path with Browse button
        folder_layout = QHBoxLayout()
        self.folder_edit = QLineEdit()
        self.folder_edit.setPlaceholderText("Select base folder path")
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_folder)
        folder_layout.addWidget(self.folder_edit)
        folder_layout.addWidget(browse_btn)

        # Project name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter project name")

        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.on_create)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)

        layout.addWidget(QLabel("Project Folder:"))
        layout.addLayout(folder_layout)
        layout.addWidget(QLabel("Project Name:"))
        layout.addWidget(self.name_edit)
        layout.addWidget(create_btn)
        layout.addWidget(QLabel("Project Structure Preview:"))
        layout.addWidget(self.tree)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Project Base Folder")
        if folder:
            self.folder_edit.setText(folder)
            

    def on_create(self):
        base = self.folder_edit.text().strip()
        name = self.name_edit.text().strip()
        if not base or not name:
            QMessageBox.critical(self, "Error", "Provide project name and a valid Project Folder.")
            return

        root_path = os.path.join(base, name)
        try:
            os.makedirs(root_path, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not create root folder:\n{e}")
            return

        try:
            existing_dirs = {
                d.lower() for d in os.listdir(root_path)
                if os.path.isdir(os.path.join(root_path, d))
            }
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot read contents of:\n{root_path}\n\nReason:\n{e}")
            return

        created = []
        skipped = []

        for sub in ("SRC", "Documentation", "Production_Files"):
            subpath = os.path.join(root_path, sub)
            if sub.lower() in existing_dirs:
                skipped.append(sub)
                continue
            try:
                os.makedirs(subpath, exist_ok=False)
                created.append(sub)
            except Exception as e:
                QMessageBox.critical(
                    self, "Error",
                    f"Failed to create sub-folder:\n  {sub}\n\nReason:\n  {e}"
                )
                return

        # Feedback
        summary = []
        if created:
            summary.append(f"Created: {', '.join(created)}")
        if skipped:
            summary.append(f"Skipped (already existed): {', '.join(skipped)}")
        if summary:
            QMessageBox.information(self, "Folder Creation Results", "\n".join(summary))

        # Update status
        if self.dot:
            self.dot.setStyleSheet("background-color: #2ECC71; border-radius: 6px;")
        if self.status_label:
            self.status_label.setText(name)

        open(os.path.join(root_path, "Readme.txt"), "a").close()
        
        # build the path and keep it in a local var
        metadata_path = os.path.join(root_path, ".KPMmetadata.txt")

        try:
            with open(metadata_path, "w") as meta_file:
                meta_file.write(f"Project Name: {name}\n")
                meta_file.write("Folders:\n")
                for folder in ("SRC", "Documentation", "Production_Files"):
                    if os.path.isdir(os.path.join(root_path, folder)):
                        meta_file.write(f"  - {folder}\n")
                meta_file.write(
                    f"Created On: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to write metadata:\n{e}")
            return
       
        project_manager.set_project(name, root_path)
        
        self.tree.clear()
        root = QTreeWidgetItem([name])
        #! update this to print out all the items in the folder not a static
        for sub in (
            "SRC (.kicad_pro)",
            "Documentation (SCH_PDF, PCB_PDF, Images)",
            "Production File (Gerber, Placement, BOM)",
            "Readme"
        ):
            root.addChild(QTreeWidgetItem([sub]))
        self.tree.addTopLevelItem(root)
        root.setExpanded(True)
 
        
#**********************************************************************************************************#
#TESTING FINCTIONALITY
if __name__ == "__main__":
    # import sys
    # from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QHBoxLayout, QVBoxLayout, QWidget

    app = QApplication(sys.argv)

    # Dummy activity status widgets
    status_dot = QLabel()
    status_dot.setFixedSize(12, 12)
    status_dot.setStyleSheet("background-color: grey; border-radius: 6px;")

    status_label = QLabel("No Project")

    # Top status bar
    status_bar = QHBoxLayout()
    status_bar.addWidget(QLabel("Activity : "))
    status_bar.addWidget(status_dot)
    status_bar.addWidget(status_label)
    status_bar.addStretch()

    # Combine layout
    main_layout = QVBoxLayout()
    main_layout.addLayout(status_bar)
    main_layout.addWidget(CreateProjectWidget(status_dot=status_dot, status_label=status_label))

    container = QWidget()
    container.setLayout(main_layout)

    window = QMainWindow()
    window.setWindowTitle("Test CreateProjectWidget")
    window.setCentralWidget(container)
    window.resize(600, 500)
    window.show()

    sys.exit(app.exec())

       
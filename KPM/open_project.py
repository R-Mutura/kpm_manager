  
import os
import sys
import datetime

from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QMainWindow, QFileDialog,
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QTreeWidget,
    QTreeWidgetItem, QLabel, QMessageBox
)
from PySide6.QtCore import Qt
from global_project_manager import project_manager
from ui_elements.loglevel_logic import CustomLogger
# Get the singleton instance
log_manager = CustomLogger()

class OpenProjectWidget(QWidget):
    def __init__(self, status_dot=None, status_label=None):
        super().__init__()
        self.dot = status_dot
        self.status_label = status_label

        opLayout = QVBoxLayout(self)

        # Project Folder Input Section
        opFolder_layout = QHBoxLayout()
        self.folder_edit = QLineEdit()
        self.folder_edit.setPlaceholderText("Select Project Folder")
        opbrowse_btn = QPushButton("Browse")
        opbrowse_btn.clicked.connect(self.browse_folder)
        opFolder_layout.addWidget(QLabel("Project Folder:"))
        opFolder_layout.addWidget(self.folder_edit)
        opFolder_layout.addWidget(opbrowse_btn)

        # Tree view and Open Button
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)

        open_btn = QPushButton("Open Project")
        open_btn.clicked.connect(self.on_openProject)

        opLayout.addLayout(opFolder_layout)
        opLayout.addWidget(open_btn)
        opLayout.addWidget(QLabel("Project Structure Preview:"))
        opLayout.addWidget(self.tree)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Project Base Folder")
        if folder:
            self.folder_edit.setText(folder)

    def on_openProject(self):
        basefolder = self.folder_edit.text().strip()

        if not basefolder:
            QMessageBox.critical(self, "Error", "Provide a valid project folder.")
            return False

        # 1) Check for metadata file
        meta_file = os.path.join(basefolder, ".KPMmetadata.txt")
        if not os.path.isfile(meta_file):
            QMessageBox.critical(self, "Error", f"No .KPMmetadata.txt found in:\n{basefolder}")
            return False

        # 2) Read and parse project name from metadata
        try:
            with open(meta_file, "r") as f:
                lines = f.readlines()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot read metadata file:\n{e}")
            return False

        project_name = None
        for line in lines:
            if line.lower().startswith("project name:"):
                project_name = line.split(":", 1)[1].strip()
                break

        if not project_name:
            QMessageBox.critical(self, "Error", ".KPMmetadata.txt missing 'Project Name:' entry.")
            return False

        # 2b) Compare metadata name with folder name
        folder_name = os.path.basename(os.path.normpath(basefolder))
        if project_name != folder_name:
            QMessageBox.warning(
                self, "Warning",
                f"Metadata project name '{project_name}'\n"
                f"does not match folder name '{folder_name}'."
            )

        # 3) Check required sub‑folders exist (case‑insensitive)
        required = {"src", "documentation", "production_files"}
        try:
            existing = {
                d.lower() for d in os.listdir(basefolder)
                if os.path.isdir(os.path.join(basefolder, d))
            }
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot list directory:\n{e}")
            return False

        missing = required - existing
        if missing:
            QMessageBox.critical(
                self, "Error",
                "Missing required folders:\n  " + "\n  ".join(missing)
            )
            return False

        # ✅ All checks passed: update UI
        self.dot.setStyleSheet("background-color: #2ECC71; border-radius: 6px;")
        self.status_label.setText(project_name)
        #singleton function to manage state of project
        project_manager.set_project(project_name, basefolder)
        
        self.db = project_manager.open_sqlite_database()
        if self.db:
            print("database active")
            # QMessageBox.warning(
            #     None,
            #     "Database SetUp Success",
            #     f"Opened database"
                
            # )
            # Create table if needed
        if not project_manager.create_project_table(self.db):
            sys.exit(1)

            #read its current content 
     
        project_logstate = project_manager.read_project_progress(self.db, project_manager.get_project_path(), item_to_read = "logstate")
        if(project_logstate):
            print("log level status: ", project_logstate)
            log_manager.set_log_level(project_logstate) #set log state
            project_manager.log_level_change.emit(project_logstate)
            if log_manager.get_log_level() == "High":
                QMessageBox.information(
                    None,
                    "Loaded Progress",
                    str(project_logstate)
                )

        project_progress = project_manager.read_project_progress(self.db, project_manager.get_project_path())
        if(project_progress):
            print("db_read_data:", project_progress)
            project_manager.default_states = project_progress #save the project statu and emit a signal to the status bar 
            project_manager.project_progress_status.emit(project_progress)
            # if log_manager.get_log_level() == "High":
            #     QMessageBox.information(
            #         None,
            #         "Loaded Progress",
            #         str(project_progress)
            #     )
        else: 
            #if the project is not present in the data base then we add it
            ok = project_manager.insert_or_update_project(
                self.db,
                project_manager.get_project_name(),
                project_manager.get_project_path(),
                project_manager.default_states,
                
            )
            if not ok:
                # sys.exit(1)
                print("Error writing to the database")

        #close the db
        project_manager.close_db(self.db)
        #***************************
        print("Project set:")   
        Namep = project_manager.get_project_name()
        pathp = project_manager.get_project_path()
        print("Project confirm:")
        print(Namep)
        print(pathp)#absolute path of the project folder
        # Update tree view
        self.tree.clear()
        root = QTreeWidgetItem([project_name])
        for sub in (
            "SRC (.kicad_pro)",
            "Documentation (SCH_PDF, PCB_PDF, Images)",
            "Production File (Gerber, Placement, BOM)",
            "Readme"
        ):
            root.addChild(QTreeWidgetItem([sub]))
        self.tree.addTopLevelItem(root)
        root.setExpanded(True)

        return True

#**********************************************************************************************************#
# # TESTING FUNCTIONALITY
# if __name__ == "__main__":
#     app = QApplication(sys.argv)

#     # Dummy activity status widgets
#     status_dot = QLabel()
#     status_dot.setFixedSize(12, 12)
#     status_dot.setStyleSheet("background-color: grey; border-radius: 6px;")

#     status_label = QLabel("No Project")

#     # Top status bar
#     status_bar = QHBoxLayout()
#     status_bar.setContentsMargins(10, 10, 10, 10)
#     status_bar.addWidget(QLabel("Activity : "))
#     status_bar.addWidget(status_dot)
#     status_bar.addWidget(status_label)
#     status_bar.addStretch()

#     # Combine layout
#     main_layout = QVBoxLayout()
#     main_layout.addLayout(status_bar)
#     main_layout.addWidget(OpenProject(status_dot=status_dot, status_label=status_label))

#     container = QWidget()
#     container.setLayout(main_layout)

#     window = QMainWindow()
#     window.setWindowTitle("Test OpenProject Widget")
#     window.setCentralWidget(container)
#     window.resize(600, 500)
#     window.show()

#     sys.exit(app.exec())

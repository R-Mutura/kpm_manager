import os
import sys
import datetime
import json
import subprocess

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

from ui_elements.loglevel_logic import CustomLogger
# Get the singleton instance
log_manager = CustomLogger()


class CreateProjectWidget(QWidget):
    def __init__(self, status_dot=None, status_label=None):
        super().__init__()
        self.dot = status_dot
        self.status_label = status_label
        self.kicad_cli = project_manager.get_kicad_cli()
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
        #populate the database withthe new project .
        self.db = project_manager.open_sqlite_database()
        if self.db:
            print("Project opened successfully")
            # if log_manager.get_log_level() == "High":
            #     QMessageBox.warning(
            #         None,
            #         "Database SetUp Success",
            #         f"Opened database"
                    
            #     )
            # Create table if needed
        if not project_manager.create_project_table(self.db):
            sys.exit(1)

            #read its current content 
            
            #write our cata to it
        description = "to be added"
        ok = project_manager.insert_or_update_project(
            self.db,
            project_manager.get_project_name(),
            project_manager.get_project_path(),
            project_manager.default_states,
            description
        )
        if not ok:
            sys.exit(1)
       
        project_progress = project_manager.read_project_progress(self.db, project_manager.get_project_path())
        if(project_progress):
            if log_manager.get_log_level() == "High":
                print("db_read_data:", project_progress)
                QMessageBox.information(
                    None,
                    "Loaded Progress",
                    str(project_progress)
                )

        ok = project_manager.update_project_loglevel(self.db, project_manager.get_project_path())
        log_level_state = project_manager.read_project_progress(self.db, project_manager.get_project_path(), item_to_read = "logstate")
        if log_manager.get_log_level() == "High":
            if(log_level_state):
                if log_manager.get_log_level() == "High":
                    print("Log state level:", log_level_state)
                    QMessageBox.information(
                        None,
                        "Loaded Progress",
                        str(log_level_state)
                    )
        #close the db
        project_manager.close_db(self.db)
        reply = QMessageBox.question(
            self,
            "Create KiCad Project?",
            f"Do you want to create a KiCad project file in the SRC folder?\n\nIt will be named '{name}.kicad_pro'.",
            QMessageBox.Ok | QMessageBox.Cancel
        )
        if reply == QMessageBox.Ok:
            project_dir = os.path.join(root_path, "SRC", name)
            os.makedirs(project_dir, exist_ok=True)
            
            kicad_project_path = os.path.join(project_dir, f"{name}.kicad_pro")
            

            try:
                # 1. Create empty schematic and PCB files
                # subprocess.run([self.kicad_cli, "schematic", "new", schematic_path])
                # subprocess.run([self.kicad_cli, "pcb", "create", pcb_path])

                # 2. Populate the .kicad_pro with references
                #! note: this can be removed if it causes compatability issues in your kicad verion
                project_data = {
                    "version": 1,
                    "project": {
                        "title": name,
                        "date": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "rev": "A1",
                        "company": "MyCompany",
                        "schematic": f"{name}.kicad_sch",
                        "board": f"{name}.kicad_pcb",
                        "page_layout": "kicad",
                        "paper": "A4"
                    },
                    "libraries": {
                        "symbols": [{"name": "Device", "type": "global"}],
                        "footprints": [{"name": "kicad-footprints", "type": "global"}]
                    },
                    "metadata": {
                        "created_with": "kpm-tool",
                        "last_updated": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                }

                with open(kicad_project_path, "w") as kicad_file:
                    json.dump(project_data, kicad_file, indent=2)
                    
                    
                # 3. Open with system default
                if sys.platform.startswith("win"):
                    os.startfile(kicad_project_path)
                elif sys.platform.startswith("darwin"):
                    os.system(f"open '{kicad_project_path}'")
                else:
                    os.system(f"xdg-open '{kicad_project_path}'")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create or open KiCad project:\n{e}")

        
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

       
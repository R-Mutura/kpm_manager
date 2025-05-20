#!/usr/bin/env python3
import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton,
    QFileDialog, QTreeWidget, QTreeWidgetItem,
    QListWidget, QListWidgetItem, QMenuBar, QMenu,
    QMessageBox
)
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KiCAD PROJECT MANAGER")
        self.resize(800, 500)
        
        
        # ─── Menu Bar ────────────────────────────────────────────────────
        menu_bar = QMenuBar()
        menu_bar.addMenu("Menu")
        menu_bar.addMenu("Help")
        self.setMenuBar(menu_bar)
        # ------ ACTIVITY BAR ----------------------------------

        # ─── Central Widget & Layout ───────────────────────────────────
        central = QWidget()
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(20)

        # ─── Left Panel: Action List ────────────────────────────────────
        action_box = QGroupBox("Action")
        action_layout = QVBoxLayout(action_box)
        # Describe style for the left box buttons
        toolbar_button_style = """
            background: #D3D3D3;
            border: none;
            padding: 8px;
            text-align: left;
            border-radius: 7px;
        """


        for txt in (
            "Create Project",
            "Open Project",
            "Generate Documentation",
            "Review and Verify",
            "Generate Production Files",
        ):
            toolbar_button = QPushButton(txt)
            toolbar_button.setStyleSheet(toolbar_button_style)
            # connect each button to the same slot, passing its text
            toolbar_button.clicked.connect(lambda checked, t=txt: self.on_action_selected(t))
            action_layout.addWidget(toolbar_button)
        action_layout.addStretch()
        main_layout.addWidget(action_box, 1)

        # ─── Right Panel ────────────────────────────────────────────────
        right_layout = QVBoxLayout()
        # Activity status line
        status_hbox = QHBoxLayout()
        status_hbox.setContentsMargins(0,0,0,5) #add a bottom setContentsMargins

        self.dot = QLabel()
        self.dot.setFixedSize(12,12) #12px by 12px size
        self.dot.setStyleSheet (
            #"background-color: #2ECC71;"  # nice green will be set either on opening a valid projectt or on creating one
            "background-color: #808080;"
            "border-radius: 6px;"         # half of width/height → circle
        ) 

       #add a text label to hold the project name (place holder is no active project)
        self.status_label = QLabel("no Active Project")
        self.status_label.setStyleSheet("font-weight: bold;")

        #combine to form thelayout on the status_hbox
        status_hbox.addWidget(QLabel("Activity"))
        status_hbox.addWidget(self.dot)
        status_hbox.addWidget(QLabel(":"))
        status_hbox.addWidget(self.status_label) #Dynamic project name to be added later
        status_hbox.addStretch() #push left 

        right_layout.addLayout(status_hbox)
        # — Description GroupBox —
        desc_box = QGroupBox("Description")
        desc_layout = QVBoxLayout(desc_box)

        # — Form for Project Name & Folder —
        form_layout = QFormLayout()
        self.name_edit = QLineEdit()
        form_layout.addRow("Project Name:", self.name_edit)

        # Project folder + Browse
        folder_h = QHBoxLayout()
        self.folder_edit = QLineEdit()
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self.on_browse)
        folder_h.addWidget(self.folder_edit)
        folder_h.addWidget(self.browse_btn)
        form_layout.addRow("Project Folder:", folder_h)

        desc_layout.addLayout(form_layout)

        # — Create Button —
        self.create_btn = QPushButton("Create")
        self.create_btn.clicked.connect(self.on_create)
        desc_layout.addWidget(self.create_btn, alignment=Qt.AlignLeft)

        # — Folder Structure Tree —
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        desc_layout.addWidget(self.tree)

        right_layout.addWidget(desc_box)
        main_layout.addLayout(right_layout, 3)

        self.setCentralWidget(central)

    def on_browse(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if folder:
            self.folder_edit.setText(folder)

    def on_create(self):
        """Stub: create the folder structure and populate the tree view."""
        base = self.folder_edit.text().strip()
        name = self.name_edit.text().strip()
        if not base or not name:
            QMessageBox.critical(self, "Error", f"Provide project name and a Valid Project Folder:\n")
            return
        
        # build structure in file system (optional)
        root_path = os.path.join(base, name)
        #os.makedirs(root_path, exist_ok=True)
        try:
            os.makedirs(root_path, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not create root folder:\n{e}")
            return  # stop here on failure

        # check if the subfolder of interest are in existence first o that we do not over write them
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
            
             # case‑insensitive existence check
            if sub.lower() in existing_dirs:
                skipped.append(sub)
                continue  # <- don't try to re‑create or overwrite

            try:
                 os.makedirs(subpath, exist_ok=True)
                 created.append(sub)
                #  if os.path.isdir(subpath):
                    
                #  else:
                #     #failed.append(sub)
            except Exception as e:
                #failed.append(sub) 
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to create sub‑folder:\n  {sub}\n\nReason:\n  {e}"
                )
        summary = []
        if created:
            summary.append(f"Created: {', '.join(created)}")
        if skipped:
            summary.append(f"Skipped (already existed): {', '.join(skipped)}")
        if summary:
            QMessageBox.information(self, "Folder Creation Results", "\n".join(summary))

        
        
        #set the activity bar/status accordingly
        self.dot.setStyleSheet (
        "background-color: #2ECC71;"  # nice green will be set either on opening a valid projectt or on creating one
        "border-radius: 6px;"
        )
        self.status_label.setText(name)

            
        # create a placeholder README
        open(os.path.join(root_path, "Readme.txt"), "a").close()

        # populate QTreeWidget
        self.tree.clear()
        root = QTreeWidgetItem([f"{name}"])
        for sub in ("SRC (.kicad_pro)", "Documentation (SCH_PDF, PCB_PDF, Images)",
                    "Production_Files (Gerber, Placement, BOM)", "Readme"):
            child = QTreeWidgetItem([sub])
            root.addChild(child)
        self.tree.addTopLevelItem(root)
        root.setExpanded(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())

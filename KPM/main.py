# main.py
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QGroupBox, QLabel, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap
import os
    # """_summary_
    #    #F68B1F => c85103 => dark orange
       
    #    # color schem used for icon on the  KPM logo
    # """
# color schem used for icon on the  KPM logo

from global_project_manager import project_manager 
from create_project import CreateProjectWidget
from open_project import OpenProjectWidget
from documentation_genrt import DocumentationGenerationWidget
from project_tree_view import ProjectFileTreeWidget
from productionfiles_gen_ui import ProductionFilesGeneratorWidget

from ui_elements.log_level_ui import LogLevelWidget
from ui_elements.progress_bar_logic import ProjectProgressWidget


# from ProjectState import ProjectManager
#this will keep track of the current opened/created project across all the files and ui

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Logo Label
        self.logo_widget = QWidget()
        logo_layout = QVBoxLayout(self.logo_widget)
        logo_layout.setContentsMargins(0, 10, 0, 10)
        logo_layout.setAlignment(Qt.AlignCenter)

        logo_label = QLabel()
        logo_pixmap = QPixmap("icons/app_icon.png")  # Adjust the path as needed
        logo_pixmap = logo_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        
        logo_layout.addWidget(logo_label)
        
        self.setWindowTitle("KiCAD Project Manager")
        icons = {
            "Create Project": "create.png",
            "Open Project": "open.png",
            "Generate Documentation": "documentation.png",
            "Review": "review.png",
            "Generate Production Files": "production.png",
            "Verify": "verify.png"
        }
        icon_dir = os.path.join(os.path.dirname(__file__), "icons")
        

        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        # Left panel with buttons
        left_box = QGroupBox("Action")
        left_layout = QVBoxLayout(left_box)

        self.actions = { 
             #a dictionary of actions is created by which we will populate the action widget
            "Create Project": self.load_create_project,
            "Open Project":   self.load_open_project,
            "Generate Documentation": self.load_doc_generator,
            "Review": self.load_create_project,
            "Generate Production Files": self.load_production_files,
            "Verify": self.load_create_project,
            # Add more buttons later
        }
        self.button = {}
        
        # Store the currently active button
        self.active_button = None
        
        # Style definitions
        self.normal_style = """
            QPushButton {
                background-color: #D3D3D3;
                border-radius: 6px;
                padding: 8px;
                text-align: left;
            }
        """

        self.active_style = """
            QPushButton {
                background-color: #FFD580;  /* Light orange */
                border-radius: 6px;
                padding: 8px;
                text-align: left;
            }
        """

        for label, func in self.actions.items():
            btn = QPushButton(label)
            btn.setStyleSheet(self.normal_style)
            #add the relevant icons
            icon_path = icons.get(label)
            if icon_path:
                full_icon_path = os.path.join(icon_dir, icon_path)
                if os.path.exists(full_icon_path):
                    btn.setIcon(QIcon(full_icon_path))
                    
            #end of icon addition function
            btn.clicked.connect(lambda _, b=btn, f=func: self.handle_button_click(b, f))
            left_layout.addWidget(btn)
            self.button[label] = btn
            
        
        
        self.project_tree_widget = ProjectFileTreeWidget(None)
        # Limit its height to half the parent (initially)
        self.project_tree_widget.setMaximumHeight(self.height() // 2)
        #left_layout.addWidget(self.project_tree_widget, alignment=Qt.AlignBottom)
        left_layout.addWidget(self.project_tree_widget)
        
        #log level buttons to allow flexible implementation of log levels
        loglevelselector = LogLevelWidget()
        loglevelselector.setMinimumHeight(80)
        loglevelselector.setMaximumHeight(120)
        loglevelselector.setStyleSheet("background-color: #D3D3D3; border-radius: 6px; padding: 8px; text-align: left;")
        left_layout.addWidget(loglevelselector)
        # add progress bar
        self.progressbarstatus = ProjectProgressWidget()
        left_layout.addWidget(self.progressbarstatus)
        # Add a spacer to push the logo to the bottom   
        
        left_layout.addStretch()
        
        left_layout.addWidget(self.logo_widget)
        
        # Connect signal
        project_manager.project_changed.connect(self.on_project_changed)
        project_manager.update_document_tree.connect(self.on_project_update)
        project_manager.project_progress_status.connect(self.updateProjectProgress)
                
        
        
        # Status bar with dot
        self.dot = QLabel()
        self.dot.setFixedSize(12, 12)
        self.dot.setStyleSheet("background-color: gray; border-radius: 6px;")
        self.activity_label = QLabel("Activity : ")
        self.status_label = QLabel(" No project loaded")
        
        # Wrap status bar the layout in a QWidget
        status_bar_widget = QWidget()
        status_bar = QHBoxLayout(status_bar_widget)
        status_bar.setContentsMargins(5, 0, 0, 5)
        status_bar.setSpacing(5)
        status_bar.addWidget(self.activity_label)
        status_bar.addWidget(self.dot)
        status_bar.addWidget(self.status_label)
        status_bar.addStretch()
        # Set maximum height to 10px
        status_bar_widget.setMaximumHeight(25)

        # Right side dynamic area
        self.right_box = QGroupBox("Description")
        self.right_layout = QVBoxLayout(self.right_box)
        
        

        # Combine right layout
        right_panel = QVBoxLayout()
        right_panel.addWidget(status_bar_widget)
        right_panel.addWidget(self.right_box)

        # Final layout
        
        main_layout.addWidget(left_box, 1)
        main_layout.addLayout(right_panel, 3)

        self.setCentralWidget(main_widget)
    # START OF FUNTION    
    def resizeEvent(self, event):
        #resize theproject tree widget dynamically
        # Adjust the maximum height of the project tree widget based on the window height
        super().resizeEvent(event)
        if hasattr(self, 'project_tree_widget'):
            self.project_tree_widget.setMaximumHeight(self.height() // 2)
            
    def updateProjectProgress(self, progress_dict):
        #update progress bar
        print("Progress update received:", progress_dict)
        self.progressbarstatus.updateProjectProgress(progress_dict)

        #update metadata once there are valid changes
        project_manager.update_metadata(project_manager.get_project_path(), "Progress")


    #handle signal emmited on set_project in ProjectState projectstate manager
    def on_project_changed(self, name: str, is_open: bool, path: str):
        if is_open:
            self.project_tree_widget.load_project(path)
            self.project_tree_widget.repaint()
        else:
            self.project_tree_widget.load_project(None)
            # self.project_tree_widget.tree_widget.clear()
            # self.project_tree_widget.label.setText("Project Root: Not loaded")
    def on_project_update(self):
        
            self.project_tree_widget.load_project(project_manager.get_project_path())
            self.project_tree_widget.repaint()
        
            # self.project_tree_widget.tree_widget.clear()
            # self.project_tree_widget.label.setText("Project Root: Not loaded")
            
    def handle_button_click(self, clicked_button, action_function):
        # Reset previous
        if self.active_button:
            self.active_button.setStyleSheet(self.normal_style)

        # Set new active
        clicked_button.setStyleSheet(self.active_style)
        self.active_button = clicked_button

        # Call the action
        action_function() #eg load_create_project()
        
    def clear_right(self):
        for i in reversed(range(self.right_layout.count())):
            widget = self.right_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def load_create_project(self):
        self.right_box.setTitle("Create Project")
        self.clear_right()
        widget = CreateProjectWidget(status_dot=self.dot, status_label=self.status_label)
        self.right_layout.addWidget(widget)
        
        
    
    def load_open_project(self):
        self.right_box.setTitle("Open Project")
        self.clear_right()
        widget = OpenProjectWidget(status_dot=self.dot, status_label=self.status_label)
        self.right_layout.addWidget(widget)
    def load_doc_generator(self):
        self.right_box.setTitle("Generate Documentation")
        self.clear_right()
        #get the project details i.e name and path from project_manager
        Namep = project_manager.get_project_name()
        pathp = project_manager.get_project_path()
        print(f"Namep: {Namep}")
        print(f"pathp: {pathp}")
        widget = DocumentationGenerationWidget(status_dot=self.dot, status_label=self.status_label, project_name=Namep, project_path=pathp)
        self.right_layout.addWidget(widget)
    def load_production_files(self):
        self.right_box.setTitle("Production Files Generator")
        self.clear_right()
        #get the project details i.e name and path from project_manager
        Namep = project_manager.get_project_name()
        pathp = project_manager.get_project_path()
        print(f"Namep: {Namep}")
        print(f"pathp: {pathp}")
        widget = ProductionFilesGeneratorWidget(status_dot=self.dot, status_label=self.status_label, project_name=Namep, project_path=pathp)
        self.right_layout.addWidget(widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon_path = os.path.join(os.path.dirname(__file__), "icons", "app_icon.png")
    app.setWindowIcon(QIcon(icon_path))

    win = MainWindow()
    win.show()
    win.resize(1000, 500)
    sys.exit(app.exec())

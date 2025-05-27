#10:01 AM 5/26/202510:01 AM 5/26/2025
# main.py
import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QGroupBox, QLabel, QFrame,
    QMessageBox, QLayout
)
from PySide6.QtCore import Qt, QStandardPaths

from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtSql import QSqlDatabase, QSqlQuery
import os
    # """_summary_
    #    #F68B1F => c85103 => dark orange
       
    #    # color schem used for icon on the  KPM logo
    # """
# color schem used for icon on the  KPM logo
from ProjectState import ProjectManager
from global_project_manager import project_manager 
from create_project import CreateProjectWidget
from open_project import OpenProjectWidget
from documentation_genrt import DocumentationGenerationWidget
from project_tree_view import ProjectFileTreeWidget
from productionfiles_gen_ui import ProductionFilesGeneratorWidget

from ui_elements.log_level_ui import LogLevelWidget
from ui_elements.progress_bar_logic import ProjectProgressWidget
from ui_elements.loglevel_logic import CustomLogger
from ui_elements.summarywidget_ui import SummaryWidget
from ui_elements.verification_ui import VerifyWidgetui
from ui_elements.settings_ui import SettingsWidget

#review elements
from review_ui import ReviewHTMLViewerWidget
# path to html path
html_path = os.path.join(os.path.dirname(__file__), "files", "reviewfile.html")
#html_path = r"C:\Users\user\Documents\python\kigui\kpm_manager\KPM\files\reviewfile.html"
# Get the singleton instance
log_manager = CustomLogger()

# from ProjectState import ProjectManager
#this will keep track of the current opened/created project across all the files and ui

class MainWindow(QMainWindow):
    def __init__(self, db_file: str):
        super().__init__()
        # Connect signal
        self.loglevelselector = LogLevelWidget()
        project_manager.log_level_change.connect(self.loglevelselector.on_selection_changed)
        project_manager.project_changed.connect(self.on_project_changed)
        project_manager.update_document_tree.connect(self.on_project_update)
        project_manager.project_progress_status.connect(self.updateProjectProgress)
              
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
            "Verify": "verify.png",
            "Settings": "settings.png"
        }
        icon_dir = os.path.join(os.path.dirname(__file__), "icons")
        
        #det databse path
        project_manager.set_db_path(db_file)

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
            "Review": self.load_review,
            "Generate Production Files": self.load_production_files,
            "Verify": self.load_verify,
            "Settings": self.load_settings,
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
        self.button_widgets = dict()
        
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
        
            
        #load all the button related widgets to a dict / dictionary
        #this ensures that the widget is instantiated only once and called multiple times in the life of the project without issues
        #this ensures that whatever changes are made in the widget persists through the lifetime of the application(mainwindow app)
        
        
        self.project_tree_widget = ProjectFileTreeWidget(None)
        # Limit its height to half the parent (initially)
        self.project_tree_widget.setMaximumHeight(self.height() // 2)
        #left_layout.addWidget(self.project_tree_widget, alignment=Qt.AlignBottom)
        left_layout.addWidget(self.project_tree_widget)
        
        #log level buttons to allow flexible implementation of log levels
        
        self.loglevelselector.setMinimumHeight(80)
        self.loglevelselector.setMaximumHeight(120)
        self.loglevelselector.setStyleSheet("background-color: #D3D3D3; border-radius: 6px; padding: 8px; text-align: left;")
        left_layout.addWidget(self.loglevelselector)
        # add progress bar
        self.progressbarstatus = ProjectProgressWidget()
        left_layout.addWidget(self.progressbarstatus)
        # Add a spacer to push the logo to the bottom   
        
        left_layout.addStretch()
        
        left_layout.addWidget(self.logo_widget)
        
          
        
        
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
        xproject_name=project_manager.get_project_name()
        xproject_path=project_manager.get_project_path()
        print(f"MMAINN ------ Project Name: {xproject_name}, Project Path: {xproject_path}")
        #initialize the widgets for dynamic loading
        self.button_widgets = {
                "documentationWidget": DocumentationGenerationWidget(status_dot=self.dot, status_label=self.status_label, project_name= xproject_name, project_path= xproject_path),
                "reviewWidget": ReviewHTMLViewerWidget(html_path, project_manager=project_manager),
                "productionWidget": ProductionFilesGeneratorWidget(status_dot=self.dot, status_label=self.status_label,  project_name=project_manager.get_project_name(), project_path=project_manager.get_project_path()),
                "verifyWidget": VerifyWidgetui(project_manager=project_manager),
                "settingsWidget": SettingsWidget(project_manager=project_manager)
                #others widgets to be loaded here
        }
        
    # START OF FUNTION    
    def resizeEvent(self, event):
        #resize theproject tree widget dynamically
        # Adjust the maximum height of the project tree widget based on the window height
        super().resizeEvent(event)
        if hasattr(self, 'project_tree_widget'):
            self.project_tree_widget.setMaximumHeight(self.height() // 2)
            
    def updateProjectProgress(self, progress_dict):
       
        if self.active_button:
            activepage = self.active_button.text()
            print(f"Active button text: {activepage}")
            if activepage.strip().lower() == "review":
                project_manager.default_states["Reviewed"] = True
                print(project_manager.default_states["Reviewed"])
         #update progress bar
         
        print("Progress update received:", progress_dict)
        self.progressbarstatus.updateProjectProgress(project_manager.default_states)

        #update the summary table
        if self.active_button:
            activepage = self.active_button.text()
            print(f"Active button text: {activepage}")
            if activepage.strip().lower() == "generate documentation":
                doc_widget = self.button_widgets["documentationWidget"]
                old_summary_widget = doc_widget.summaryWidget
                print("button: ", activepage.strip().lower())

                # Get the parent layout where the summaryWidget lives
                parent_layout = old_summary_widget.parentWidget().layout()
                if parent_layout is not None:
                    # Find and remove the old widget from the layout
                    for i in range(parent_layout.count()):
                        item = parent_layout.itemAt(i)
                        if item and item.widget() == old_summary_widget:
                            old_widget = parent_layout.takeAt(i).widget()
                            if old_widget:
                                old_widget.setParent(None)
                            break

                # Create and insert new SummaryWidget
                new_summary_widget = SummaryWidget(project_manager, activepage.strip().lower())
                doc_widget.summaryWidget = new_summary_widget  # update reference
                parent_layout.insertWidget(i, new_summary_widget)  # insert at same position   

            elif activepage.strip().lower() == "generate production files":
                
                doc_widget = self.button_widgets["productionWidget"]
                old_summary_widget = doc_widget.summaryWidget
                print("button: ", activepage.strip().lower())

                # Get the parent layout where the summaryWidget lives
                parent_layout = old_summary_widget.parentWidget().layout()
                if parent_layout is not None:
                    # Find and remove the old widget from the layout
                    for i in range(parent_layout.count()):
                        item = parent_layout.itemAt(i)
                        if item and item.widget() == old_summary_widget:
                            old_widget = parent_layout.takeAt(i).widget()
                            if old_widget:
                                old_widget.setParent(None)
                            break

                # Create and insert new SummaryWidget
                new_summary_widget = SummaryWidget(project_manager, activepage.strip().lower())
                doc_widget.summaryWidget = new_summary_widget  # update reference
                parent_layout.insertWidget(i, new_summary_widget)  # insert at same position 
            
            elif activepage.strip().lower() == "verify":
                # Handle the verification summary update
                doc_widget = self.button_widgets["verifyWidget"]
                old_summary_widget = doc_widget.summaryWidget
                print("button: ", activepage.strip().lower())

                # Get the parent layout where the summaryWidget lives
                parent_layout = old_summary_widget.parentWidget().layout()
                if parent_layout is not None:
                    # Find and remove the old widget from the layout
                    for i in range(parent_layout.count()):
                        item = parent_layout.itemAt(i)
                        if item and item.widget() == old_summary_widget:
                            old_widget = parent_layout.takeAt(i).widget()
                            if old_widget:
                                old_widget.setParent(None)
                            break

                # Create and insert new SummaryWidget
                new_summary_widget = SummaryWidget(project_manager, activepage.strip().lower(), checked_items=project_manager.verification_checklist)
                #print("new summary widget: ", new_summary_widget)
                doc_widget.summaryWidget = new_summary_widget  # update reference
                parent_layout.insertWidget(i, new_summary_widget)  # insert at same position 
                
        #update metadata in the sqlitebd
        #project_manager.open_sqlite_database()#parameters are already defined upon windows opening and setup
        self.db = project_manager.open_sqlite_database()
        # if self.db:
        #     QMessageBox.warning(
        #         None,
        #         "Database SetUp Success",
        #         f"Opened database"
                
        #     )
            # Create table if needed
        if not project_manager.create_project_table(self.db):
            sys.exit(1)            
            #write our data to it // only on the project tab
        ok = project_manager.update_project_progress(
            self.db,
            project_manager.get_project_path(),
            project_manager.default_states,
        )
        if not ok:
            description = "redefined description"
            ok = project_manager.insert_or_update_project(
                self.db,
                project_manager.get_project_name(),
                project_manager.get_project_path(),
                project_manager.default_states,
                description
            )
            if not ok:
                sys.exit(1)
        
        ok = project_manager.update_project_loglevel(self.db, project_manager.get_project_path(), log_manager.get_log_level())
        if ok:
            print("log level state recorded ")

        # project_progress = project_manager.read_project_progress(self.db, project_manager.get_project_path(), item_to_read = "logstate")
        # if(project_progress):
        #     print("log level status: ", project_progress)
        #     QMessageBox.information(
        #         None,
        #         "Loaded Progress",
        #         str(project_progress)
        #     )
        #close the db
        project_manager.close_db(self.db)


    #handle signal emmited on set_project in ProjectState projectstate manager
    def on_project_changed(self, name: str, is_open: bool, path: str):
        if is_open:
            self.project_tree_widget.load_project(path)
            self.project_tree_widget.repaint()
            #then we load all the widgets that will be used in the project hereby instantiating them once for the whole project
            
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
        
    # def clear_right(self):
    #     for i in reversed(range(self.right_layout.count())):
    #         widget = self.right_layout.itemAt(i).widget()
    #         if widget:
    #             widget.setParent(None)
    def clear_right(self):
        for i in reversed(range(self.right_layout.count())):
            item = self.right_layout.itemAt(i)
            widget = item.widget()
            if widget:
                self.right_layout.removeWidget(widget)
                widget.setVisible(False)  # Optional: hide instead of destroy the right widget
        

    def load_widget_by_key(self, key: str, title: str):
        self.right_box.setTitle(title)
        self.clear_right()

        widget = self.button_widgets.get(key)
        if widget:
            widget.setVisible(True)  # In case it was hidden before
            self.right_layout.addWidget(widget)
        else:
            print(f"[Error] Widget with key '{key}' not found.")

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
        #self.right_box.setTitle("Generate Documentation")
        self.clear_right()
        #widget = DocumentationGenerationWidget(status_dot=self.dot, status_label=self.status_label, project_name=Namep, project_path=pathp)
        # self.right_layout.addWidget(widget)
        if self.button_widgets:
            self.load_widget_by_key("documentationWidget","Generate Documentation")
        
    def load_production_files(self):
        #self.right_box.setTitle("Production Files Generator")
        self.clear_right()
        #get the project details i.e name and path from project_manager
        # widget = ProductionFilesGeneratorWidget(status_dot=self.dot, status_label=self.status_label, project_name=Namep, project_path=pathp)
        # self.right_layout.addWidget(widget)
        self.load_widget_by_key("productionWidget","Production Files Generator")
    
    def load_review(self):
        #self.right_box.setTitle("Production Files Generator")
        self.clear_right()
        #get the project details i.e name and path from project_manager
        # widget = ProductionFilesGeneratorWidget(status_dot=self.dot, status_label=self.status_label, project_name=Namep, project_path=pathp)
        # self.right_layout.addWidget(widget)
        self.load_widget_by_key("reviewWidget","Review Project")
    
    def load_settings(self):
        # self.right_box.setTitle("Settings")
        self.clear_right()
        self.load_widget_by_key("settingsWidget","Settings")
        # widget = SettingsWidget(project_kipath=project_manager.get_kicad_cli())
        # self.right_layout.addWidget(widget)
        
        # self.clear_right()
        # self.load_widget_by_key("settingsWidget","Settings")
    
    def load_verify(self):
        #self.right_box.setTitle("Production Files Generator")
        self.clear_right()
        #get the project details i.e name and path from project_manager
        # widget = ProductionFilesGeneratorWidget(status_dot=self.dot, status_label=self.status_label, project_name=Namep, project_path=pathp)
        # self.right_layout.addWidget(widget)
        self.load_widget_by_key("verifyWidget","Verify Project")


    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    #--------DATABASE RELATED FUNCTIONALITY-------------#
    #DEFINE location where this apps metadat/related data will be stored 
    #this will be handld by the qt-system
    #in windows the data is tored in C:\Users\user\AppData\Local\MyCompany\KPM
    #in linux yet to find out ->
    app.setOrganizationName("KPM")
    app.setApplicationName("KPM")
    #define data directory 
    home = os.path.expanduser("~")
      
    # create directory if it is not there
    db_file = os.path.join(home, "kpm_projects.db")
    
   
    
    #os.makedirs(db_file, exist_ok=True)
    #database class is interited in the project state instance as which allows us to use the project state to mage the database in any way we want
    #lets use the project_manager to open the database ---> see below after mainwidget is initalized
    
    #-------------END OF DATABASE FUNCTIONALITY----------#

    icon_path = os.path.join(os.path.dirname(__file__), "icons", "app_icon.png")
    app.setWindowIcon(QIcon(icon_path))

    win = MainWindow(db_file)#pass database dir here

    win.show()
    win.resize(1000, 500)

    
    # db = project_manager.open_sqlite_database(db_path = db_file)
    # if db:
    #     QMessageBox.warning(
    #         None,
    #         "Database SetUp Success",
    #         f"Opened database"
            
    #     )
    #     project_manager.close_db(db)
    
    #NOW CLOSING THE DDB AFTER USE Example


    sys.exit(app.exec())

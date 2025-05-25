from PySide6.QtCore import QObject, Signal
import os
import sys
import json
import datetime
import PySide6.QtSql #handle database
from PySide6.QtWidgets import QMessageBox

from database_elements.mydatabase import KpmDatabase #open an instance of the database for this project



class ProjectManager(QObject, KpmDatabase):
    # Signal emitted when project changes
     # Emit (project_name, is_open, project_path)
    #creating a signal that will be used to handle changes states and action generations here
    #1. signal 1 just emits a signal each time the generate button is pressed to update a documetn tree
    update_document_tree = Signal() # Define the signal just a basic signal
    #2. Emits a signal to update the progress bar in the main window to show level of execution in the project
    project_progress_status = Signal(dict) #takes in a disctionart { "name": true/false}
    """the default status of the project to be defined here (signleton slef implemented class so only one state of this will exists)
    so the items in the dict include below:

    end"""

    #3 handle project opening and closing.
    project_changed = Signal(str, bool, str)  #updates the current project

    default_states = {
            "Schematic_PDF": False,
            "PCB_PDF": False,
            "Images": False,
            "Step": False,
            "VRML": False,
            "BOM": False,
            "Gerber": False,
            "Placement": False,
            "Drill": False,
        }#defined as false on opening of the project manager

    def __init__(self):
        #super().__init__() #not used in double inheritances
        QObject.__init__(self)  # Initialize QObject part
        KpmDatabase.__init__(self)  # Initialize MyDatabase part

        self._project_name = None
        self._is_open = False
        self._project_path = None

    def set_project(self,  name: str, path: str):
        self._project_name = name
        self._project_path = path
        self._is_open = True
        self.project_changed.emit(name, True, path)

    def clear_project(self):
        self._project_name = None
        self._project_path = None
        self._is_open = False
        self.project_changed.emit("", False)

    def get_project_name(self):
        return self._project_name
    
    def get_project_path(self):
        return self._project_path

    def is_project_open(self):
        return self._is_open
    
    



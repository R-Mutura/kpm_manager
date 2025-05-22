from PySide6.QtCore import QObject, Signal
import os
import sys
import json
import datetime
from PySide6.QtWidgets import QMessageBox

class ProjectManager(QObject):
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
        super().__init__()
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
    
    def update_metadata(self, root_path:str, action:str):
        #takes in the root path and the action to write append or read (w,a,r)
        metadata_filename = ".KPMmetadata.txt"
        metadata_path = os.path.join(root_path, metadata_filename)
        # Ensure the file exists
        if not os.path.exists(metadata_path):
            try:
                with open(metadata_path, "w") as f:
                    f.write("")  # Create empty file
                    f.write(f"Project Name: {name}\n")
                    f.write("Folders:\n")
                    for folder in ("SRC", "Documentation", "Production_Files"):
                        if os.path.isdir(os.path.join(root_path, folder)):
                            f.write(f"  - {folder}\n")
                    f.write(
                        f"Created On: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to write metadata:\n{e}")
                return
        #if the file exists then we move here 
        # Read existing entries
        entries = []
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entry = json.loads(line)
                            entries.append(entry)
                        except json.JSONDecodeError:
                            continue  # skip malformed lines

        # Remove any existing entry with the same action
        entries = [e for e in entries if e.get("action") != action]

        # Build metadata dictionary to append

        new_entry  = {
            "action": action,
            "project_progress_status": self.default_states.copy()
        }
        new_entry["Project Name"] = self._project_name

        entries.append(new_entry)

        # Append the dictionary as a new line in the metadata file
        with open(metadata_path, "w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")



from PySide6.QtCore import QObject, Signal
import os
import sys
import json
import datetime
import platform


import PySide6.QtSql #handle database
from PySide6.QtWidgets import QMessageBox

from database_elements.mydatabase import KpmDatabase #open an instance of the database for this project


kicad_cli_name = "kicad-cli.exe"
kicad_bom_script_name = "bom_csv_grouped_by_value.py"
class ProjectManager(QObject, KpmDatabase):
    # Signal emitted when project changes
     # Emit (project_name, is_open, project_path)
    #creating a signal that will be used to handle changes states and action generations here
    #1. signal 1 just emits a signal each time the generate button is pressed to update a documetn tree
    update_document_tree = Signal() # Define the signal just a basic signal
    #2. Emits a signal to update the progress bar in the main window to show level of execution in the project
    project_progress_status = Signal(dict) #takes in a disctionart { "name": true/false}
    #signal to call on change from anywhere
    log_level_change = Signal(str)
    #3 handle project opening and closing.
    project_changed = Signal(str, bool, str)  #updates the current project
    # Emit (project_name, is_open, project_path)
    #*****************END OF SIGNALS DEFINITIONS************************//
    
    """the default status of the project to be defined here (signleton self implemented class so only one state of this will exists)
    so the items in the dict include below:

    end"""

    #checklist to handle the default states of the project
    #this is used to handle the default states of the project when it is opened
    default_states = {
            "Schematic_PDF": False,
            "PCB_PDF": False,
            "Images": False,
            "3D_file": False,
            "BOM": False,
            "Gerber": False,
            "Placement": False,
            "Drill": False,
            "Reviewed": False,
            "Verified": False
        }#defined as false on opening of the project manager

    #checklist to handle verification process in the last tab
    verification_checklist = []
    #KICAD_CLI = "" #HOLDS THE PATH TO THE KICAD_CLI depending on the OS used
        #function below will be used to set the cli path

    def __init__(self):
        #super().__init__() #not used in double inheritances
        QObject.__init__(self)  # Initialize QObject part
        KpmDatabase.__init__(self)  # Initialize MyDatabase part

        
        


        self._project_name = None
        self._is_open = False
        self._project_path = None

        self.kicad_cli =None

    
    # ─── Platform Detection ─────────────────────────────────────────
    @staticmethod
    def is_windows() -> bool:
        return os.name == 'nt' or platform.system() == 'Windows'

    @staticmethod
    def is_mac() -> bool:
        return platform.system() == 'Darwin'

    @staticmethod
    def is_wsl() -> bool:
        if platform.system() != 'Linux':
            return False
        return 'microsoft' in platform.uname().release.lower()

    @staticmethod
    def is_linux() -> bool:
        return platform.system() == 'Linux' and not DocGeneratorKiCLI.is_wsl()

    @staticmethod
    def current_os() -> str:
        if ProjectManager.is_wsl():
            return 'wsl'
        if ProjectManager.is_windows():
            return 'windows'
        if ProjectManager.is_mac():
            return 'mac'
        if ProjectManager.is_linux():
            return 'linux'
        return 'unknown'

    # ─── Path Conversion ────────────────────────────────────────────
    @staticmethod
    def wsl_to_windows_path(wsl_path: str) -> str:
        if wsl_path.startswith("/mnt/"):
            parts = wsl_path.split("/")
            drive = parts[2].upper() + ":"
            return os.path.join(drive, *parts[3:])
        return wsl_path

    # ─── Tests ─────────────────────────────────────────────────────
    def test_cli(self):
        """Prints kicad-cli version to confirm we can call it."""
        print(f"Detected OS: {self.current_os()} → using `{self.kicad_cli}`")
        try:
            result = subprocess.run(
                [self.kicad_cli, "--version"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print("KiCad CLI Version:", result.stdout.strip())
        except subprocess.CalledProcessError as e:
            print("Error running KiCad CLI:", e.stderr)

    # ─── End of os detection scripts────────────────────────────

    #TODO: make these function dynamically called or available to be set by the user
    def set_kicad_cli(self, path = None):
        if path == None:
            print("none")


    def get_kicad_cli(self):
        # Decide which kicad-cli to call based on our OS
        if self.kicad_cli == None:

            os_type = ProjectManager.current_os()
            if os_type == "windows":
                #self.kicad_cli = r"C:\Program Files\KiCad\9.0\bin\kicad-cli.exe"
                return r"C:\Program Files\KiCad\9.0\bin\kicad-cli.exe"
            elif os_type == "wsl":
                # if you want to call the Windows exe from WSL
                #self.kicad_cli = "/mnt/c/Program Files/KiCad/9.0/bin/kicad-cli.exe"
                return "/mnt/c/Program Files/KiCad/9.0/bin/kicad-cli.exe"
            else:
                # assume it's on your $PATH (Linux/macOS install)
                #self.kicad_cli = "kicad-cli"
                return "kicad-cli"
        else:
            return kicad_cli
        
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
    
    



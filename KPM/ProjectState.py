from PySide6.QtCore import QObject, Signal
import os
import sys
import json
import datetime
import platform
import subprocess


import PySide6.QtSql #handle database
from PySide6.QtWidgets import QMessageBox

from database_elements.mydatabase import KpmDatabase #open an instance of the database for this project


kicad_cli_name = "kicad-cli.exe"
kicad_bom_script_name = "bom_csv_grouped_by_value.py"

class ProjectManager(QObject, KpmDatabase):
    _instance = None
    
    
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ProjectManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    
    
    application_name = "KPM"  # Application name 
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
    save_kicad_paths_signal = Signal(str, str)  # Emit (kicad_cli_path, kicad_bom_script_path)
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
        if self._initialized:
            return
        self._initialized = True
        #super().__init__() #not used in double inheritances
        QObject.__init__(self)  # Initialize QObject part
        KpmDatabase.__init__(self)  # Initialize MyDatabase part

        
        


        self._project_name = None
        self._is_open = False
        self._project_path = None

        self.kicad_cli = None
        print("ProjectManager initialized once")

    
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
        return platform.system() == 'Linux' and not ProjectManager.is_wsl()

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
    def set_kicad_cli(self, kicad_cli_path = None, kicad_bom_script_path = None):
        """Sets the path to the kicad-cli executable and the bom script."""
        if kicad_cli_path is not None:
            self.kicad_cli = kicad_cli_path
            self.kicad_bom_script = kicad_bom_script_path
            #save the paths to the json file in C:\Users\ujuzi\KPM\kicad_paths.json
            self.kicad_cli = os.path.normpath(self.kicad_cli)
            self.kicad_bom_script = os.path.normpath(self.kicad_bom_script)
            # Ensure the directory exists
            self.save_kicad_paths(kicad_cli_path, kicad_bom_script_path)
        else:
            self.kicad_cli = self.get_kicad_cli()
            self.kicad_bom_script = os.path.join(os.path.dirname(self.kicad_cli), "scripting", "plugins", kicad_bom_script_name)
                 
            #self.kicad_bom_script = os.path.join(os.path.dirname(self.kicad_cli), "scripting", "plugins", kicad_bom_script_name)
           


    def get_kicad_cli(self):
        # Decide which kicad-cli to call based on our OS
        
        if self.kicad_cli == None:
            self.kicad_cli = self.read_kicad_json()
            self.kicad_bom_script = os.path.join(os.path.dirname(self.kicad_cli), "scripting", "plugins", kicad_bom_script_name)
            return self.kicad_cli
        else:
            return None
        
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
    
    def save_kicad_paths(self, kicad_cli_path: str, kicad_bom_script_path: str):
        #application_name
        home = os.path.expanduser("~")
        application_dir = os.path.join(home, self.application_name)
        if not os.path.exists(application_dir):
            os.makedirs(application_dir)
        
        application_info_path = os.path.join(application_dir, "kicad_paths.json")
        
        paths = {
            "kicad_cli": kicad_cli_path,
            "kicad_bom_script": kicad_bom_script_path
        }
        with open(application_info_path, "w") as f:
            json.dump(paths, f, indent=4)
    
        print(f"Saved KiCad paths to kicad_paths.json: {paths}")
        
        
    def read_kicad_json(self) -> str:
        """Loads and returns the KiCad CLI path from the saved JSON configuration."""
        home = os.path.expanduser("~")
        application_dir = os.path.join(home, self.application_name)
        application_info_path = os.path.join(application_dir, "kicad_paths.json")

        if not os.path.isfile(application_info_path):
            print( "Missing File", "No saved KiCad path found. Please configure the path.")
            return ""

        try:
            with open(application_info_path, "r") as f:
                data = json.load(f)
                return data.get("kicad_cli", "")
        except json.JSONDecodeError:
            print( "Corrupt File", "The KiCad path file is corrupted. Please reconfigure.")
            return ""
        except Exception as e:
            print("Error", f"Failed to load KiCad CLI path: {e}")
            return ""

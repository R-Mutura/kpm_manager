from PySide6.QtCore import QObject, Signal

class ProjectManager(QObject):
    # Signal emitted when project changes
     # Emit (project_name, is_open, project_path)
    project_changed = Signal(str, bool, str)  

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

import sys
import os
import json

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMessageBox
)
from PySide6.QtSql import QSqlDatabase, QSqlQuery
from PySide6.QtCore import QStandardPaths

# --- Database Helper Class -----------------------------------------------

class KpmDatabase:
    def __init__(self, db_path: str = None):
        self.db_path = db_path

    def set_db_path(self,passed_db_path):
        self.db_path =passed_db_path

    def open_sqlite_database(self, connection_name: str = "app_sqlite"):
        """
        Opens (or creates) an SQLite database at self.db_path and returns the QSqlDatabase.
        """
        db = QSqlDatabase.addDatabase("QSQLITE", connection_name)
        db.setDatabaseName(self.db_path)
        if not db.open():
            QMessageBox.critical(
                None,
                "Database Error",
                f"Could not open database:\n{db.lastError().text()}"
            )
            return None
        return db

    def create_project_table(self, db: QSqlDatabase) -> bool:
        """
        Creates the 'projects' table if it doesn't already exist.
        """
        query = QSqlQuery(db)
        sql = """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            path TEXT NOT NULL UNIQUE,
            progress_json TEXT,
            description TEXT,
            logstate TEXT
        )
        """
        if not query.exec(sql):
            QMessageBox.critical(
                None,
                "Database Error",
                f"Failed to create table:\n{query.lastError().text()}"
            )
            return False
        return True

    def insert_or_update_project(
        self,
        db: QSqlDatabase,
        name: str,
        path: str,
        progress_dict: dict,
        description: str = "",
        logstate: str = "HIGH"
    ) -> bool:
        """
        Inserts a new project row or updates an existing one (matching on path).
        """
        progress_json = json.dumps(progress_dict)

        # Try to update existing
        upd = QSqlQuery(db)
        upd.prepare("""
            UPDATE projects
               SET name = :name,
                   progress_json = :progress_json,
                   description = :description,
                   logstate = :logstate
             WHERE path = :path
        """)
        upd.bindValue(":name", name)
        upd.bindValue(":progress_json", progress_json)
        upd.bindValue(":description", description)
        upd.bindValue(":path", path)
        upd.bindValue(":logstate", logstate)

        if not upd.exec():
            # fallback to insert
            print("UPDATE failed:", upd.lastError().text())
        elif upd.numRowsAffected() > 0:
            return True

        # Insert new
        ins = QSqlQuery(db)
        ins.prepare("""
            INSERT INTO projects (name, path, progress_json, description)
            VALUES (:name, :path, :progress_json, :description)
        """)
        ins.bindValue(":name", name)
        ins.bindValue(":path", path)
        ins.bindValue(":progress_json", progress_json)
        ins.bindValue(":description", description)

        if not ins.exec():
            QMessageBox.critical(
                None,
                "Database Error",
                f"Failed to insert project:\n{ins.lastError().text()}"
            )
            return False

        return True

    def read_project_progress(self, db: QSqlDatabase, project_path: str) -> dict | None:
        """
        Reads the `progress_json` for the given path and returns it as a dict.
        """
        query = QSqlQuery(db)
        query.prepare("SELECT progress_json FROM projects WHERE path = :path")
        query.bindValue(":path", project_path)
        if not query.exec():
            print("DB Error:", query.lastError().text())
            return None

        if query.next():
            raw = query.value(0)
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                print(f"Invalid JSON for project at {project_path}")
                return None

        print(f"No project found at path: {project_path}")
        return None
    #writes only the item of interest
    def update_project_progress(self, db: QSqlDatabase, path: str, progress_dict: dict) -> bool:
        """
        Updates only the progress_json column for the project with the given path.
        """
        progress_json = json.dumps(progress_dict)

        query = QSqlQuery(db)
        query.prepare("""
            UPDATE projects
               SET progress_json = :progress_json
             WHERE path = :path
        """)
        query.bindValue(":progress_json", progress_json)
        query.bindValue(":path", path)

        if not query.exec():
            QMessageBox.critical(
                None,
                "Database Error",
                f"Failed to update project progress:\n{query.lastError().text()}"
            )
            return False

        # Optionally check if any row was actually affected:
        if query.numRowsAffected() == 0:
            QMessageBox.warning(
                None,
                "Database Warning",
                f"No project found at path: {path}"
            )
            return False

        return True

    def close_db(self, db: QSqlDatabase):
        """
        Closes and removes the named QSQLITE connection.
        """
        if db and db.isOpen():
            name = db.connectionName()
            db.close()
            QSqlDatabase.removeDatabase(name)

# --- Main Window --------------------------------------------------------

class MainWindow(QMainWindow):
    def __init__(self, db_file: str):
        super().__init__()
        self.setWindowTitle("KPM Project Manager")

        # Initialize and open the database
        self.kpm_db = KpmDatabase(db_file)
        self.db = self.kpm_db.open_sqlite_database()
        if not self.db:
            sys.exit(1)

        # Create table if needed
        if not self.kpm_db.create_project_table(self.db):
            sys.exit(1)

        QMessageBox.information(None, "Database", "Database is ready.")

        # Example usage
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
        }
        project_name = "MyProject3"
        project_path = r"C:\Users\user\Documents\KiCad\KPM_PROJECTS\ONE2"
        description = "Initial import."

        # Insert or update row
        ok = self.kpm_db.insert_or_update_project(
            self.db, project_name, project_path, default_states, description
        )
        if not ok:
            sys.exit(1)

        # Read it back
        progress = self.kpm_db.read_project_progress(self.db, project_path)
        QMessageBox.information(None, "Loaded Progress", str(progress))

    def closeEvent(self, event):
        # Clean up on exit
        self.kpm_db.close_db(self.db)
        super().closeEvent(event)

# --- Application Entry Point -------------------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setOrganizationName("KPM")
    app.setApplicationName("KPM")

    # Determine where to store the DB file
    data_dir = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
    os.makedirs(data_dir, exist_ok=True)
    db_file = os.path.join(data_dir, "kpm_projects.db")

    window = MainWindow(db_file)
    window.show()
    sys.exit(app.exec())

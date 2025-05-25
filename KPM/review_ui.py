# from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser, QCheckBox, QLabel
# from PySide6.QtCore import Qt, QUrl
# import os
# import sys

# class ReviewHTMLViewerWidget(QWidget):
#     def __init__(self, html_file_path, project_manager, parent=None):
#         super().__init__(parent)
#         self.html_file_path = html_file_path
#         self.init_ui()
#         self.project_manager = project_manager

#     def on_checked_cb(self, state):
#         checked = state == Qt.Checked
#         print(f"Checkbox checked: {checked}")
#         if checked:
#             self.project_manager.default_states["Reviewed"] = True
        
#         print(self.project_manager.default_states)

#     def init_ui(self):
#         layout = QVBoxLayout(self)
#         ReviewTitle = QLabel("You Have to review the project manually.\n Click Link to hire a reiewer. \n AI review to be added shortl")
#         self.reviewed_cb = QCheckBox("Project has Been reviewed")
#         self.reviewed_cb.stateChanged.connect(self.on_checked_cb)
        
#         self.text_browser = QTextBrowser()

#         layout.addWidget(ReviewTitle)
#         layout.addWidget(self.text_browser)
#         layout.addWidget(self.reviewed_cb)

#         if os.path.exists(self.html_file_path):
#             url = QUrl.fromLocalFile(os.path.abspath(self.html_file_path))
#             self.text_browser.setSource(url)
#         else:
#             self.text_browser.setHtml(f"<h3>File not found:</h3><p>{self.html_file_path}</p>")

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextBrowser, QCheckBox, QLabel
from PySide6.QtCore import QUrl, Qt
import os

class ReviewHTMLViewerWidget(QWidget):
    def __init__(self, html_file_path, project_manager, parent=None):
        super().__init__(parent)
        self.html_file_path = html_file_path
        self.project_manager = project_manager  # store the reference ONCE
        self.init_ui()

    def on_checked_cb(self, state):
        checked = state == Qt.Checked
        print(f"Checkbox checked: {checked}")  # Debug print
        # self.project_manager.default_states["Reviewed"] = checked
        self.project_manager.project_progress_status.emit(self.project_manager.default_states)

    def init_ui(self):
        layout = QVBoxLayout(self)

        review_title = QLabel(
            "You have to review the project manually.\nClick link to hire a reviewer.\nAI review to be added shortly."
        )

        self.reviewed_cb = QCheckBox("Project has been reviewed")
        self.reviewed_cb.stateChanged.connect(self.on_checked_cb)

        self.text_browser = QTextBrowser()

        layout.addWidget(review_title)
        layout.addWidget(self.text_browser)
        layout.addWidget(self.reviewed_cb)

        if os.path.exists(self.html_file_path):
            url = QUrl.fromLocalFile(os.path.abspath(self.html_file_path))
            self.text_browser.setSource(url)
        else:
            self.text_browser.setHtml(f"<h3>File not found:</h3><p>{self.html_file_path}</p>")

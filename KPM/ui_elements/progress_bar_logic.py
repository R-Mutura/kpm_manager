#progress_bar_logic.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt

class ProjectProgressWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)

        # Title
        self.progress_label = QLabel("Progress: 0%")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.progress_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.progress_bar)

        # List of steps
        self.step_list = QListWidget()
        # self.layout.addWidget(self.step_list)

        self.setLayout(self.layout)

    def updateProjectProgress(self, progress_dict: dict):
        total = len(progress_dict)
        done = sum(1 for value in progress_dict.values() if value)

        percent = int((done / total) * 100)
        self.progress_bar.setValue(percent)
        self.progress_label.setText(f"Progress: {percent}%")

        self.step_list.clear()
        for key, value in progress_dict.items():
            item_text = f"{key}: {'✅' if value else '❌'}"
            item = QListWidgetItem(item_text)
            if value:
                item.setForeground(Qt.green)
            else:
                item.setForeground(Qt.red)
            self.step_list.addItem(item)

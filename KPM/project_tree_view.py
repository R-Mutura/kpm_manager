from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel
)
import os

class ProjectFileTreeWidget(QWidget):
    def __init__(self, project_path=None, parent=None):
        super().__init__(parent)
        self.project_path = project_path
        self.setWindowTitle("Project File Tree")
        # self.setMinimumSize(400, 600)

        layout = QVBoxLayout(self)

        
        self.label = QLabel("Project Root: Not loaded")
        layout.addWidget(self.label)


        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Name"])
        layout.addWidget(self.tree_widget)

        # self.populate_tree(self.project_path, self.tree_widget.invisibleRootItem())
        if self.project_path:
            self.load_project(self.project_path)
            
    def load_project(self, path):
        """ Call this when you're ready to populate the tree """
        self.project_path = path
        self.label.setText(f"Project Root: {self.project_path}")
        self.tree_widget.clear()
        self.populate_tree(self.project_path, self.tree_widget.invisibleRootItem())
        
          
    def populate_tree(self, folder_path, parent_item):
        try:
            for item in sorted(os.listdir(folder_path)):
                item_path = os.path.join(folder_path, item)
                tree_item = QTreeWidgetItem([item])
                parent_item.addChild(tree_item)

                if os.path.isdir(item_path):
                    self.populate_tree(item_path, tree_item)
        except PermissionError:
            # Skip folders we can't access
            pass


# Usage example (within another PySide6 window, or for testing)
if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    project_path = os.path.abspath(".")  # Current directory or specify path
    widget = ProjectFileTreeWidget(project_path)
    widget.show()
    sys.exit(app.exec())
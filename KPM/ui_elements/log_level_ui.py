from PySide6.QtWidgets import QApplication, QWidget, QComboBox, QVBoxLayout, QLabel


from .loglevel_logic import CustomLogger
# Get the singleton instance
log_manager = CustomLogger()

class LogLevelWidget(QWidget):
    
    def __init__(self):
        
        super().__init__()

        self.setWindowTitle("Set Log Level")

        # Create a combo box
        self.combo = QComboBox()

        # Add items to the combo box
        self.combo.addItems(["High", "Medium", "Low", "Dont_care"])
        self.combo.setStyleSheet("""
            QComboBox {
                font-size: 10pt;
                padding: 4px;
                border: 1px solid gray;
                border-radius: 5px;
            }
            QComboBox QAbstractItemView {
                font-size: 10pt;
                selection-background-color: lightgray;
            }
        """)
        self.label = QLabel("Select priority")
        self.label.setStyleSheet("font-size: 10pt;")
        
        # Label to show the selected item
        self.label = QLabel("High")

        # Connect the combo box signal to a slot method
        self.combo.currentTextChanged.connect(self.on_selection_changed)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.combo)
        layout.addWidget(self.label)

        self.setLayout(layout)

    def on_selection_changed(self, text):
        self.label.setText(f"Selected: {text}")
        CustomLogger().set_log_level(text)
        
        current_level = log_manager.get_log_level()
        print(f"Current Log Level: {current_level}")  
        
        #put in db his state
        
        # Logging messages
        log = log_manager.get_logger()
        log.info("Something informative")
        log.error("Something went wrong")  

if __name__ == "__main__":
    app = QApplication([])
    window = LogLevelWidget()
    window.show()
    app.exec()

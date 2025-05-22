import logging
import sys

class CustomLogger:
    _instance = None
    _initialized = False

    # Custom levels mapped to standard logging levels
    _custom_level_map = {
        "High": logging.CRITICAL,     # 50
        "Medium": logging.ERROR,      # 40
        "Low": logging.WARNING,       # 30
        "Don't Care": logging.NOTSET  # 0
    }

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CustomLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self, log_file=None):
        if self._initialized:
            return

        self._initialized = True
        self._current_level = "Medium"  # Default level

        # Set up logger
        self.logger = logging.getLogger("AppLogger")
        self.logger.setLevel(self._custom_level_map[self._current_level])
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # Clear previous handlers
        if self.logger.hasHandlers():
            self.logger.handlers.clear()

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File Handler (optional)
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def set_log_level(self, level_str: str):
        """Set custom log level based on UI selection."""
        if level_str in self._custom_level_map:
            self._current_level = level_str
            std_level = self._custom_level_map[level_str]
            self.logger.setLevel(std_level)
            for handler in self.logger.handlers:
                handler.setLevel(std_level)
            self.logger.info(f"Log level set to {level_str}")
        else:
            self.logger.warning(f"Unknown log level: {level_str}")

    def get_log_level(self) -> str:
        """Return the current custom log level."""
        return self._current_level

    def get_logger(self):
        """Get the standard logger instance."""
        return self.logger
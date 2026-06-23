"""
Real-time logs tab for WeeWX service monitoring.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QCheckBox, 
    QPushButton, QLabel, QComboBox
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QTextCursor
import subprocess


class LogTailerThread(QThread):
    """Thread to tail WeeWX logs."""
    
    log_line = Signal(str)
    
    def __init__(self, filter_text=""):
        super().__init__()
        self.filter_text = filter_text
        self.running = True
    
    def run(self):
        """Run log tailer."""
        try:
            process = subprocess.Popen(
                ["sudo", "-n", "journalctl", "-u", "weewx", "-f"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            for line in process.stdout:
                if not self.running:
                    break
                
                if self.filter_text.lower() in line.lower():
                    self.log_line.emit(line.strip())
        
        except Exception as e:
            self.log_line.emit(f"Error: {e}")
    
    def stop(self):
        """Stop the tailer."""
        self.running = False


class LogsTab(QWidget):
    """Real-time logs tab."""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.log_tailer = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        
        controls_layout.addWidget(QLabel("Filter:"))
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "All",
            "Errors",
            "Wunderground",
            "Driver",
            "Archive",
            "INFO",
            "DEBUG",
        ])
        self.filter_combo.currentIndexChanged.connect(self.restart_tailer)
        controls_layout.addWidget(self.filter_combo)
        
        controls_layout.addStretch()
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_logs)
        controls_layout.addWidget(clear_btn)
        
        layout.addLayout(controls_layout)
        
        # Logs display
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setFont(QFont("Courier", 9))
        self.logs_text.setStyleSheet("background-color: #1e1e1e; color: #00ff00;")
        layout.addWidget(self.logs_text)
        
        self.setLayout(layout)
        
        # Start log tailer
        self.restart_tailer()
    
    def get_filter_text(self):
        """Get current filter text."""
        filter_type = self.filter_combo.currentText()
        
        filters = {
            "All": "",
            "Errors": "ERROR",
            "Wunderground": "Wunderground",
            "Driver": "driver",
            "Archive": "archive",
            "INFO": "INFO",
            "DEBUG": "DEBUG",
        }
        
        return filters.get(filter_type, "")
    
    def restart_tailer(self):
        """Restart the log tailer with new filter."""
        if self.log_tailer:
            self.log_tailer.stop()
            self.log_tailer.wait()
        
        filter_text = self.get_filter_text()
        self.log_tailer = LogTailerThread(filter_text)
        self.log_tailer.log_line.connect(self.append_log)
        self.log_tailer.start()
    
    def append_log(self, line):
        """Append a log line."""
        scroll_bar = self.logs_text.verticalScrollBar()
        previous_scroll = scroll_bar.value()
        was_at_bottom = previous_scroll >= max(0, scroll_bar.maximum() - 4)

        cursor = self.logs_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.logs_text.setTextCursor(cursor)
        
        self.logs_text.insertPlainText(line + "\n")
        
        # Keep only last 500 lines for performance
        doc = self.logs_text.document()
        while doc.blockCount() > 500:
            trim_cursor = QTextCursor(doc.firstBlock())
            trim_cursor.select(QTextCursor.BlockUnderCursor)
            trim_cursor.removeSelectedText()
            trim_cursor.deleteChar()

        if was_at_bottom:
            scroll_bar.setValue(scroll_bar.maximum())
        else:
            scroll_bar.setValue(min(previous_scroll, scroll_bar.maximum()))
    
    def clear_logs(self):
        """Clear logs display."""
        self.logs_text.clear()
    
    def closeEvent(self, event):
        """Clean up on close."""
        if self.log_tailer:
            self.log_tailer.stop()
        super().closeEvent(event)

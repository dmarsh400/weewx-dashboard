"""
Setup tab for configuring WeeWX and Weather Underground settings.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QGroupBox, QFormLayout, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from pathlib import Path
import subprocess


class SetupTab(QWidget):
    """Setup configuration tab."""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # WeeWX Configuration Group
        weewx_group = QGroupBox("WeeWX Configuration")
        weewx_layout = QFormLayout()
        
        self.weewx_root_input = QLineEdit()
        self.weewx_root_input.setText(self.config.get("weewx_root", "/etc/weewx"))
        weewx_layout.addRow("WeeWX Root:", self.weewx_root_input)
        
        self.weewx_conf_input = QLineEdit()
        self.weewx_conf_input.setText(self.config.get("weewx_conf", "/etc/weewx/weewx.conf"))
        weewx_layout.addRow("Config File:", self.weewx_conf_input)
        
        self.weewx_db_input = QLineEdit()
        self.weewx_db_input.setText(self.config.get("weewx_db", "/var/lib/weewx/weewx.sdb"))
        weewx_layout.addRow("Database:", self.weewx_db_input)
        
        # Browse buttons
        browse_layout = QHBoxLayout()
        browse_conf_btn = QPushButton("Browse Config")
        browse_conf_btn.clicked.connect(self.browse_weewx_conf)
        browse_db_btn = QPushButton("Browse Database")
        browse_db_btn.clicked.connect(self.browse_weewx_db)
        browse_layout.addWidget(browse_conf_btn)
        browse_layout.addWidget(browse_db_btn)
        weewx_layout.addRow("Browse:", browse_layout)
        
        weewx_group.setLayout(weewx_layout)
        layout.addWidget(weewx_group)
        
        # Weather Underground Configuration Group
        wu_group = QGroupBox("Weather Underground")
        wu_layout = QFormLayout()
        
        self.wu_station_input = QLineEdit()
        self.wu_station_input.setPlaceholderText("e.g., KXXXXXXX")
        self.wu_station_input.setText(self.config.get("wu_station_id", ""))
        wu_layout.addRow("Station ID:", self.wu_station_input)
        
        self.wu_api_input = QLineEdit()
        self.wu_api_input.setPlaceholderText("Your Weather Underground API key")
        self.wu_api_input.setEchoMode(QLineEdit.Password)
        self.wu_api_input.setText(self.config.get("wu_api_key", ""))
        wu_layout.addRow("API Key:", self.wu_api_input)
        
        wu_group.setLayout(wu_layout)
        layout.addWidget(wu_group)
        
        # System Status Group
        status_group = QGroupBox("System Status")
        status_layout = QVBoxLayout()
        
        self.status_label = QLabel("Click 'Check Status' to verify connections.")
        status_layout.addWidget(self.status_label)
        
        check_btn = QPushButton("Check Status")
        check_btn.clicked.connect(self.check_status)
        status_layout.addWidget(check_btn)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Save button
        save_btn = QPushButton("Save Configuration")
        save_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px; font-weight: bold;")
        save_btn.clicked.connect(self.save_config)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def browse_weewx_conf(self):
        """Browse for WeeWX config file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select WeeWX Config File", "/etc/weewx/", "Config Files (weewx.conf)"
        )
        if file_path:
            self.weewx_conf_input.setText(file_path)
    
    def browse_weewx_db(self):
        """Browse for WeeWX database file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select WeeWX Database", "/etc/weewx/", "Database Files (*.sdb)"
        )
        if file_path:
            self.weewx_db_input.setText(file_path)
    
    def check_status(self):
        """Check system status."""
        status_lines = []
        
        # Check files
        conf_path = Path(self.weewx_conf_input.text())
        db_path = Path(self.weewx_db_input.text())
        
        status_lines.append(f"Config file: {'✓' if conf_path.exists() else '✗'} {conf_path}")
        status_lines.append(f"Database file: {'✓' if db_path.exists() else '✗'} {db_path}")
        
        # Check WeeWX service
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "weewx"],
                capture_output=True, text=True, timeout=5
            )
            weewx_status = "✓ Running" if result.returncode == 0 else "✗ Not running"
        except Exception as e:
            weewx_status = f"✗ Error: {e}"
        
        status_lines.append(f"WeeWX service: {weewx_status}")
        
        self.status_label.setText("\n".join(status_lines))
    
    def save_config(self):
        """Save configuration."""
        self.config.set("weewx_root", self.weewx_root_input.text())
        self.config.set("weewx_conf", self.weewx_conf_input.text())
        self.config.set("weewx_db", self.weewx_db_input.text())
        self.config.set("wu_station_id", self.wu_station_input.text())
        self.config.set("wu_api_key", self.wu_api_input.text())
        
        QMessageBox.information(self, "Success", "Configuration saved successfully!")

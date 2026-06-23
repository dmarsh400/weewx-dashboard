#!/usr/bin/env python3
"""
WeeWX Dashboard - Cross-platform GUI for WeeWX monitoring and Weather Underground uploads.
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QScrollArea,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon

from tabs.setup import SetupTab
from tabs.monitor import MonitorTab
from tabs.history import HistoryTab
from tabs.publish_status import PublishStatusTab
from tabs.logs import LogsTab
from config import Config


class WeeWXDashboard(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.setWindowTitle("WeeWX Dashboard")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet(
            """
            QMainWindow {
                background: #0b1220;
            }
            QWidget {
                color: #d7e2f2;
                background: #0b1220;
            }
            QTabWidget::pane {
                border: 1px solid #223047;
                background: #0f1a2b;
            }
            QTabBar::tab {
                background: #132238;
                color: #9bb4d1;
                border: 1px solid #223047;
                border-bottom: none;
                padding: 8px 12px;
                min-width: 110px;
            }
            QTabBar::tab:selected {
                background: #1c3659;
                color: #ffffff;
            }
            QGroupBox {
                border: 1px solid #223047;
                border-radius: 8px;
                margin-top: 8px;
                font-weight: 700;
                color: #b8cbe5;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px 0 4px;
            }
            QLineEdit, QComboBox, QTextEdit {
                background: #101a2b;
                border: 1px solid #2c3f5a;
                border-radius: 6px;
                padding: 4px;
                color: #d7e2f2;
            }
            QPushButton {
                background: #245a9f;
                color: #ffffff;
                border: 1px solid #2f6fbf;
                border-radius: 7px;
                padding: 6px 10px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: #2f6fbf;
            }
            QScrollBar:vertical {
                background: #101a2b;
                width: 14px;
                margin: 0;
            }
            QScrollBar::handle:vertical {
                background: #365177;
                min-height: 22px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: #1a2a42;
                height: 14px;
            }
            QScrollBar:horizontal {
                background: #101a2b;
                height: 14px;
                margin: 0;
            }
            QScrollBar::handle:horizontal {
                background: #365177;
                min-width: 22px;
                border-radius: 6px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                background: #1a2a42;
                width: 14px;
            }
            """
        )
        
        # Set icon if available
        icon_path = Path(__file__).parent / "assets" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Create central widget with tabs
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
        
        # Initialize tabs
        self.setup_tab = SetupTab(self.config)
        self.monitor_tab = MonitorTab(self.config)
        self.history_tab = HistoryTab(self.config)
        self.publish_tab = PublishStatusTab(self.config)
        self.logs_tab = LogsTab(self.config)
        
        self.tab_widget.addTab(self._make_scrollable_tab(self.setup_tab), "Setup")
        self.tab_widget.addTab(self._make_scrollable_tab(self.monitor_tab), "Live Monitor")
        self.tab_widget.addTab(self._make_scrollable_tab(self.history_tab), "History")
        self.tab_widget.addTab(self._make_scrollable_tab(self.publish_tab), "Publish Status")
        self.tab_widget.addTab(self._make_scrollable_tab(self.logs_tab), "Logs")
        
        # Timer to refresh live data
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_tabs)
        self.refresh_timer.start(1000)  # Refresh every 1 second

    def _make_scrollable_tab(self, tab_widget):
        """Wrap a tab widget in a scroll area for mouse-wheel and scrollbar support."""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setWidget(tab_widget)
        return scroll_area
        
    def refresh_tabs(self):
        """Refresh active tab data."""
        active_tab = self.tab_widget.currentWidget()
        if hasattr(active_tab, 'refresh'):
            active_tab.refresh()
            return

        # Active tab is wrapped in a QScrollArea.
        inner_tab = active_tab.widget() if hasattr(active_tab, 'widget') else None
        if inner_tab is not None and hasattr(inner_tab, 'refresh'):
            inner_tab.refresh()


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    
    dashboard = WeeWXDashboard()
    dashboard.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

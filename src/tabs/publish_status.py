"""
Weather Underground publish status tab.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QFormLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QApplication,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont
import subprocess
from datetime import datetime, timedelta


class PublishStatusTab(QWidget):
    """Weather Underground upload status tab."""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.auto_refresh_interval = 30
        self.seconds_until_refresh = self.auto_refresh_interval
        self.init_ui()
        self.auto_timer = QTimer(self)
        self.auto_timer.setInterval(1000)
        self.auto_timer.timeout.connect(self._on_auto_refresh_tick)
        self.auto_timer.start()
        self.manual_refresh()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()

        self.alert_banner = QLabel("No active Weather Underground alerts.")
        self.alert_banner.setStyleSheet(
            "background: #e8f5e9; color: #1b5e20; border: 1px solid #a5d6a7; "
            "border-radius: 8px; padding: 8px; font-weight: 700;"
        )
        layout.addWidget(self.alert_banner)
        
        # Status Group
        status_group = QGroupBox("Upload Status")
        status_layout = QFormLayout()
        
        self.station_label = QLabel(self.config.get("wu_station_id", "Not configured"))
        status_layout.addRow("Station ID:", self.station_label)
        
        self.last_upload_label = QLabel("--")
        status_layout.addRow("Last Upload:", self.last_upload_label)
        
        self.upload_status_label = QLabel("--")
        status_layout.addRow("Status:", self.upload_status_label)

        self.consecutive_failures_label = QLabel("0")
        status_layout.addRow("Consecutive Failures:", self.consecutive_failures_label)
        
        self.error_count_label = QLabel("0")
        status_layout.addRow("Recent Errors:", self.error_count_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # Service Controls
        control_group = QGroupBox("WeeWX Service Controls")
        control_layout = QVBoxLayout()
        btn_row = QHBoxLayout()

        start_btn = QPushButton("Start")
        start_btn.clicked.connect(lambda: self.run_service_action("start"))
        btn_row.addWidget(start_btn)

        stop_btn = QPushButton("Stop")
        stop_btn.clicked.connect(lambda: self.run_service_action("stop"))
        btn_row.addWidget(stop_btn)

        restart_btn = QPushButton("Restart")
        restart_btn.clicked.connect(lambda: self.run_service_action("restart"))
        btn_row.addWidget(restart_btn)

        control_layout.addLayout(btn_row)
        self.control_hint_label = QLabel("Tip: actions may prompt for admin authentication.")
        self.control_hint_label.setStyleSheet("color: #9bb4d1;")
        control_layout.addWidget(self.control_hint_label)

        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # Diagnostics Group
        diag_group = QGroupBox("Troubleshooting")
        diag_layout = QVBoxLayout()

        self.diag_text = QTextEdit()
        self.diag_text.setReadOnly(True)
        self.diag_text.setFont(QFont("Courier", 9))
        self.diag_text.setMaximumHeight(190)
        diag_layout.addWidget(self.diag_text)

        diag_btn_layout = QHBoxLayout()
        run_diag_btn = QPushButton("Run Diagnostics")
        run_diag_btn.clicked.connect(self.run_diagnostics)
        diag_btn_layout.addWidget(run_diag_btn)

        copy_fix_btn = QPushButton("Copy Suggested Fix Commands")
        copy_fix_btn.clicked.connect(self.copy_fix_commands)
        diag_btn_layout.addWidget(copy_fix_btn)
        diag_layout.addLayout(diag_btn_layout)

        diag_group.setLayout(diag_layout)
        layout.addWidget(diag_group)
        
        # Recent Logs Group
        logs_group = QGroupBox("Recent Upload Activity")
        logs_layout = QVBoxLayout()
        
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setFont(QFont("Courier", 9))
        self.logs_text.setMaximumHeight(300)
        logs_layout.addWidget(self.logs_text)
        
        logs_group.setLayout(logs_layout)
        layout.addWidget(logs_group)
        
        # Refresh button
        refresh_row = QHBoxLayout()
        refresh_btn = QPushButton("Refresh Status")
        refresh_btn.clicked.connect(self.manual_refresh)
        refresh_row.addWidget(refresh_btn)

        self.auto_refresh_label = QLabel("")
        self.auto_refresh_label.setStyleSheet("color: #9bb4d1; font-weight: 600;")
        refresh_row.addWidget(self.auto_refresh_label)
        refresh_row.addStretch()
        layout.addLayout(refresh_row)
        
        layout.addStretch()
        self.setLayout(layout)
        self.suggested_commands = []
        self.last_wu_lines = []
    
    def refresh(self):
        """Lightweight refresh hook used by the main tab refresher."""
        self._update_auto_refresh_label()

    def manual_refresh(self):
        """Refresh upload status immediately and reset countdown."""
        self.station_label.setText(self.config.get("wu_station_id", "Not configured"))
        self.get_upload_logs()
        self.check_upload_status()
        self.run_diagnostics()
        self.seconds_until_refresh = self.auto_refresh_interval
        self._update_auto_refresh_label()

    def _on_auto_refresh_tick(self):
        """Tick countdown and perform automatic periodic refresh."""
        self.seconds_until_refresh -= 1
        if self.seconds_until_refresh <= 0:
            self.manual_refresh()
        else:
            self._update_auto_refresh_label()

    def _update_auto_refresh_label(self):
        """Update auto-refresh countdown label."""
        self.auto_refresh_label.setText(f"Auto-refresh in {self.seconds_until_refresh}s")

    def _parse_journal_line_time(self, line):
        """Parse journal timestamp prefix like 'Jun 22 13:25:20'."""
        try:
            parts = line.split()
            if len(parts) < 3:
                return None
            prefix = " ".join(parts[:3])
            parsed = datetime.strptime(prefix, "%b %d %H:%M:%S")
            return parsed.replace(year=datetime.now().year)
        except Exception:
            return None

    def _get_consecutive_failures(self, wu_lines):
        """Count failures since the last published record."""
        count = 0
        for line in reversed(wu_lines):
            lowered = line.lower()
            if "published record" in lowered or "posted" in lowered:
                break
            if "failed to publish" in lowered:
                count += 1
        return count
    
    def get_upload_logs(self):
        """Get recent upload logs from WeeWX."""
        try:
            scroll_bar = self.logs_text.verticalScrollBar()
            previous_scroll = scroll_bar.value()
            was_at_bottom = previous_scroll >= max(0, scroll_bar.maximum() - 4)

            result = subprocess.run(
                ["journalctl", "-u", "weewx", "-n", "120", "--no-pager"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # Fallback for systems where journal access requires elevation.
            if result.returncode != 0 or not result.stdout.strip():
                result = subprocess.run(
                    ["sudo", "-n", "journalctl", "-u", "weewx", "-n", "120", "--no-pager"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

            if result.returncode != 0:
                self.logs_text.setText(
                    "Could not read WeeWX logs for upload status.\n\n"
                    "Try running this once in terminal to verify access:\n"
                    "journalctl -u weewx -n 30 --no-pager"
                )
                self.upload_status_label.setText("⚠ Log access unavailable")
                self.upload_status_label.setStyleSheet("color: orange; font-weight: bold;")
                self.last_upload_label.setText("Unknown")
                self.error_count_label.setText("0")
                self.consecutive_failures_label.setText("0")
                self.last_wu_lines = []
                return
            
            # Filter for Wunderground lines
            lines = result.stdout.split('\n')
            wu_lines = [
                l for l in lines
                if 'Wunderground-PWS' in l or 'wunderground-pws' in l
            ]
            self.last_wu_lines = wu_lines
            
            log_text = '\n'.join(wu_lines[-20:])  # Last 20 relevant lines
            self.logs_text.setPlainText(log_text)

            # Keep tail-follow behavior if user is already at bottom.
            if was_at_bottom:
                scroll_bar.setValue(scroll_bar.maximum())
            else:
                scroll_bar.setValue(min(previous_scroll, scroll_bar.maximum()))
            
            # Count errors
            error_count = sum(1 for l in wu_lines if 'error' in l.lower() or 'failed' in l.lower())
            self.error_count_label.setText(str(error_count))

            consecutive_failures = self._get_consecutive_failures(wu_lines)
            self.consecutive_failures_label.setText(str(consecutive_failures))
            if consecutive_failures >= 3:
                self.alert_banner.setText(
                    "ALERT: Weather Underground has 3+ consecutive publish failures. "
                    "Run diagnostics below."
                )
                self.alert_banner.setStyleSheet(
                    "background: #ffebee; color: #b71c1c; border: 1px solid #ef9a9a; "
                    "border-radius: 8px; padding: 8px; font-weight: 700;"
                )
            elif consecutive_failures > 0:
                self.alert_banner.setText(
                    f"Warning: {consecutive_failures} consecutive publish failure(s)."
                )
                self.alert_banner.setStyleSheet(
                    "background: #fff8e1; color: #8d6e00; border: 1px solid #ffe082; "
                    "border-radius: 8px; padding: 8px; font-weight: 700;"
                )
            else:
                self.alert_banner.setText("No active Weather Underground alerts.")
                self.alert_banner.setStyleSheet(
                    "background: #e8f5e9; color: #1b5e20; border: 1px solid #a5d6a7; "
                    "border-radius: 8px; padding: 8px; font-weight: 700;"
                )
            
            # Extract last upload time
            last_success_line = None
            for line in reversed(wu_lines):
                if 'Published' in line or 'posted' in line.lower():
                    last_success_line = line
                    parsed_time = self._parse_journal_line_time(line)
                    if parsed_time is not None:
                        age_min = int((datetime.now() - parsed_time).total_seconds() // 60)
                        self.last_upload_label.setText(
                            f"{parsed_time.strftime('%b %d %H:%M:%S')} ({age_min} min ago)"
                        )
                    else:
                        self.last_upload_label.setText("Recently")
                    self.upload_status_label.setText("✓ Success")
                    self.upload_status_label.setStyleSheet("color: green; font-weight: bold;")
                    break
            else:
                # No successful upload found in logs
                if wu_lines:
                    self.upload_status_label.setText("✗ No successful uploads in recent logs")
                else:
                    self.upload_status_label.setText("⚠ No Wunderground log entries found")
                self.upload_status_label.setStyleSheet("color: red; font-weight: bold;")
                self.last_upload_label.setText("Unknown")

            # If last success exists but failures are more recent, make status amber.
            if last_success_line is not None and consecutive_failures > 0:
                self.upload_status_label.setText("⚠ Recent failures after last success")
                self.upload_status_label.setStyleSheet("color: orange; font-weight: bold;")
        
        except Exception as e:
            self.logs_text.setText(f"Error reading logs: {e}\n\nMake sure this is run with sudo or weewx logs are readable.")
    
    def check_upload_status(self):
        """Check overall upload status."""
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "weewx"],
                capture_output=True, text=True, timeout=5
            )
            
            state = (result.stdout or "").strip().lower()
            if state != "active":
                self.upload_status_label.setText("⚠ WeeWX service not running")
                self.upload_status_label.setStyleSheet("color: orange; font-weight: bold;")
        
        except Exception as e:
            print(f"Error checking service: {e}")

    def run_diagnostics(self):
        """Run lightweight diagnostics and suggest targeted fixes."""
        issues = []
        self.suggested_commands = []

        # WeeWX service check
        try:
            svc = subprocess.run(
                ["systemctl", "is-active", "weewx"],
                capture_output=True, text=True, timeout=5
            )
            if (svc.stdout or "").strip().lower() != "active":
                issues.append("- WeeWX service is not active.")
                self.suggested_commands.append("sudo systemctl restart weewx")
        except Exception as e:
            issues.append(f"- Could not check WeeWX service: {e}")

        # WU endpoint check
        try:
            endpoint = subprocess.run(
                [
                    "curl",
                    "-I",
                    "--max-time",
                    "12",
                    "https://rtupdate.wunderground.com/weatherstation/updateweatherstation.php",
                ],
                capture_output=True, text=True, timeout=15
            )
            if "HTTP/" not in endpoint.stdout:
                issues.append("- Could not reach Weather Underground endpoint.")
                self.suggested_commands.append(
                    "curl -I https://rtupdate.wunderground.com/weatherstation/updateweatherstation.php"
                )
        except Exception as e:
            issues.append(f"- Endpoint check failed: {e}")

        # Time sync check
        try:
            ntp = subprocess.run(
                ["timedatectl", "show", "-p", "NTPSynchronized", "--value"],
                capture_output=True, text=True, timeout=5
            )
            if ntp.stdout.strip().lower() != "yes":
                issues.append("- System clock is not synchronized.")
                self.suggested_commands.append("sudo timedatectl set-ntp true")
        except Exception as e:
            issues.append(f"- NTP check failed: {e}")

        # USB presence check
        try:
            usb = subprocess.run(["lsusb"], capture_output=True, text=True, timeout=6)
            if "24c0:0003" not in usb.stdout:
                issues.append("- Acurite USB device (24c0:0003) not detected.")
                self.suggested_commands.append("lsusb | grep 24c0")
                self.suggested_commands.append("sudo systemctl restart weewx")
        except Exception as e:
            issues.append(f"- USB check failed: {e}")

        # Recent publish freshness check
        last_published_time = None
        for line in reversed(self.last_wu_lines):
            if "Published record" in line:
                last_published_time = self._parse_journal_line_time(line)
                break

        if last_published_time is not None:
            if datetime.now() - last_published_time > timedelta(minutes=20):
                issues.append("- No successful WU publish in the last 20 minutes.")
                self.suggested_commands.append(
                    "sudo journalctl -u weewx -f | grep -E 'Wunderground-PWS: (Published|Failed)'"
                )
        else:
            issues.append("- No recent successful WU publish found in logs.")

        if not issues:
            self.diag_text.setText(
                "Diagnostics: OK\n"
                "- WeeWX service is active\n"
                "- WU endpoint is reachable\n"
                "- Clock synchronization is healthy\n"
                "- USB device is present\n"
                "- Recent WU publish detected"
            )
            self.suggested_commands = ["# No fixes needed right now"]
            return

        diag_lines = ["Diagnostics found issues:"]
        diag_lines.extend(issues)
        diag_lines.append("")
        diag_lines.append("Suggested fixes:")
        if self.suggested_commands:
            for cmd in self.suggested_commands:
                diag_lines.append(f"- {cmd}")
        else:
            diag_lines.append("- No automatic fix commands available.")

        self.diag_text.setText("\n".join(diag_lines))

    def copy_fix_commands(self):
        """Copy suggested fix commands to clipboard."""
        commands = self.suggested_commands or ["# No fixes needed right now"]
        QApplication.clipboard().setText("\n".join(commands))

    def run_service_action(self, action):
        """Run start/stop/restart on weewx with desktop auth fallback."""
        cmd = ["systemctl", action, "weewx"]

        # Prefer polkit GUI prompt for desktop apps.
        try:
            result = subprocess.run(["pkexec"] + cmd, capture_output=True, text=True, timeout=20)
            if result.returncode == 0:
                self.control_hint_label.setText(f"Service action succeeded: {' '.join(cmd)}")
                self.refresh()
                return
        except FileNotFoundError:
            pass
        except Exception:
            pass

        # Fallback for environments with NOPASSWD sudo configured.
        try:
            result = subprocess.run(["sudo", "-n"] + cmd, capture_output=True, text=True, timeout=12)
            if result.returncode == 0:
                self.control_hint_label.setText(f"Service action succeeded: {' '.join(cmd)}")
                self.refresh()
                return
        except Exception:
            pass

        self.control_hint_label.setText("Service action needs elevated privileges.")
        QMessageBox.information(
            self,
            "Privilege Required",
            "Could not run service action from the app without admin auth.\n\n"
            f"Run this in terminal:\n\n  sudo {' '.join(cmd)}",
        )

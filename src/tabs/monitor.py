"""
Live monitor tab for real-time WeeWX data.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QGridLayout,
    QLabel,
    QPushButton,
    QFrame,
    QProgressBar,
)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QFont, QPainter, QColor, QPen, QPolygon
from weewx_db import WeeWXDatabase
import subprocess
from datetime import datetime
import math


class MetricCard(QFrame):
    """Compact metric card with value and optional progress gauge."""

    def __init__(self, title, unit="", progress_range=None, accent_color="#1d74d9", badge_text=""):
        super().__init__()
        self.title = title
        self.unit = unit
        self.progress_range = progress_range
        self.accent_color = accent_color
        self.badge_text = badge_text

        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(
            """
            QFrame {
                background: #132238;
                border: 1px solid #2a3d59;
                border-radius: 12px;
            }
            """
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(5)

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("color: #8ea8c6; font-size: 11px; font-weight: 600;")
        top_row.addWidget(self.title_label)

        self.badge_label = QLabel(badge_text)
        self.badge_label.setStyleSheet(
            f"background: {self.accent_color}; color: white; font-size: 9px; font-weight: 700; "
            "padding: 2px 7px; border-radius: 8px;"
        )
        self.badge_label.setVisible(bool(badge_text))
        top_row.addWidget(self.badge_label, alignment=Qt.AlignRight)

        layout.addLayout(top_row)

        self.value_label = QLabel("--")
        self.value_label.setFont(QFont("DejaVu Sans", 24, QFont.Bold))
        self.value_label.setStyleSheet("color: #dce8f8;")

        self.sub_label = QLabel(unit)
        self.sub_label.setStyleSheet("color: #7f97b5; font-size: 10px; text-transform: uppercase;")

        self.trend_label = QLabel("")
        self.trend_label.setStyleSheet("color: #9db3cd; font-size: 10px; font-weight: 700;")

        layout.addWidget(self.value_label)
        layout.addWidget(self.sub_label)
        layout.addWidget(self.trend_label)

        self.progress = None
        if progress_range is not None:
            self.progress = QProgressBar()
            self.progress.setRange(0, 100)
            self.progress.setTextVisible(False)
            self.progress.setFixedHeight(8)
            self.progress.setStyleSheet(
                f"""
                QProgressBar {{
                    background: #0e192a;
                    border: 1px solid #2a3d59;
                    border-radius: 4px;
                }}
                QProgressBar::chunk {{
                    background: {self.accent_color};
                    border-radius: 3px;
                }}
                """
            )
            layout.addWidget(self.progress)

        self.setLayout(layout)

    def set_value(self, value):
        """Set card value and update gauge if configured."""
        if value is None:
            self.value_label.setText("--")
            if self.progress:
                self.progress.setValue(0)
            return

        if isinstance(value, float):
            text_value = f"{value:.1f}"
        else:
            text_value = str(value)

        self.value_label.setText(text_value)

        if self.progress and self.progress_range:
            low, high = self.progress_range
            if high > low:
                pct = int(max(0, min(100, ((float(value) - low) / (high - low)) * 100)))
                self.progress.setValue(pct)

    def set_alert_color(self, color_hex):
        """Colorize value for quick state recognition."""
        self.value_label.setStyleSheet(f"color: {color_hex};")

    def set_trend(self, trend_symbol, trend_text):
        """Set trend indicator text."""
        if trend_symbol:
            self.trend_label.setText(f"{trend_symbol} {trend_text}")
        else:
            self.trend_label.setText("")


class CompassWidget(QFrame):
    """Simple wind direction compass dial."""

    def __init__(self):
        super().__init__()
        self.wind_dir = None
        self.setMinimumSize(170, 170)
        self.setStyleSheet(
            """
            QFrame {
                background: #132238;
                border: 1px solid #2a3d59;
                border-radius: 12px;
            }
            """
        )

    def set_direction(self, degrees):
        """Set wind direction in degrees and repaint."""
        self.wind_dir = degrees
        self.update()

    def paintEvent(self, event):
        """Draw compass dial and direction needle."""
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        cx = w // 2
        cy = h // 2
        radius = min(w, h) // 2 - 18

        painter.setPen(QPen(QColor("#2e4668"), 2))
        painter.setBrush(QColor("#0f1a2b"))
        painter.drawEllipse(cx - radius, cy - radius, radius * 2, radius * 2)

        painter.setPen(QPen(QColor("#9bb4d1"), 1))
        painter.setFont(QFont("DejaVu Sans", 9, QFont.Bold))
        painter.drawText(cx - 6, cy - radius + 14, "N")
        painter.drawText(cx - 5, cy + radius - 6, "S")
        painter.drawText(cx + radius - 12, cy + 4, "E")
        painter.drawText(cx - radius + 4, cy + 4, "W")

        if self.wind_dir is not None:
            ang = math.radians(float(self.wind_dir) - 90)
            tip_x = cx + int(math.cos(ang) * (radius - 12))
            tip_y = cy + int(math.sin(ang) * (radius - 12))

            left_ang = ang + math.radians(150)
            right_ang = ang - math.radians(150)
            base_r = 12
            left_x = cx + int(math.cos(left_ang) * base_r)
            left_y = cy + int(math.sin(left_ang) * base_r)
            right_x = cx + int(math.cos(right_ang) * base_r)
            right_y = cy + int(math.sin(right_ang) * base_r)

            painter.setPen(QPen(QColor("#1d74d9"), 2))
            painter.setBrush(QColor("#1d74d9"))
            painter.drawPolygon(QPolygon([
                QPoint(tip_x, tip_y),
                QPoint(left_x, left_y),
                QPoint(right_x, right_y),
            ]))

            painter.setBrush(QColor("#d7e2f2"))
            painter.setPen(QPen(QColor("#d7e2f2"), 1))
            painter.drawEllipse(cx - 4, cy - 4, 8, 8)

            painter.setPen(QPen(QColor("#9bb4d1"), 1))
            painter.setFont(QFont("DejaVu Sans", 10, QFont.Bold))
            painter.drawText(10, h - 10, f"Wind Dir: {int(self.wind_dir)} deg")


class MonitorTab(QWidget):
    """Live monitoring tab."""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.db = None
        self.init_ui()
        self.refresh()
    
    def init_ui(self):
        """Initialize the UI."""
        self.setStyleSheet(
            """
            MonitorTab {
                background: #0b1220;
            }
            QGroupBox {
                font-weight: 700;
                color: #b8cbe5;
                border: 1px solid #223047;
                border-radius: 12px;
                margin-top: 10px;
                background: #0f1a2b;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px 0 4px;
            }
            QPushButton {
                background: #245a9f;
                color: white;
                border-radius: 8px;
                padding: 7px 12px;
                font-weight: 700;
            }
            QPushButton:hover {
                background: #2f6fbf;
            }
            """
        )

        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Device Status Group
        device_group = QGroupBox("Device Status")
        device_layout = QHBoxLayout()
        
        self.device_status_label = QLabel("Checking device status...")
        self.device_status_label.setTextFormat(Qt.RichText)
        self.device_status_label.setWordWrap(True)
        self.device_status_label.setStyleSheet("font-weight: 600; color: #b8cbe5;")
        device_layout.addWidget(self.device_status_label)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh)
        device_layout.addWidget(refresh_btn)
        
        device_group.setLayout(device_layout)
        layout.addWidget(device_group)

        # Headline tiles
        headline_layout = QHBoxLayout()
        headline_layout.setSpacing(10)

        self.feels_like_card = MetricCard(
            "Feels Like",
            "deg F",
            progress_range=(-10, 115),
            accent_color="#ef4444",
            badge_text="FEELS",
        )
        self.today_rain_card = MetricCard(
            "Today Rain",
            "inches",
            progress_range=(0, 3),
            accent_color="#2563eb",
            badge_text="TODAY",
        )

        headline_layout.addWidget(self.feels_like_card)
        headline_layout.addWidget(self.today_rain_card)
        layout.addLayout(headline_layout)
        
        # Visual dashboard cards
        cards_group = QGroupBox("Live Conditions")
        cards_layout = QGridLayout()
        cards_layout.setHorizontalSpacing(10)
        cards_layout.setVerticalSpacing(10)

        self.out_temp_card = MetricCard("Outdoor Temperature", "deg F", progress_range=(-10, 110), accent_color="#f97316", badge_text="TEMP")
        self.out_hum_card = MetricCard("Outdoor Humidity", "%", progress_range=(0, 100), accent_color="#0ea5e9", badge_text="HUM")
        self.pressure_card = MetricCard("Barometer", "inHg", progress_range=(28, 31), accent_color="#4f46e5", badge_text="PRES")
        self.wind_card = MetricCard("Wind Speed", "mph", progress_range=(0, 60), accent_color="#0f766e", badge_text="WIND")
        self.gust_card = MetricCard("Wind Gust", "mph", progress_range=(0, 80), accent_color="#047857", badge_text="GUST")
        self.rain_rate_card = MetricCard("Rain Rate", "in/hr", progress_range=(0, 3), accent_color="#2563eb", badge_text="RAIN")

        self.wind_compass = CompassWidget()

        cards_layout.addWidget(self.out_temp_card, 0, 0)
        cards_layout.addWidget(self.out_hum_card, 0, 1)
        cards_layout.addWidget(self.pressure_card, 0, 2)
        cards_layout.addWidget(self.wind_card, 1, 0)
        cards_layout.addWidget(self.gust_card, 1, 1)
        cards_layout.addWidget(self.rain_rate_card, 1, 2)
        cards_layout.addWidget(self.wind_compass, 0, 3, 2, 1)

        cards_group.setLayout(cards_layout)
        layout.addWidget(cards_group)

        # Detailed Readings Group
        readings_group = QGroupBox("Detailed Readings")
        readings_layout = QGridLayout()
        readings_layout.setHorizontalSpacing(16)

        self.reading_labels = {}
        readings = [
            ("outTemp", "Outdoor Temp"),
            ("outHumidity", "Outdoor Humidity"),
            ("barometer", "Barometer"),
            ("windSpeed", "Wind Speed"),
            ("windDir", "Wind Direction"),
            ("windGust", "Wind Gust"),
            ("rain", "Rain"),
            ("rainRate", "Rain Rate"),
            ("dewpoint", "Dew Point"),
            ("windchill", "Wind Chill"),
            ("inTemp", "Indoor Temp"),
            ("inHumidity", "Indoor Humidity"),
        ]

        for row, (key, label) in enumerate(readings):
            label_widget = QLabel(label + ":")
            label_widget.setStyleSheet("color: #8ea8c6;")

            value_widget = QLabel("--")
            value_widget.setFont(QFont("DejaVu Sans", 10, QFont.Bold))
            value_widget.setStyleSheet("color: #dce8f8;")

            self.reading_labels[key] = value_widget

            readings_layout.addWidget(label_widget, row, 0)
            readings_layout.addWidget(value_widget, row, 1)

        readings_group.setLayout(readings_layout)
        layout.addWidget(readings_group)
        
        # Timestamp label
        self.timestamp_label = QLabel("Last update: --")
        self.timestamp_label.setStyleSheet("color: #9bb4d1; font-weight: 700;")
        layout.addWidget(self.timestamp_label)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def refresh(self):
        """Refresh live data."""
        self.update_device_status()
        self.update_readings()
    
    def update_device_status(self):
        """Update device connection status."""
        try:
            result = subprocess.run(
                ["lsusb"],
                capture_output=True, text=True, timeout=5
            )

            console_ok = "24c0:0003" in result.stdout
            
            # Check WeeWX service
            result = subprocess.run(
                ["systemctl", "is-active", "weewx"],
                capture_output=True, text=True, timeout=5
            )

            weewx_ok = (result.stdout or "").strip().lower() == "active"

            if console_ok:
                console_html = (
                    "<span style='color:#86efac; font-weight:700;'>● Acurite Console: Connected</span>"
                )
            else:
                console_html = (
                    "<span style='color:#fca5a5; font-weight:700;'>● Acurite Console: Not connected</span>"
                )

            if weewx_ok:
                weewx_html = (
                    "<span style='color:#86efac; font-weight:700;'>● WeeWX: Running</span>"
                )
            else:
                weewx_html = (
                    "<span style='color:#fca5a5; font-weight:700;'>● WeeWX: Stopped</span>"
                )
            
            self.device_status_label.setText(f"{console_html} &nbsp;&nbsp; {weewx_html}")
        except Exception as e:
            self.device_status_label.setText(
                f"<span style='color:#fca5a5; font-weight:700;'>Status check error: {e}</span>"
            )

    def _wind_to_compass(self, degrees):
        """Convert wind direction degrees to compass text."""
        if degrees is None:
            return "--"
        points = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        idx = int((float(degrees) + 22.5) // 45) % 8
        return points[idx]

    def _trend_for_metric(self, records, key):
        """Build simple trend arrow using latest three points."""
        values = [r.get(key) for r in records if r.get(key) is not None]
        if len(values) < 2:
            return "", "No trend"
        old = float(values[-2])
        new = float(values[-1])
        delta = new - old

        if abs(delta) < 0.01:
            return "->", "steady"
        if delta > 0:
            return "up", f"+{delta:.2f}"
        return "down", f"{delta:.2f}"

    def _calc_today_rain(self, records):
        """Sum rainfall from local midnight to now."""
        now = datetime.now()
        midnight = datetime(now.year, now.month, now.day)
        midnight_ts = midnight.timestamp()
        total = 0.0
        for r in records:
            dt = r.get("dateTime")
            rain = r.get("rain")
            if dt is not None and rain is not None and float(dt) >= midnight_ts:
                total += float(rain)
        return total
    
    def update_readings(self):
        """Update current readings from database."""
        try:
            db_path = self.config.weewx_database
            if not db_path.exists():
                for label in self.reading_labels.values():
                    label.setText("Database not found")
                self._set_cards_no_data()
                return
            
            db = WeeWXDatabase(db_path)
            record = db.get_latest_record()
            trend_records = db.get_records_since(2)
            
            if record:
                # Update all reading labels
                for key, label in self.reading_labels.items():
                    value = record.get(key)
                    if value is not None:
                        if isinstance(value, float):
                            label.setText(f"{value:.2f}")
                        else:
                            label.setText(str(value))
                    else:
                        label.setText("--")

                self._update_cards(record)

                # Headline tiles
                feels_like = record.get("heatindex")
                if feels_like is None:
                    feels_like = record.get("windchill")
                if feels_like is None:
                    feels_like = record.get("outTemp")
                self.feels_like_card.set_value(feels_like)

                today_rain = self._calc_today_rain(trend_records)
                self.today_rain_card.set_value(today_rain)

                # Trends for major cards
                temp_trend, temp_text = self._trend_for_metric(trend_records, "outTemp")
                hum_trend, hum_text = self._trend_for_metric(trend_records, "outHumidity")
                pressure_trend, pressure_text = self._trend_for_metric(trend_records, "barometer")
                wind_trend, wind_text = self._trend_for_metric(trend_records, "windSpeed")
                rain_trend, rain_text = self._trend_for_metric(trend_records, "rainRate")

                self.out_temp_card.set_trend(temp_trend, temp_text)
                self.out_hum_card.set_trend(hum_trend, hum_text)
                self.pressure_card.set_trend(pressure_trend, pressure_text)
                self.wind_card.set_trend(wind_trend, wind_text)
                self.rain_rate_card.set_trend(rain_trend, rain_text)

                # Wind compass
                wind_dir = record.get("windDir")
                self.wind_compass.set_direction(wind_dir)
                self.reading_labels["windDir"].setText(self._wind_to_compass(wind_dir))
                
                # Update timestamp
                timestamp = datetime.fromtimestamp(record.get('dateTime', 0))
                self.timestamp_label.setText(f"Last update: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                for label in self.reading_labels.values():
                    label.setText("--")
                self._set_cards_no_data()
                self.wind_compass.set_direction(None)
                self.timestamp_label.setText("Last update: No data")
        
        except Exception as e:
            for label in self.reading_labels.values():
                label.setText(f"Error: {e}")
            self._set_cards_no_data()
            self.wind_compass.set_direction(None)

    def _update_cards(self, record):
        """Update graphical cards from latest record."""
        out_temp = record.get("outTemp")
        out_hum = record.get("outHumidity")
        baro = record.get("barometer")
        wind = record.get("windSpeed")
        gust = record.get("windGust")
        rain_rate = record.get("rainRate")

        self.out_temp_card.set_value(out_temp)
        self.out_hum_card.set_value(out_hum)
        self.pressure_card.set_value(baro)
        self.wind_card.set_value(wind)
        self.gust_card.set_value(gust)
        self.rain_rate_card.set_value(rain_rate)

        if out_temp is not None:
            if out_temp >= 90:
                self.out_temp_card.set_alert_color("#dc2626")
            elif out_temp <= 32:
                self.out_temp_card.set_alert_color("#0284c7")
            else:
                self.out_temp_card.set_alert_color("#dce8f8")

        if out_hum is not None and out_hum >= 80:
            self.out_hum_card.set_alert_color("#0369a1")
        else:
            self.out_hum_card.set_alert_color("#dce8f8")

        if wind is not None and wind >= 20:
            self.wind_card.set_alert_color("#b45309")
        else:
            self.wind_card.set_alert_color("#dce8f8")

        if rain_rate is not None and rain_rate > 0:
            self.rain_rate_card.set_alert_color("#1d4ed8")
        else:
            self.rain_rate_card.set_alert_color("#dce8f8")

    def _set_cards_no_data(self):
        """Reset cards to no-data state."""
        for card in [
            self.feels_like_card,
            self.today_rain_card,
            self.out_temp_card,
            self.out_hum_card,
            self.pressure_card,
            self.wind_card,
            self.gust_card,
            self.rain_rate_card,
        ]:
            card.set_value(None)
            card.set_trend("", "")

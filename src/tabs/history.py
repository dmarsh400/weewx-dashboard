"""
History tab with charts and historical data visualization.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel
)
from PySide6.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from weewx_db import WeeWXDatabase
from datetime import datetime
import math


class HistoryTab(QWidget):
    """Historical data and charting tab."""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.series_registry = []
        self.annotations = {}
        self.init_ui()
        self.refresh()
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout()
        
        # Controls
        controls_layout = QHBoxLayout()
        
        controls_layout.addWidget(QLabel("Time Period:"))
        
        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "Last 24 Hours",
            "Last 7 Days",
            "Last 30 Days",
        ])
        self.period_combo.currentIndexChanged.connect(self.refresh)
        controls_layout.addWidget(self.period_combo)

        mode_label = QLabel("Mode: Grid Dashboard")
        mode_label.setStyleSheet("color: #9bb4d1; font-weight: 600;")
        controls_layout.addWidget(mode_label)
        
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(12, 5), dpi=100)
        self.figure.patch.set_facecolor("#0f1a2b")
        self.canvas = FigureCanvas(self.figure)
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)
        layout.addWidget(self.canvas)
        
        self.setLayout(layout)
    
    def refresh(self):
        """Refresh chart data."""
        try:
            db_path = self.config.weewx_database
            if not db_path.exists():
                return
            
            db = WeeWXDatabase(db_path)
            
            # Get time period
            period_text = self.period_combo.currentText()
            if "24 Hours" in period_text:
                hours = 24
            elif "7 Days" in period_text:
                hours = 7 * 24
            elif "30 Days" in period_text:
                hours = 30 * 24
            else:
                hours = 24
            
            records = db.get_records_since(hours)
            
            if not records:
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                ax.set_facecolor("#0f1a2b")
                ax.text(0.5, 0.5, "No history data available", color="#d7e2f2", ha="center", va="center")
                ax.set_xticks([])
                ax.set_yticks([])
                self.canvas.draw()
                return
            
            timestamps = [datetime.fromtimestamp(r["dateTime"]) for r in records]
            x_nums = mdates.date2num(timestamps)
            nan = float("nan")

            temp = [float(r["outTemp"]) if r.get("outTemp") is not None else nan for r in records]
            humidity = [float(r["outHumidity"]) if r.get("outHumidity") is not None else nan for r in records]
            pressure = [float(r["barometer"]) if r.get("barometer") is not None else nan for r in records]
            wind_speed = [float(r["windSpeed"]) if r.get("windSpeed") is not None else nan for r in records]
            wind_gust = [float(r["windGust"]) if r.get("windGust") is not None else nan for r in records]
            rain_rate = [float(r["rainRate"]) if r.get("rainRate") is not None else nan for r in records]
            rain_total = [float(r["rain"]) if r.get("rain") is not None else 0.0 for r in records]
            
            self.figure.clear()

            axes = self.figure.subplots(3, 2, sharex=True)
            axes = axes.flatten()

            self.series_registry = []
            self.annotations = {}

            self._plot_series(axes[0], x_nums, temp, "Outdoor Temperature", "deg F", "#ff8a65")
            self._plot_series(axes[1], x_nums, humidity, "Outdoor Humidity", "%", "#4fc3f7")
            self._plot_series(axes[2], x_nums, pressure, "Barometer", "inHg", "#b39ddb")

            self._plot_series(axes[3], x_nums, wind_speed, "Wind Speed", "mph", "#80cbc4")
            self._plot_series(axes[3], x_nums, wind_gust, "Wind Gust", "mph", "#ef9a9a", linestyle="--", attach_annotation=False)
            axes[3].legend(loc="upper left", fontsize=8)

            self._plot_series(axes[4], x_nums, rain_rate, "Rain Rate", "in/hr", "#64b5f6")
            self._plot_bars(axes[5], x_nums, rain_total, "Rain Total", "in", "#42a5f5")

            for ax in axes:
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d\n%H:%M"))
                ax.tick_params(axis="x", labelsize=8, colors="#9bb4d1")
                ax.tick_params(axis="y", labelsize=8, colors="#9bb4d1")

            self.figure.tight_layout()
            self.canvas.draw()
        
        except Exception as e:
            print(f"Error refreshing chart: {e}")

    def _style_axes(self, ax, title, y_label):
        """Apply dark chart styling."""
        ax.set_facecolor("#111f32")
        ax.set_title(title, fontsize=10, fontweight="bold", color="#d7e2f2")
        ax.set_ylabel(y_label, fontsize=9, color="#9bb4d1")
        ax.grid(True, alpha=0.22, color="#3a5477")
        for spine in ax.spines.values():
            spine.set_color("#2b3f5b")

    def _ensure_annotation(self, ax):
        """Create per-axis tooltip annotation."""
        ann = ax.annotate(
            "",
            xy=(0, 0),
            xytext=(10, 10),
            textcoords="offset points",
            bbox={"boxstyle": "round,pad=0.3", "fc": "#0b1220", "ec": "#4d6a8e", "alpha": 0.95},
            color="#d7e2f2",
            fontsize=8,
        )
        ann.set_visible(False)
        self.annotations[ax] = ann

    def _plot_series(self, ax, x_nums, y_vals, label, unit, color, linestyle="-", attach_annotation=True):
        """Plot a line series and register for hover tooltips."""
        self._style_axes(ax, label, unit)
        ax.plot(x_nums, y_vals, linestyle=linestyle, linewidth=1.8, color=color, label=label)

        if ax not in self.annotations:
            self._ensure_annotation(ax)

        if attach_annotation:
            self.series_registry.append(
                {
                    "ax": ax,
                    "x": x_nums,
                    "y": y_vals,
                    "label": label,
                    "unit": unit,
                    "color": color,
                }
            )

    def _plot_bars(self, ax, x_nums, y_vals, label, unit, color):
        """Plot bar series and register bar tops for hover tooltips."""
        self._style_axes(ax, label, unit)
        bar_width = (x_nums[-1] - x_nums[0]) / max(80, len(x_nums) * 2)
        if bar_width <= 0:
            bar_width = 0.004
        ax.bar(x_nums, y_vals, width=bar_width, color=color, alpha=0.85)

        if ax not in self.annotations:
            self._ensure_annotation(ax)

        self.series_registry.append(
            {
                "ax": ax,
                "x": x_nums,
                "y": y_vals,
                "label": label,
                "unit": unit,
                "color": color,
            }
        )

    def on_hover(self, event):
        """Show tooltip with detailed value when hovering near chart points."""
        changed = False

        for ann in self.annotations.values():
            if ann.get_visible():
                ann.set_visible(False)
                changed = True

        if event.inaxes is None or event.xdata is None:
            if changed:
                self.canvas.draw_idle()
            return

        candidates = [s for s in self.series_registry if s["ax"] == event.inaxes]
        if not candidates:
            if changed:
                self.canvas.draw_idle()
            return

        best = None
        best_dist = 999999.0

        for series in candidates:
            x_vals = series["x"]
            y_vals = series["y"]
            if len(x_vals) == 0:
                continue
            idx = min(range(len(x_vals)), key=lambda i: abs(x_vals[i] - event.xdata))
            y = y_vals[idx]
            if y is None:
                continue
            try:
                if math.isnan(float(y)):
                    continue
            except Exception:
                continue

            px, py = event.inaxes.transData.transform((x_vals[idx], y))
            dist = ((px - event.x) ** 2 + (py - event.y) ** 2) ** 0.5
            if dist < best_dist:
                best_dist = dist
                best = (series, idx, y)

        if best is None or best_dist > 25:
            if changed:
                self.canvas.draw_idle()
            return

        series, idx, y = best
        ax = series["ax"]
        ann = self.annotations.get(ax)
        if ann is None:
            return

        dt = mdates.num2date(series["x"][idx])
        ann.xy = (series["x"][idx], y)
        ann.set_text(
            f"{series['label']}\n"
            f"{dt.strftime('%Y-%m-%d %H:%M')}\n"
            f"{float(y):.2f} {series['unit']}"
        )
        ann.get_bbox_patch().set_edgecolor(series["color"])
        ann.set_visible(True)
        self.canvas.draw_idle()

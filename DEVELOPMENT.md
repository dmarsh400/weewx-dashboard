# Development Guide

This guide explains how to extend and develop the WeeWX Dashboard.

## Architecture Overview

```
main.py (QMainWindow)
├── SetupTab (configure paths & WU credentials)
├── MonitorTab (live readings)
├── HistoryTab (charts)
├── PublishStatusTab (WU status)
└── LogsTab (service logs)

config.py (Configuration management)
weewx_db.py (Database reader)
```

## Adding a New Tab

### 1. Create the Tab File

Create `src/tabs/my_new_tab.py`:

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtGui import QFont

class MyNewTab(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        label = QLabel("My new tab content")
        layout.addWidget(label)
        self.setLayout(layout)
    
    def refresh(self):
        """Called when tab is active and timer fires."""
        pass
```

### 2. Register in main.py

In `src/main.py`, add to `WeeWXDashboard.__init__()`:

```python
from tabs.my_new_tab import MyNewTab

# In __init__:
self.my_tab = MyNewTab(self.config)
self.tab_widget.addTab(self.my_tab, "My Tab")
```

## Database Access Pattern

To read WeeWX data:

```python
from weewx_db import WeeWXDatabase
from pathlib import Path

db = WeeWXDatabase(Path("/var/lib/weewx/weewx.sdb"))

# Get latest record
record = db.get_latest_record()
print(record['outTemp'])  # Current temperature

# Get historical data
records = db.get_records_since(hours=24)
for r in records:
    print(r['dateTime'], r['outTemp'])
```

## Configuration Access Pattern

```python
# Get value
value = self.config.get("key", "default_value")

# Set value (auto-saves)
self.config.set("key", "new_value")

# Direct access
print(self.config.weewx_database)  # Path object
print(self.config.weewx_config)    # Path object
```

## UI Components

### Common Layouts

```python
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton,
    QComboBox, QCheckBox, QTextEdit
)

# Vertical stack
vbox = QVBoxLayout()
vbox.addWidget(widget1)
vbox.addWidget(widget2)

# Horizontal stack
hbox = QHBoxLayout()
hbox.addWidget(widget1)
hbox.addWidget(widget2)

# Grid layout
grid = QGridLayout()
grid.addWidget(label, 0, 0)      # Row 0, Col 0
grid.addWidget(input, 0, 1)      # Row 0, Col 1
```

### Styling

```python
# Apply styles
button.setStyleSheet("""
    background-color: #4CAF50;
    color: white;
    padding: 8px;
    font-weight: bold;
    border-radius: 4px;
""")

# Font
from PySide6.QtGui import QFont
font = QFont("Arial", 12, QFont.Bold)
label.setFont(font)
```

## Running with Matplotlib

The HistoryTab shows how to embed matplotlib:

```python
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Create figure
self.figure = Figure(figsize=(12, 5), dpi=100)
self.canvas = FigureCanvas(self.figure)
layout.addWidget(self.canvas)

# Plot data
ax = self.figure.add_subplot(111)
ax.plot(x_data, y_data)
ax.set_title("My Chart")
self.figure.tight_layout()
self.canvas.draw()
```

## Running External Commands

```python
import subprocess

# Blocking call
result = subprocess.run(
    ["lsusb"],
    capture_output=True,
    text=True,
    timeout=5
)
print(result.stdout)
print(result.returncode)

# Background thread (for long operations)
from PySide6.QtCore import QThread, pyqtSignal

class WorkerThread(QThread):
    finished = pyqtSignal(str)
    
    def run(self):
        result = subprocess.run(["command"], capture_output=True, text=True)
        self.finished.emit(result.stdout)

thread = WorkerThread()
thread.finished.connect(self.on_finished)
thread.start()
```

## Debugging

### Enable Debug Output

```python
# In main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Issues

**"Cannot find USB device" in Monitor tab**
- Check WeeWX is running: `systemctl status weewx`
- Verify device: `lsusb | grep 24c0`

**"Database not found"**
- Verify path in Setup tab
- Check file permissions: `ls -la /etc/weewx/weewx.sdb`

**Permission denied for logs**
- Logs tab needs sudo to read journalctl
- Run with: `sudo python src/main.py`

## Building Distribution Packages

### Linux AppImage

```bash
pip install appimage-builder
appimage-builder build
```

### Windows Installer

```bash
pip install pyinstaller
pyinstaller weewx_dashboard.spec
# Creates dist/weewx-dashboard/
```

### Debian Package

```bash
pip install stdeb
python setup.py --command-packages=stdeb.command bdist_deb
```

## Testing

Run from command line with:

```bash
cd /path/to/weewx-dashboard
python src/main.py
```

Monitor for errors in the terminal output.

## Performance Tips

1. **Refresh Rate**: Monitor tab refreshes every 1 second. Adjust in main.py if needed:
   ```python
   self.refresh_timer.start(2000)  # 2 seconds
   ```

2. **Database Queries**: History tab queries can be slow. Cache results:
   ```python
   self.cached_records = None
   self.cache_time = 0
   ```

3. **Log Streaming**: Logs tab keeps last 500 lines. Adjust in logs.py:
   ```python
   if doc.blockCount() > 500:  # Change 500 to desired limit
   ```

## Contributing

1. Create a feature branch
2. Make changes with clear commit messages
3. Test locally with `python src/main.py`
4. Submit pull request

## Resources

- [PySide6 Documentation](https://doc.qt.io/qtforpython/)
- [WeeWX Documentation](https://weewx.com/docs)
- [Matplotlib Guide](https://matplotlib.org/stable/tutorials/index)

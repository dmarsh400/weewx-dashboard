# WeeWX Dashboard

A modern, cross-platform GUI dashboard for monitoring WeeWX weather station data and Weather Underground uploads.

## Features

- **Setup Tab**: Configure WeeWX paths, Weather Underground credentials, and verify system status
- **Live Monitor**: Real-time weather readings directly from your station (temperature, humidity, wind, pressure, etc.)
- **History**: Interactive charts showing historical data trends over 24 hours, 7 days, or 30 days
- **Publish Status**: Track Weather Underground uploads, view recent activity, and error logs
- **Live Logs**: Real-time tail of WeeWX service logs with filtering capabilities
- **Cross-Platform**: Runs on Linux and Windows

## System Requirements

- Python 3.8+
- WeeWX installed and configured
- Linux or Windows operating system

## Installation

### From Source (Development)

```bash
# Clone or download the repository
cd weewx-dashboard

# Create a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python src/main.py
```

### From Source (System-wide Installation)

```bash
python3 -m pip install --user . --break-system-packages
weewx-dashboard
```

Recommended on Linux:

```bash
pipx install .
```

### Linux Menu Install (shows up in Programs list)

```bash
chmod +x scripts/install-linux-user.sh
./scripts/install-linux-user.sh
```

This installs:
- executable: `~/.local/bin/weewx-dashboard`
- launcher: `~/.local/share/applications/weewx-dashboard.desktop`

Notes:
- On Ubuntu/Debian with PEP 668, the script uses `pipx` when available.
- If `pipx` is unavailable, it falls back to `pip --user --break-system-packages`.

### Flatpak Install (Linux)

Build and install locally:

```bash
chmod +x scripts/prepare-flatpak-deps.sh scripts/build-flatpak.sh scripts/install-flatpak-local.sh
./scripts/install-flatpak-local.sh
```

Run:

```bash
flatpak run io.github.weewxdashboard
```

Flatpak files:
- Manifest: `packaging/flatpak/org.weewx.Dashboard.yaml`
- Desktop file: `packaging/flatpak/org.weewx.Dashboard.desktop`
- Metadata: `packaging/flatpak/org.weewx.Dashboard.metainfo.xml`
- Generated deps: `packaging/flatpak/python3-deps.json`

Generate/update Flatpak Python dependency lock file:

```bash
./scripts/prepare-flatpak-deps.sh
```

### Flathub Submission Prep

1. Ensure your app ID is stable: `io.github.weewxdashboard`
2. Commit manifest + metainfo + desktop + icon + `python3-deps.json`
3. Push source to GitHub and create a tagged release
4. In Flathub, submit a new app request/PR using your manifest
5. Update manifest source section from local `type: dir` to GitHub archive URL + sha256 before PR

Typical end-user install after Flathub approval:

```bash
flatpak install flathub io.github.weewxdashboard
```

### Building Standalone Executables

```bash
# Linux binary build
chmod +x scripts/build-linux-binary.sh
./scripts/build-linux-binary.sh

# Run binary
dist/weewx-dashboard/weewx-dashboard
```

```powershell
# Windows binary build (PowerShell)
./scripts/build-windows.ps1

# Output
dist\weewx-dashboard\weewx-dashboard.exe
```

### Windows Installer (Inno Setup)

```powershell
# Requires Inno Setup 6 installed
./scripts/build-windows-installer.ps1
```

Outputs installer to:

```text
dist\installer\WeeWXDashboardSetup.exe
```

Installer script:
- `packaging/windows/WeeWXDashboard.iss`

### Cross-Platform Distribution Notes

- Linux: Build on each target distro family for best compatibility, or distribute Flatpak.
- Linux app menu integration is provided by `packaging/weewx-dashboard.desktop`.
- Windows: build with PyInstaller on Windows for native `.exe` output.
- Optional installer layers:
   - Linux: AppImage/Flatpak/deb/rpm
   - Windows: Inno Setup or NSIS installer around the built executable

Important Flatpak note:
- This app calls host utilities (`systemctl`, `journalctl`, `lsusb`). Inside Flatpak sandbox, some diagnostics/control features may require host-bridge adjustments or reduced sandboxing policies during Flathub review.

## Configuration

On first launch, use the **Setup** tab to:

1. Verify WeeWX installation paths:
   - WeeWX Root: `/etc/weewx`
   - Config File: `/etc/weewx/weewx.conf`
   - Database: `/var/lib/weewx/weewx.sdb`

2. Enter your Weather Underground credentials:
   - Station ID (e.g., `KXXXXXXX`)
   - API Key (from your WU account)

3. Click "Check Status" to verify:
   - Config file exists
   - Database file exists
   - WeeWX service is running

4. Click "Save Configuration" to persist settings

## Usage

### Live Monitor Tab
- Displays current weather readings updated in real-time
- Shows device connection status (Acurite console, WeeWX service)
- Automatically refreshes data every second

### History Tab
- Select time period: Last 24 Hours, 7 Days, or 30 Days
- View all major charts in a default grid dashboard
- Hover near lines/bars to see detailed timestamp + value tooltips

### Publish Status Tab
- View last successful Weather Underground upload
- Track upload errors and retry status
- See recent WeeWX activity related to uploads

### Logs Tab
- Real-time streaming of WeeWX service logs
- Filter by: Errors, Wunderground, Driver, Archive, INFO, DEBUG
- Keeps last 500 lines for performance
- Clear logs display with one click

## Keyboard Shortcuts

- **Tab Navigation**: Use mouse or arrow keys to switch tabs
- **Refresh**: Click the Refresh button on any tab

## Troubleshooting

### "Database not found" Error
- Verify WeeWX Root path in Setup tab
- Ensure WeeWX is running: `systemctl status weewx`

### Permission Errors Reading Logs
- The dashboard requires sudo to read WeeWX logs
- On Linux, run with: `sudo python src/main.py`
- Or add your user to sudo without password (not recommended for security)

### Weather Underground Not Uploading
- Check Publish Status tab for recent errors
- Verify credentials in Setup tab
- Check WeeWX service logs in Logs tab (filter by "Wunderground")

### USB Device Not Detected
- Check Live Monitor for device status
- Verify your console is plugged in
- Run: `lsusb | grep 24c0`

## Development

### Project Structure

```
weewx-dashboard/
├── src/
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration management
│   ├── weewx_db.py          # WeeWX database interface
│   └── tabs/
│       ├── setup.py         # Setup tab
│       ├── monitor.py       # Live monitor tab
│       ├── history.py       # History/charts tab
│       ├── publish_status.py # WU publish status tab
│       └── logs.py          # Live logs tab
├── requirements.txt         # Python dependencies
├── setup.py                 # Installation script
├── weewx_dashboard.spec     # PyInstaller configuration
└── README.md               # This file
```

### Adding New Tabs

1. Create a new file in `src/tabs/`
2. Inherit from `QWidget`
3. Implement `init_ui()` method
4. Add to main.py's `WeeWXDashboard.__init__()`

## License

MIT License - See LICENSE file for details

## Support

For issues, feature requests, or contributions, please open an issue on GitHub.

## Changelog

### Version 1.0.0
- Initial release
- Five main tabs: Setup, Monitor, History, Publish Status, Logs
- Cross-platform support (Linux, Windows)
- Real-time data visualization
- Weather Underground integration monitoring

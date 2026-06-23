# WeeWX Dashboard

Modern desktop dashboard for WeeWX with live station monitoring, Weather Underground publish tracking, diagnostics, and history charts.

## Highlights

- Live monitor with weather cards, trend indicators, and wind compass
- Device/service health status with clear color indicators
- History tab with multi-chart grid and hover tooltips
- Publish diagnostics with auto-refresh and troubleshooting hints
- Dark mode UI
- Linux + Windows packaging support

## Quick Start (Development)

```bash
cd weewx-dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

## Install as App (Linux)

```bash
chmod +x scripts/install-linux-user.sh
./scripts/install-linux-user.sh
```

This installs:

- command: `~/.local/bin/weewx-dashboard`
- launcher: `~/.local/share/applications/weewx-dashboard.desktop`

If command is not found, ensure `~/.local/bin` is in your `PATH`.

## Flatpak (Local)

```bash
chmod +x scripts/prepare-flatpak-deps.sh scripts/build-flatpak.sh scripts/install-flatpak-local.sh
./scripts/install-flatpak-local.sh
flatpak run io.github.weewxdashboard
```

Flatpak files are in [packaging/flatpak](packaging/flatpak).

## Windows Build + Installer

From PowerShell on Windows:

```powershell
./scripts/build-windows.ps1
./scripts/build-windows-installer.ps1
```

Outputs:

- app bundle: `dist\weewx-dashboard\`
- installer: `dist\installer\WeeWXDashboardSetup.exe`

## Project Layout

```text
src/
  main.py
  config.py
  weewx_db.py
  tabs/
packaging/
  flatpak/
  windows/
scripts/
```

## License

MIT. See [LICENSE](LICENSE).

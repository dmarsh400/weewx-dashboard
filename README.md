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

## Automated GitHub Releases

Workflow: [.github/workflows/release.yml](.github/workflows/release.yml)

When you push a tag like `v1.0.1`, GitHub Actions will:

1. Build Linux artifact (`.tar.gz`)
2. Build Windows app + Inno Setup installer (`.exe`)
3. Publish/update GitHub Release and attach artifacts

Release command example:

```bash
git tag -a v1.0.1 -m "v1.0.1"
git push origin v1.0.1
```

## Flathub Prep Notes

- App ID currently set to `io.github.weewxdashboard`
- Before Flathub submission, point manifest source to your GitHub release archive + `sha256`
- Regenerate `python3-deps.json` whenever Python dependencies change

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

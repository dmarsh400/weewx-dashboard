"""
Configuration and settings management for WeeWX Dashboard.
"""

from pathlib import Path
import json


class Config:
    """Manage application configuration."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "weewx-dashboard"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        
        # Default paths
        self.weewx_root = Path("/etc/weewx")
        self.weewx_conf = self.weewx_root / "weewx.conf"
        self.weewx_db = Path("/var/lib/weewx/weewx.sdb")
        
        # Load or create config
        self.settings = self._load_config()
        
    def _load_config(self):
        """Load configuration from file or return defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    return json.load(f)
            except Exception:
                pass
        
        return {
            "weewx_root": str(self.weewx_root),
            "weewx_conf": str(self.weewx_conf),
            "weewx_db": str(self.weewx_db),
            "wu_station_id": "",
            "wu_api_key": "",
            "auto_refresh": True,
            "refresh_interval": 1000,
        }
    
    def save(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key, default=None):
        """Get a configuration value."""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a configuration value and save."""
        self.settings[key] = value
        self.save()
    
    @property
    def weewx_database(self):
        """Get WeeWX database path."""
        return Path(self.get("weewx_db", str(self.weewx_db)))
    
    @property
    def weewx_config(self):
        """Get WeeWX config file path."""
        return Path(self.get("weewx_conf", str(self.weewx_conf)))

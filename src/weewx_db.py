"""
WeeWX database reader module.
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


class WeeWXDatabase:
    """Interface to WeeWX SQLite database."""
    
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
    
    def _get_connection(self):
        """Get database connection."""
        if not self.db_path.exists():
            raise FileNotFoundError(f"WeeWX database not found: {self.db_path}")
        return sqlite3.connect(str(self.db_path))
    
    def get_latest_record(self) -> Optional[Dict]:
        """Get the latest archive record from the database."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT dateTime, usUnits, interval, barometer, altimeter,
                       inTemp, outTemp, inHumidity, outHumidity,
                       windSpeed, windDir, windGust, rain, rainRate,
                       dewpoint, windchill, heatindex
                FROM archive
                ORDER BY dateTime DESC
                LIMIT 1
            """)
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'dateTime': row[0],
                    'usUnits': row[1],
                    'interval': row[2],
                    'barometer': row[3],
                    'altimeter': row[4],
                    'inTemp': row[5],
                    'outTemp': row[6],
                    'inHumidity': row[7],
                    'outHumidity': row[8],
                    'windSpeed': row[9],
                    'windDir': row[10],
                    'windGust': row[11],
                    'rain': row[12],
                    'rainRate': row[13],
                    'dewpoint': row[14],
                    'windchill': row[15],
                    'heatindex': row[16],
                }
        except Exception as e:
            print(f"Error reading latest record: {e}")
        return None
    
    def get_records_since(self, hours: int = 24) -> List[Dict]:
        """Get all records from the past N hours."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Calculate timestamp for N hours ago
            now = datetime.now().timestamp()
            since = now - (hours * 3600)
            
            cursor.execute("""
                SELECT dateTime, outTemp, outHumidity, windSpeed, 
                       windDir, barometer, rain, rainRate
                FROM archive
                WHERE dateTime >= ?
                ORDER BY dateTime ASC
            """, (since,))
            
            records = []
            for row in cursor.fetchall():
                records.append({
                    'dateTime': row[0],
                    'outTemp': row[1],
                    'outHumidity': row[2],
                    'windSpeed': row[3],
                    'windDir': row[4],
                    'barometer': row[5],
                    'rain': row[6],
                    'rainRate': row[7],
                })
            
            conn.close()
            return records
        except Exception as e:
            print(f"Error reading records: {e}")
        return []
    
    def get_daily_summary(self, date_str: str) -> Optional[Dict]:
        """Get daily summary for a specific date (YYYYMMDD)."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT dateTime, min, mintime, max, maxtime, 
                       avg, rms, sum
                FROM archive_day_outTemp
                WHERE dateTime = ?
            """, (int(date_str),))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'date': row[0],
                    'min': row[1],
                    'mintime': row[2],
                    'max': row[3],
                    'maxtime': row[4],
                    'avg': row[5],
                }
        except Exception as e:
            print(f"Error reading daily summary: {e}")
        return None

"""
SQLite database operations for complaint tracking.
"""

import sqlite3
import uuid
from datetime import datetime

DB_PATH = "complaints.db"


def init_db():
    """Create complaints table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS complaints (
            ticket_id TEXT PRIMARY KEY,
            category TEXT,
            severity TEXT,
            description TEXT,
            latitude REAL,
            longitude REAL,
            department TEXT,
            status TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def create_complaint(category, severity, description, lat, lon, department):
    """
    Insert a new complaint and return its generated ticket ID.
    Format: CIV-XXXXXX (6 uppercase hex chars).
    """
    ticket_id = "CIV-" + str(uuid.uuid4())[:6].upper()
    now = datetime.now().isoformat()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO complaints VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            ticket_id,
            category,
            severity,
            description,
            lat,
            lon,
            department,
            "Submitted",
            now,
            now,
        ),
    )
    conn.commit()
    conn.close()
    return ticket_id


def get_all_complaints():
    """Fetch all complaints as list of dicts (newest first)."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM complaints ORDER BY created_at DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_complaint(ticket_id):
    """Fetch a single complaint by ticket ID."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM complaints WHERE ticket_id = ?", (ticket_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def update_status(ticket_id, new_status):
    """Update the status of a complaint."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "UPDATE complaints SET status = ?, updated_at = ? WHERE ticket_id = ?",
        (new_status, datetime.now().isoformat(), ticket_id),
    )
    conn.commit()
    conn.close()


def get_stats():
    """Return aggregate stats for the dashboard."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    stats = {}
    for status in ["Submitted", "Acknowledged", "In Progress", "Resolved"]:
        c.execute("SELECT COUNT(*) FROM complaints WHERE status = ?", (status,))
        stats[status] = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM complaints")
    stats["Total"] = c.fetchone()[0]
    conn.close()
    return stats

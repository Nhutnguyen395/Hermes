import sqlite3
import uuid
import os

# Store the DB file in the root of the sentinel-agent directory
DB_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "incidents.db")

def init_db():
    """ Create the incident table if it doesn't exists."""
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id TEXT PRIMARY KEY,
                root_cause TEXT,
                action TEXT,
                target TEXT,
                status TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

def create_incident(root_cause: str, action: str, target: str) -> str:
    """ Saves a pending incident and returns a unique Ticket ID """
    incident_id = str(uuid.uuid4())
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            "INSERT INTO incidents (id, root_cause, action, target, status) VALUES (?, ?, ?, ?, ?)",
            (incident_id, root_cause, action, target, "PENDING")
        )
    return incident_id

def get_pending_incidents() -> list:
    """ Retrieves all incidents waiting for human approval. """
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM incidents WHERE status = 'PENDING'").fetchall()
        return [dict(row) for row in rows]

def get_incident(incident_id: str) -> dict:
    """ Fetch a specific incident ID. """
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,)).fetchone()
    return dict(row) if row else None

def update_incident_status(incident_id: str, status: str):
    """ Updates the status to APPROVED or DENIED. """
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("UPDATE incidents SET status = ? WHERE id = ?", (status, incident_id))
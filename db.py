import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.getcwd(), "specgen.db")

# ----------------------------------
# Initialize Database
# ----------------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS specifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            feature TEXT,
            json_output TEXT,
            markdown_output TEXT,
            created_at TEXT
        );
        """
    )

    conn.commit()
    conn.close()


# ----------------------------------
# Save Specification
# ----------------------------------
def save_spec(title: str, feature: str, json_str: str, markdown: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO specifications (title, feature, json_output, markdown_output, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            title,
            feature,
            json_str,
            markdown,
            datetime.utcnow().isoformat()
        )
    )

    conn.commit()
    conn.close()


# ----------------------------------
# Fetch All Specifications
# ----------------------------------
def get_all_specs():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, title, feature, created_at FROM specifications ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return rows


# ----------------------------------
# Fetch Full Spec
# ----------------------------------
def get_spec_by_id(spec_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, title, feature, json_output, markdown_output, created_at FROM specifications WHERE id = ?",
        (spec_id,)
    )
    row = cur.fetchone()
    conn.close()
    return row


# ----------------------------------
# Delete Specification
# ----------------------------------
def delete_spec(spec_id: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM specifications WHERE id = ?", (spec_id,))
    conn.commit()
    conn.close()


# ----------------------------------
# Initialize DB at import
# ----------------------------------
init_db()
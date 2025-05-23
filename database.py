import sqlite3
import os
from datetime import datetime

# Path to the database file
DB_PATH = os.path.abspath('basededon.db')
print(f"Using database file: {DB_PATH}")

# Establishing database connection
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

def initialize_database():
    """Creates the measurements table if it doesn't exist."""
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            m_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            measure_type TEXT NOT NULL,
            value REAL NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()
        print("Table created successfully.")
    except Exception as e:
        print(f"Error creating table: {e}")

def insert_measurements(patient_id, measure_type, value):
    """Inserts a new measurement into the database."""
    try:
        cursor.execute("""
        INSERT INTO measurements (patient_id, measure_type, value, date)
        VALUES (?, ?, ?, ?)
        """, (patient_id, measure_type, value, datetime.now()))
        conn.commit()
        print("Inserted into table successfully.")
    except Exception as e:
        print(f"Error inserting into table: {e}")

def get_measurements(measure_type):
    """Fetches measurement data for a specific measure_type."""
    try:
        cursor.execute("""
        SELECT date, value FROM measurements
        WHERE measure_type = ?
        ORDER BY date ASC
        """, (measure_type,))
        data = cursor.fetchall()
        return data
    except Exception as e:
        print(f"Error fetching measurements: {e}")
        return []

def show_table_content():
    """Displays all records in the measurements table."""
    try:
        cursor.execute("SELECT * FROM measurements;")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
    except Exception as e:
        print(f"Error displaying table content: {e}")

if __name__ == "__main__":

    initialize_database()

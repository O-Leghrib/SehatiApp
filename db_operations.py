# db_operations.py
import sqlite3
import bcrypt # Assuming you use bcrypt for password hashing
from datetime import datetime # For date handling in measurements and reminders

# === Database Initialization ===
def initialize_database_unified():
    conn = sqlite3.connect('myapp.db')
    cursor = conn.cursor()

    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')

    # Create Forms table (now including medications)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Forms (
        form_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        weight TEXT,
        height TEXT,
        age TEXT,
        blood_type TEXT,
        diabetes INTEGER,         -- 0 for False, 1 for True
        blood_pressure INTEGER,     -- 0 for False, 1 for True
        heart_disease INTEGER,     -- 0 for False, 1 for True
        medications TEXT,          -- Added this column for medications
        FOREIGN KEY (user_id) REFERENCES Users(user_id)
    )
    ''')

    # Create Emergency Contacts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS emergency_contacts (
            user_id INTEGER,
            name TEXT,
            number TEXT,
            FOREIGN KEY (user_id) REFERENCES Users(user_id)
        )
    """)
    
    # Create Measurements table - THIS IS THE TABLE FOR USER-SPECIFIC MEASUREMENTS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS measurements (
        measure_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        blood_sugar REAL,
        blood_pressure_systolic INTEGER,
        blood_pressure_diastolic INTEGER,
        weight REAL,
        measure_date TEXT, -- e.g., "YYYY-MM-DD"
        FOREIGN KEY (user_id) REFERENCES Users(user_id)
    )
    ''')

    # Create Reminders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reminders (
        reminder_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        reminder_text TEXT NOT NULL,
        reminder_time TEXT NOT NULL, -- e.g., "HH:MM"
        reminder_date TEXT,          -- e.g., "YYYY-MM-DD" (for one-time)
        frequency TEXT,              -- e.g., "daily", "weekly", "once"
        FOREIGN KEY (user_id) REFERENCES Users(user_id)
    )
    ''')


    conn.commit()
    conn.close()
    print("Database 'myapp.db' initialized with all necessary tables.")


# === User Authentication & Registration ===
def signup_user(username, email, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = sqlite3.connect('myapp.db')
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Users (username, email, password) VALUES (?, ?, ?)",
                       (username, email, hashed_password))
        user_id = cursor.lastrowid
        conn.commit()
        return user_id # Return the newly created user_id
    except sqlite3.IntegrityError:
        return None # Username or email already exists
    finally:
        conn.close()

def login_user(username, password):
    conn = sqlite3.connect('myapp.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, password FROM Users WHERE username = ?", (username,))
    user_data = cursor.fetchone()
    conn.close()
    if user_data:
        user_id, hashed_password_from_db = user_data
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password_from_db):
            return user_id
    return None

# === User Profile & Form Data ===
def get_user_info_db(user_id):
    """Fetches user details from Users and Forms tables."""
    conn = sqlite3.connect("myapp.db")
    cursor = conn.cursor()
    cursor.execute("SELECT username, email, password FROM Users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    cursor.execute("SELECT weight, height, age, blood_type, diabetes, blood_pressure, heart_disease, medications FROM Forms WHERE user_id = ?", (user_id,))
    profile = cursor.fetchone()
    conn.close()
    return user, profile

def update_user_info_db(user_id, username, email, password_hash, weight, height, age, blood_type, diabetes, bp, heart, medications):
    """Updates user details in Users and Forms tables."""
    try:
        conn = sqlite3.connect("myapp.db")
        cursor = conn.cursor()
        
        # Update Users table (password_hash is already hashed here if changing password)
        cursor.execute("UPDATE Users SET username = ?, email = ?, password = ? WHERE user_id = ?", 
                       (username, email, password_hash, user_id))

        # Check if form data exists for the user, then update or insert
        cursor.execute("SELECT * FROM Forms WHERE user_id = ?", (user_id,))
        if cursor.fetchone():
            cursor.execute("""
                UPDATE Forms SET weight = ?, height = ?, age = ?, blood_type = ?, diabetes = ?, blood_pressure = ?, heart_disease = ?, medications = ?
                WHERE user_id = ?
            """, (weight, height, age, blood_type, diabetes, bp, heart, medications, user_id))
        else:
            cursor.execute("""
                INSERT INTO Forms (user_id, weight, height, age, blood_type, diabetes, blood_pressure, heart_disease, medications)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, weight, height, age, blood_type, diabetes, bp, heart, medications))

        conn.commit()
        return True, "Profile updated successfully!"
    except sqlite3.IntegrityError as e:
        return False, f"Error: A user with this username or email already exists. {e}"
    except Exception as e:
        return False, f"An unexpected error occurred: {e}"
    finally:
        if conn:
            conn.close()

# === Emergency Contact ===
def save_emergency_contact_db(user_id, name, number):
    """Saves or updates emergency contact for a user."""
    conn = sqlite3.connect("myapp.db")
    cursor = conn.cursor()
    # Delete existing contact for the user to ensure only one per user
    cursor.execute("DELETE FROM emergency_contacts WHERE user_id = ?", (user_id,))
    cursor.execute("INSERT INTO emergency_contacts (user_id, name, number) VALUES (?, ?, ?)", (user_id, name, number))
    conn.commit()
    conn.close()

def get_emergency_contact_db(user_id):
    """Retrieves emergency contact for a user."""
    conn = sqlite3.connect("myapp.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, number FROM emergency_contacts WHERE user_id = ?", (user_id,))
    contact = cursor.fetchone()
    conn.close()
    return contact


# === Measurements Operations ===
def add_measurement_db(user_id, blood_sugar, blood_pressure_systolic, blood_pressure_diastolic, weight, measure_date):
    """Inserts a new measurement for a user."""
    conn = sqlite3.connect('myapp.db')
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO measurements (user_id, blood_sugar, blood_pressure_systolic, blood_pressure_diastolic, weight, measure_date) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, blood_sugar, blood_pressure_systolic, blood_pressure_diastolic, weight, measure_date)
        )
        conn.commit()
        return True, "Measurement added successfully!"
    except Exception as e:
        print(f"Error adding measurement: {e}")
        return False, f"Error adding measurement: {e}"
    finally:
        conn.close()

def get_measurements_db(user_id):
    """Retrieves all measurements for a specific user, ordered by date."""
    conn = sqlite3.connect('myapp.db')
    cursor = conn.cursor()
    cursor.execute("SELECT blood_sugar, blood_pressure_systolic, blood_pressure_diastolic, weight, measure_date FROM measurements WHERE user_id = ? ORDER BY measure_date ASC", (user_id,))
    measurements = cursor.fetchall()
    conn.close()
    return measurements

# === Reminders Operations ===
def add_reminder_db(user_id, reminder_text, reminder_time, reminder_date=None, frequency="once"):
    conn = sqlite3.connect('myapp.db')
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO reminders (user_id, reminder_text, reminder_time, reminder_date, frequency) VALUES (?, ?, ?, ?, ?)",
            (user_id, reminder_text, reminder_time, reminder_date, frequency)
        )
        conn.commit()
        return True, "Reminder added successfully!"
    except Exception as e:
        print(f"Error adding reminder: {e}")
        return False, f"Error adding reminder: {e}"
    finally:
        conn.close()

def get_reminders_db(user_id):
    conn = sqlite3.connect('myapp.db')
    cursor = conn.cursor()
    cursor.execute("SELECT reminder_id, reminder_text, reminder_time, reminder_date, frequency FROM reminders WHERE user_id = ?", (user_id,))
    reminders = cursor.fetchall()
    conn.close()
    return reminders

def delete_reminder_db(reminder_id):
    conn = sqlite3.connect('myapp.db')
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM reminders WHERE reminder_id = ?", (reminder_id,))
        conn.commit()
        return True, "Reminder deleted successfully!"
    except Exception as e:
        print(f"Error deleting reminder: {e}")
        return False, f"Error deleting reminder: {e}"
    finally:
        conn.close()
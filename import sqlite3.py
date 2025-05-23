import sqlite3
import tkinter as tk
from tkinter import messagebox

# === إنشاء قاعدة البيانات والجداول ===
def initialize_database():
    conn = sqlite3.connect('myapp.db')
    cursor = conn.cursor()

    # Drop tables if they exist to ensure a clean start for testing
    # You might remove these in a production environment
    cursor.execute('DROP TABLE IF EXISTS Forms')
    cursor.execute('DROP TABLE IF EXISTS Users')
    cursor.execute('DROP VIEW IF EXISTS Profile')


    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER DEFAULT 1 PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Forms (
        form_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        weight TEXT,
        height TEXT,
        age TEXT,
        blood_type TEXT,
        diabetes INTEGER,        -- 0 for False, 1 for True
        blood_pressure INTEGER,   -- 0 for False, 1 for True
        heart_disease INTEGER,    -- 0 for False, 1 for True
        medications TEXT,         -- Added this column for medications
        FOREIGN KEY (user_id) REFERENCES Users(user_id)
    )
    ''')

    # Corrected CREATE VIEW statement
    # A VIEW combines data from tables but doesn't store data itself,
    # so it cannot have PRIMARY KEY, AUTOINCREMENT, or FOREIGN KEY.
    cursor.execute('''
    CREATE VIEW Profile AS
    SELECT
        U.user_id,
        U.username,
        U.email,
        -- U.password, -- Consider if you want to expose password in a view for security reasons
        F.form_id,
        F.weight,
        F.height,
        F.age,
        F.blood_type,
        F.diabetes,
        F.blood_pressure,
        F.heart_disease,
        F.medications
    FROM Users AS U
    JOIN Forms AS F ON U.user_id = F.user_id
    ''')

    conn.commit()
    conn.close()
    print("Database 'myapp.db' initialized with Users, Forms tables and Profile view.")

# Example of how to use the initialize_database function
if __name__ == "__main__":
    initialize_database()

    # You can now test inserting data and querying the view
    conn = sqlite3.connect('myapp.db')
    cursor = conn.cursor()

    # Insert a dummy user
    cursor.execute("INSERT INTO Users (username, email, password) VALUES (?, ?, ?)",
                   ('testuser', 'test@example.com', 'hashedpassword'))
    user_id = cursor.lastrowid # Get the ID of the newly inserted user

    # Insert dummy form data for this user
    cursor.execute("INSERT INTO Forms (user_id, weight, height, age, blood_type, diabetes, blood_pressure, heart_disease, medications) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (user_id, '70', '175', '30', 'A+', 1, 0, 1, 'Insulin, Aspirin'))
    conn.commit()

    # Query the Profile view
    print("\nQuerying the Profile view:")
    cursor.execute("SELECT * FROM Profile WHERE user_id = ?", (user_id,))
    profile_data = cursor.fetchone()

    if profile_data:
        print(f"Profile Data for user_id {profile_data[0]}:")
        print(f"  Username: {profile_data[1]}")
        print(f"  Email: {profile_data[2]}")
        print(f"  Form ID: {profile_data[3]}")
        print(f"  Weight: {profile_data[4]}kg")
        print(f"  Height: {profile_data[5]}cm")
        print(f"  Age: {profile_data[6]}")
        print(f"  Blood Type: {profile_data[7]}")
        print(f"  Diabetes: {'Yes' if profile_data[8] else 'No'}")
        print(f"  Blood Pressure: {'Yes' if profile_data[9] else 'No'}")
        print(f"  Heart Disease: {'Yes' if profile_data[10] else 'No'}")
        print(f"  Medications: {profile_data[11]}")
    else:
        print("No profile data found for this user.")

    conn.close()
import sqlite3

DATABASE = "database/academic.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():

    connection = get_connection()
    cursor = connection.cursor()

    # -----------------------------
    # Students Table
    # -----------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            semester INTEGER NOT NULL
        )
    """)

    # -----------------------------
    # Faculty Table
    # -----------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS faculty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL
        )
    """)

    # -----------------------------
    # Courses Table
    # -----------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_code TEXT UNIQUE NOT NULL,
            course_name TEXT NOT NULL,
            credits INTEGER NOT NULL,
            faculty_id INTEGER,
            FOREIGN KEY (faculty_id)
            REFERENCES faculty(id)
        )
    """)

    # -----------------------------
    # Enrollments Table
    # -----------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            semester INTEGER NOT NULL,
            FOREIGN KEY (student_id)
            REFERENCES students(id),
            FOREIGN KEY (course_id)
            REFERENCES courses(id),
            UNIQUE(student_id, course_id, semester)
        )
    """)

    # -----------------------------
    # Grades Table
    # -----------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            grade TEXT NOT NULL,
            grade_point REAL NOT NULL,
            FOREIGN KEY (student_id)
            REFERENCES students(id),
            FOREIGN KEY (course_id)
            REFERENCES courses(id),
            UNIQUE(student_id, course_id)
        )
    """)

    connection.commit()
    connection.close()
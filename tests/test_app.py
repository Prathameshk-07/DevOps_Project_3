import os
import sys
import sqlite3
import pytest

# Allow Python to find the app folder
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from app.app import app
from app.database import initialize_database


# -----------------------------
# Test Database Fixture
# -----------------------------

@pytest.fixture
def client(tmp_path):

    # Create a temporary database
    test_database = tmp_path / "test_academic.db"

    # Change database location for testing
    import app.database as database

    database.DATABASE = str(test_database)

    # Initialize tables
    initialize_database()

    # Flask testing mode
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


# -----------------------------
# Health API Test
# -----------------------------

def test_health(client):

    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "healthy"


# -----------------------------
# Student Creation Test
# -----------------------------

def test_create_student(client):

    response = client.post(
        "/api/students",
        json={
            "name": "Test Student",
            "email": "test@example.com",
            "department": "AI-ML",
            "semester": 2
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "Student created successfully"


# -----------------------------
# Course Creation Test
# -----------------------------

def test_create_course(client):

    response = client.post(
        "/api/courses",
        json={
            "course_code": "TEST101",
            "course_name": "Test Course",
            "credits": 4
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "Course created successfully"


# -----------------------------
# Enrollment Test
# -----------------------------

def test_create_enrollment(client):

    # Create student
    student_response = client.post(
        "/api/students",
        json={
            "name": "Enrollment Student",
            "email": "enrollment@example.com",
            "department": "AI-ML",
            "semester": 2
        }
    )

    student_id = student_response.get_json()["student_id"]

    # Create course
    course_response = client.post(
        "/api/courses",
        json={
            "course_code": "ENR101",
            "course_name": "Enrollment Course",
            "credits": 4
        }
    )

    course_id = course_response.get_json()["course_id"]

    # Create enrollment
    response = client.post(
        "/api/enrollments",
        json={
            "student_id": student_id,
            "course_id": course_id,
            "semester": 2
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "Enrollment successful"
    assert data["total_credits"] == 4


# -----------------------------
# Grade Test
# -----------------------------

def test_create_grade(client):

    # Create student
    student_response = client.post(
        "/api/students",
        json={
            "name": "Grade Student",
            "email": "grade@example.com",
            "department": "AI-ML",
            "semester": 2
        }
    )

    student_id = student_response.get_json()["student_id"]

    # Create course
    course_response = client.post(
        "/api/courses",
        json={
            "course_code": "GRD101",
            "course_name": "Grade Course",
            "credits": 4
        }
    )

    course_id = course_response.get_json()["course_id"]

    # Enroll student
    client.post(
        "/api/enrollments",
        json={
            "student_id": student_id,
            "course_id": course_id,
            "semester": 2
        }
    )

    # Create grade
    response = client.post(
        "/api/grades",
        json={
            "student_id": student_id,
            "course_id": course_id,
            "grade": "A",
            "grade_point": 9
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["message"] == "Grade created successfully"


# -----------------------------
# GPA Calculation Test
# -----------------------------

def test_gpa_calculation(client):

    # Create student
    student_response = client.post(
        "/api/students",
        json={
            "name": "GPA Student",
            "email": "gpa@example.com",
            "department": "AI-ML",
            "semester": 2
        }
    )

    student_id = student_response.get_json()["student_id"]

    # Create course
    course_response = client.post(
        "/api/courses",
        json={
            "course_code": "GPA101",
            "course_name": "GPA Course",
            "credits": 4
        }
    )

    course_id = course_response.get_json()["course_id"]

    # Enroll student
    client.post(
        "/api/enrollments",
        json={
            "student_id": student_id,
            "course_id": course_id,
            "semester": 2
        }
    )

    # Add grade point 9
    client.post(
        "/api/grades",
        json={
            "student_id": student_id,
            "course_id": course_id,
            "grade": "A",
            "grade_point": 9
        }
    )

    # Calculate GPA
    response = client.get(
        f"/api/students/{student_id}/gpa"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["gpa"] == 9.0
    assert data["total_credits"] == 4


# -----------------------------
# Student Not Found Test
# -----------------------------

def test_student_not_found(client):

    response = client.get(
        "/api/students/99999/gpa"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["error"] == "Student not found"
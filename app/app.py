from flask import Flask, jsonify, request

from app.database import initialize_database, get_connection

# ---------------------------------
# Flask Application
# ---------------------------------

app = Flask(__name__)


# ---------------------------------
# Initialize Database
# ---------------------------------

initialize_database()


# =================================
# HOME
# =================================

@app.route("/")
def home():
    return "Student Academic Management Platform"


# =================================
# HEALTH CHECK
# =================================

@app.route("/api/health")
def health():
    return jsonify({
        "status": "healthy",
        "application": "Student Academic Management Platform"
    })


# =================================
# STUDENTS
# =================================

# Create Student
@app.route("/api/students", methods=["POST"])
def create_student():

    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    department = data.get("department")
    semester = data.get("semester")

    if not name or not email or not department or not semester:
        return jsonify({
            "error": "All fields are required"
        }), 400

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO students
            (name, email, department, semester)
            VALUES (?, ?, ?, ?)
        """, (
            name,
            email,
            department,
            semester
        ))

        connection.commit()

        student_id = cursor.lastrowid

        return jsonify({
            "message": "Student created successfully",
            "student_id": student_id
        }), 201

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:

        connection.close()


# Get Students
@app.route("/api/students", methods=["GET"])
def get_students():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM students
    """)

    students = cursor.fetchall()

    connection.close()

    student_list = []

    for student in students:

        student_list.append({
            "id": student["id"],
            "name": student["name"],
            "email": student["email"],
            "department": student["department"],
            "semester": student["semester"]
        })

    return jsonify(student_list)


# =================================
# FACULTY
# =================================

# Create Faculty
@app.route("/api/faculty", methods=["POST"])
def create_faculty():

    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    department = data.get("department")

    if not name or not email or not department:
        return jsonify({
            "error": "All fields are required"
        }), 400

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO faculty
            (name, email, department)
            VALUES (?, ?, ?)
        """, (
            name,
            email,
            department
        ))

        connection.commit()

        faculty_id = cursor.lastrowid

        return jsonify({
            "message": "Faculty created successfully",
            "faculty_id": faculty_id
        }), 201

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:

        connection.close()


# Get Faculty
@app.route("/api/faculty", methods=["GET"])
def get_faculty():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM faculty
    """)

    faculty_members = cursor.fetchall()

    connection.close()

    faculty_list = []

    for faculty in faculty_members:

        faculty_list.append({
            "id": faculty["id"],
            "name": faculty["name"],
            "email": faculty["email"],
            "department": faculty["department"]
        })

    return jsonify(faculty_list)


# =================================
# COURSES
# =================================

# Create Course
@app.route("/api/courses", methods=["POST"])
def create_course():

    data = request.get_json()

    course_code = data.get("course_code")
    course_name = data.get("course_name")
    credits = data.get("credits")
    faculty_id = data.get("faculty_id")

    if not course_code or not course_name or not credits:
        return jsonify({
            "error": "Course code, course name and credits are required"
        }), 400

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO courses
            (course_code, course_name, credits, faculty_id)
            VALUES (?, ?, ?, ?)
        """, (
            course_code,
            course_name,
            credits,
            faculty_id
        ))

        connection.commit()

        course_id = cursor.lastrowid

        return jsonify({
            "message": "Course created successfully",
            "course_id": course_id
        }), 201

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 400

    finally:

        connection.close()


# Get Courses
@app.route("/api/courses", methods=["GET"])
def get_courses():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            courses.id,
            courses.course_code,
            courses.course_name,
            courses.credits,
            courses.faculty_id,
            faculty.name AS faculty_name
        FROM courses
        LEFT JOIN faculty
        ON courses.faculty_id = faculty.id
    """)

    courses = cursor.fetchall()

    connection.close()

    course_list = []

    for course in courses:

        course_list.append({
            "id": course["id"],
            "course_code": course["course_code"],
            "course_name": course["course_name"],
            "credits": course["credits"],
            "faculty_id": course["faculty_id"],
            "faculty_name": course["faculty_name"]
        })

    return jsonify(course_list)
# =================================
# ENROLLMENTS
# =================================

# Create Enrollment
@app.route("/api/enrollments", methods=["POST"])
def create_enrollment():

    data = request.get_json()

    student_id = data.get("student_id")
    course_id = data.get("course_id")
    semester = data.get("semester")

    # Check required fields
    if not student_id or not course_id or not semester:
        return jsonify({
            "error": "Student ID, course ID and semester are required"
        }), 400

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # Check whether student exists
        cursor.execute(
            "SELECT * FROM students WHERE id = ?",
            (student_id,)
        )

        student = cursor.fetchone()

        if not student:
            return jsonify({
                "error": "Student not found"
            }), 404

        # Check whether course exists
        cursor.execute(
            "SELECT * FROM courses WHERE id = ?",
            (course_id,)
        )

        course = cursor.fetchone()

        if not course:
            return jsonify({
                "error": "Course not found"
            }), 404

        # Calculate current credits
        cursor.execute("""
            SELECT COALESCE(SUM(courses.credits), 0) AS total_credits
            FROM enrollments
            JOIN courses
            ON enrollments.course_id = courses.id
            WHERE enrollments.student_id = ?
            AND enrollments.semester = ?
        """, (
            student_id,
            semester
        ))

        result = cursor.fetchone()

        current_credits = result["total_credits"]

        # Calculate new total credits
        new_total = current_credits + course["credits"]

        # Maximum 18 credits per semester
        if new_total > 18:
            return jsonify({
                "error": "Credit limit exceeded",
                "current_credits": current_credits,
                "course_credits": course["credits"],
                "maximum_credits": 18
            }), 400

        # Create enrollment
        cursor.execute("""
            INSERT INTO enrollments
            (student_id, course_id, semester)
            VALUES (?, ?, ?)
        """, (
            student_id,
            course_id,
            semester
        ))

        connection.commit()

        enrollment_id = cursor.lastrowid

        return jsonify({
            "message": "Enrollment successful",
            "enrollment_id": enrollment_id,
            "total_credits": new_total
        }), 201

    except Exception as e:

        connection.rollback()

        return jsonify({
            "error": str(e)
        }), 400

    finally:

        connection.close()


# Get Enrollments
@app.route("/api/enrollments", methods=["GET"])
def get_enrollments():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            enrollments.id,
            enrollments.student_id,
            students.name AS student_name,
            enrollments.course_id,
            courses.course_code,
            courses.course_name,
            courses.credits,
            enrollments.semester

        FROM enrollments

        JOIN students
        ON enrollments.student_id = students.id

        JOIN courses
        ON enrollments.course_id = courses.id
    """)

    enrollments = cursor.fetchall()

    connection.close()

    enrollment_list = []

    for enrollment in enrollments:

        enrollment_list.append({
            "id": enrollment["id"],
            "student_id": enrollment["student_id"],
            "student_name": enrollment["student_name"],
            "course_id": enrollment["course_id"],
            "course_code": enrollment["course_code"],
            "course_name": enrollment["course_name"],
            "credits": enrollment["credits"],
            "semester": enrollment["semester"]
        })

    return jsonify(enrollment_list)
# -----------------------------
# Grades - Create
# -----------------------------

@app.route("/api/grades", methods=["POST"])
def create_grade():

    data = request.get_json()

    student_id = data.get("student_id")
    course_id = data.get("course_id")
    grade = data.get("grade")
    grade_point = data.get("grade_point")

    if not student_id or not course_id or not grade or grade_point is None:
        return jsonify({
            "error": "Student ID, course ID, grade and grade point are required"
        }), 400

    connection = get_connection()
    cursor = connection.cursor()

    try:

        # Check student
        cursor.execute(
            "SELECT * FROM students WHERE id = ?",
            (student_id,)
        )

        student = cursor.fetchone()

        if not student:
            return jsonify({
                "error": "Student not found"
            }), 404

        # Check course
        cursor.execute(
            "SELECT * FROM courses WHERE id = ?",
            (course_id,)
        )

        course = cursor.fetchone()

        if not course:
            return jsonify({
                "error": "Course not found"
            }), 404

        # Check enrollment
        cursor.execute("""
            SELECT *
            FROM enrollments
            WHERE student_id = ?
            AND course_id = ?
        """, (student_id, course_id))

        enrollment = cursor.fetchone()

        if not enrollment:
            return jsonify({
                "error": "Student is not enrolled in this course"
            }), 400

        # Insert grade
        cursor.execute("""
            INSERT INTO grades
            (student_id, course_id, grade, grade_point)
            VALUES (?, ?, ?, ?)
        """, (
            student_id,
            course_id,
            grade,
            grade_point
        ))

        connection.commit()

        grade_id = cursor.lastrowid

        return jsonify({
            "message": "Grade created successfully",
            "grade_id": grade_id
        }), 201

    except Exception as e:

        connection.rollback()

        return jsonify({
            "error": str(e)
        }), 400

    finally:
        connection.close()


# -----------------------------
# Grades - Get All
# -----------------------------

@app.route("/api/grades", methods=["GET"])
def get_grades():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            grades.id,
            grades.student_id,
            students.name AS student_name,
            grades.course_id,
            courses.course_code,
            courses.course_name,
            courses.credits,
            grades.grade,
            grades.grade_point

        FROM grades

        JOIN students
        ON grades.student_id = students.id

        JOIN courses
        ON grades.course_id = courses.id
    """)

    grades = cursor.fetchall()

    connection.close()

    grade_list = []

    for grade in grades:

        grade_list.append({
            "id": grade["id"],
            "student_id": grade["student_id"],
            "student_name": grade["student_name"],
            "course_id": grade["course_id"],
            "course_code": grade["course_code"],
            "course_name": grade["course_name"],
            "credits": grade["credits"],
            "grade": grade["grade"],
            "grade_point": grade["grade_point"]
        })

    return jsonify(grade_list)
# -----------------------------
# -----------------------------
# GPA Calculation
# -----------------------------

@app.route("/api/students/<int:student_id>/gpa", methods=["GET"])
def calculate_gpa(student_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    )

    student = cursor.fetchone()

    if not student:
        connection.close()

        return jsonify({
            "error": "Student not found"
        }), 404

    cursor.execute("""
        SELECT
            grades.grade_point,
            courses.credits
        FROM grades
        JOIN courses
        ON grades.course_id = courses.id
        WHERE grades.student_id = ?
    """, (student_id,))

    records = cursor.fetchall()

    connection.close()

    if not records:
        return jsonify({
            "student_id": student_id,
            "student_name": student["name"],
            "message": "No grades available",
            "gpa": 0
        })

    total_points = 0
    total_credits = 0

    for record in records:
        total_points += record["grade_point"] * record["credits"]
        total_credits += record["credits"]

    gpa = total_points / total_credits

    return jsonify({
        "student_id": student_id,
        "student_name": student["name"],
        "total_credits": total_credits,
        "total_grade_points": total_points,
        "gpa": round(gpa, 2)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

# =================================
# RUN APPLICATION
# =================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
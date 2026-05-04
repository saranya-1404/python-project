from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(name,
template_folder="templates")
app.secret_key = "secretkey"

------------------ DATABASE ------------------
def get_db():
return sqlite3.connect("database.db")

------------------ LOGIN ------------------
def get_student(student_id):
db = get_db()
cursor = db.cursor()
cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
return cursor.fetchone()

@app.route("/menu")
def menu_page():
if "student_id" not in session:
return redirect("/")
return render_template("menu.html")

------------------ FEES ------------------
def get_fees(student_id):
db = get_db()
cursor = db.cursor()
cursor.execute("SELECT * FROM fees WHERE student_id=?", (student_id,))
return cursor.fetchone()

------------------ MARKS ------------------
def get_marks(student_id):
db = get_db()
cursor = db.cursor()
cursor.execute("SELECT * FROM marks WHERE student_id=?", (student_id,))
return cursor.fetchall()

------------------ ATTENDANCE ------------------
def get_attendance(student_id):
db = get_db()
cursor = db.cursor()
cursor.execute("SELECT * FROM attendance WHERE student_id=?", (student_id,))
return cursor.fetchall()

------------------ TIMETABLE ------------------
def get_timetable():
db = get_db()
cursor = db.cursor()
cursor.execute("SELECT * FROM timetable")
return cursor.fetchall()

------------------ GRADE LOGIC ------------------
def get_grade(avg):
if avg >= 90:
return 10
elif avg >= 80:
return 9
elif avg >= 70:
return 8
elif avg >= 60:
return 7
elif avg >= 50:
return 6
else:
return 0

def get_grade_letter(mark):
if mark >= 90:
return "O"
elif mark >= 80:
return "A"
elif mark >= 70:
return "B"
elif mark >= 60:
return "C"
elif mark >= 50:
return "D"
else:
return "F"

------------------ SGPA ------------------
def calculate_sgpa(marks):
semester_data = {}

for m in marks:
    subject = m[1]
    mid = m[2]
    sem = m[3]
    year = m[4]
    credits = m[5]

    key = str(year)

    avg = (mid + sem) / 2
    grade, gp = get_grade(avg)

    if key not in semester_data:
        semester_data[key] = {"points": 0, "credits": 0}

    semester_data[key]["points"] += gp * credits
    semester_data[key]["credits"] += credits

sgpa_result = {}
for k in semester_data:
    pts = semester_data[k]["points"]
    cr = semester_data[k]["credits"]
    sgpa_result[k] = round(pts / cr, 2) if cr != 0 else 0

return sgpa_result
------------------ COMPLAINT ------------------
def add_complaint(student_id, text):
db = get_db()
cursor = db.cursor()
cursor.execute("INSERT INTO complaints(student_id, text) VALUES (?,?)",
(student_id, text))
db.commit()

================== ROUTES ==================
@app.route("/", methods=["GET", "POST"])
def login():
if request.method == "POST":
student_id = request.form["student_id"]
student = get_student(student_id)

    if student:
        session["student_id"] = student_id
        return redirect("/menu")
    else:
        return "Invalid ID"

return render_template("login.html")
@app.route("/dashboard")
def dashboard():
if "student_id" not in session:
return redirect("/")

student_id = session["student_id"]

student = get_student(student_id)
fees = get_fees(student_id)
marks = get_marks(student_id)
attendance = get_attendance(student_id)
timetable = get_timetable()
sgpa = calculate_sgpa(marks)

return render_template("dashboard.html",
                       student=student,
                       fees=fees,
                       marks=marks,
                       attendance=attendance,
                       timetable=timetable,
                       sgpa=sgpa)
@app.route("/complaint", methods=["GET", "POST"])
def complaint():
if "student_id" not in session:
return redirect("/")

if request.method == "POST":
    text = request.form["complaint"]
    add_complaint(session["student_id"], text)
    return "Complaint submitted!"

return render_template("complaint.html")
@app.route("/revaluation", methods=["POST"])
def revaluation():
selected_subjects = request.form.getlist("subjects")
return f"Revaluation requested for: {', '.join(selected_subjects)}"

@app.route("/logout")
def logout():
session.pop("student_id", None)
return redirect("/")

@app.route("/menu")
def menu():
if "student_id" not in session:
return redirect("/")
return render_template("menu.html")

@app.route("/fees")
def fees_page():
student_id = session["student_id"]

db = get_db()
cursor = db.cursor()

# -------- GET STUDENT DETAILS --------
cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
student = cursor.fetchone()

name = student[1]
year = student[2]
course = student[3]
stype = student[4]      # dayscholar / hosteller
transport = student[5]  # 0 or 1

# -------- GET FEES DATA --------
cursor.execute("SELECT * FROM fees WHERE student_id=?", (student_id,))
fees = cursor.fetchone()

tuition = fees[1]
hostel_fee = fees[2]
bus_fee = fees[3]
paid = fees[4]

# -------- CALCULATE TOTAL --------
total = tuition

if stype == "hosteller":
    total += hostel_fee

if stype == "dayscholar" and transport == 1:
    total += bus_fee

pending = total - paid

# -------- SEND TO HTML --------
return render_template(
    "fees.html",
    name=name,
    year=year,
    course=course,
    stype=stype,
    tuition=tuition,
    hostel_fee=hostel_fee,
    bus_fee=bus_fee,
    paid=paid,
    total=total,
    pending=pending
)
@app.route("/attendance")
def attendance_page():
student_id = session["student_id"]
attendance = get_attendance(student_id)
return render_template("attendance.html", attendance=attendance)

from collections import defaultdict

from collections import defaultdict

from collections import defaultdict

@app.route("/marks")
def marks_page():
student_id = session["student_id"]
year = int(request.args.get("year", 2026))

db = get_db()
cursor = db.cursor()

# -------- FETCH MARKS --------
cursor.execute("SELECT * FROM marks WHERE student_id=? AND year=?", (student_id, year))
marks = cursor.fetchall()

# -------- GROUP BY SEMESTER --------
semester_data = defaultdict(list)

for m in marks:
    semester = m[5]
    semester_data[semester].append(m)

# -------- SGPA --------
total = 0
credits = 0

for m in marks:
    total_marks = m[2] + m[3]
    gp = get_grade(total_marks)
    credit = int(m[6])

    total += gp * credit
    credits += credit

sgpa = round(total / credits, 2) if credits else 0

# -------- CGPA --------
cursor.execute("SELECT * FROM marks WHERE student_id=?", (student_id,))
all_marks = cursor.fetchall()

total_all = 0
credits_all = 0

for m in all_marks:
    total_marks = m[2] + m[3]
    gp = get_grade(total_marks)
    credit = int(m[6])

    total_all += gp * credit
    credits_all += credit

cgpa = round(total_all / credits_all, 2) if credits_all else 0

# -------- YEARS --------
cursor.execute("SELECT DISTINCT year FROM marks WHERE student_id=?", (student_id,))
years = sorted([y[0] for y in cursor.fetchall()], reverse=True)

return render_template(
    "marks.html",
    semester_data=semester_data,
    marks=marks,
    year=year,
    sgpa=sgpa,
    cgpa=cgpa,
    years=years,
    get_grade_letter=get_grade_letter
)
@app.route("/timetable")
def timetable_page():
student_id = session["student_id"]

db = get_db()
cursor = db.cursor()

# -------- STUDENT DETAILS --------
cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
student = cursor.fetchone()

name = student[1]
year = student[2]
course = student[3]

# -------- TIMETABLE DATA --------
cursor.execute("SELECT * FROM timetable")
data = cursor.fetchall()

timetable = {}
days = set()
times = set()

for row in data:
    day, time, subject, lecturer = row

    days.add(day)
    times.add(time)

    if time not in timetable:
        timetable[time] = {}

    timetable[time][day] = f"{subject} ({lecturer})"

days = sorted(days)
times = sorted(times)

return render_template(
    "timetable.html",
    timetable=timetable,
    days=days,
    times=times,
    name=name,
    year=year,
    course=course
)
from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.pagesizes import letter

@app.route("/receipt")
def download_receipt():
student_id = session["student_id"]

db = get_db()
cursor = db.cursor()

cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
student = cursor.fetchone()

cursor.execute("SELECT * FROM payments WHERE student_id=?", (student_id,))
payments = cursor.fetchall()

file_path = "receipt.pdf"

doc = SimpleDocTemplate(file_path, pagesize=letter)

content = []

content.append(Paragraph(f"Student Name: {student[1]}", None))
content.append(Paragraph(f"Student ID: {student[0]}", None))

for p in payments:
    content.append(Paragraph(
        f"{p[2]} Fee Paid: {p[3]} on {p[4]}", None
    ))

doc.build(content)

return send_file(file_path, as_attachment=True)
if name == "main":
app.run(debug=True)

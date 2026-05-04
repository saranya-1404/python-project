import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

---------------- STUDENTS ----------------
c.execute("""CREATE TABLE students(
id TEXT PRIMARY KEY,
name TEXT,
year INTEGER,
course TEXT,
type TEXT,
transport INTEGER
)""")

---------------- FEES ----------------
c.execute("""CREATE TABLE fees(
student_id TEXT,
tuition INTEGER,
hostel INTEGER,
transport_fee INTEGER,
paid_tuition INTEGER,
paid_hostel INTEGER,
paid_transport INTEGER
)""")

---------------- MARKS ----------------
c.execute("""CREATE TABLE marks(
student_id TEXT,
subject TEXT,
mid INTEGER,
sem INTEGER,
year INTEGER,
semester INTEGER,
credits INTEGER
)""")

---------------- ATTENDANCE ----------------
c.execute("""CREATE TABLE attendance(
student_id TEXT,
subject TEXT,
attended INTEGER,
total INTEGER
)""")

---------------- TIMETABLE ----------------
c.execute("""CREATE TABLE timetable(
day TEXT,
time TEXT,
subject TEXT,
lecturer TEXT
)""")

---------------- COMPLAINTS ----------------
c.execute("""CREATE TABLE complaints(
student_id TEXT,
text TEXT
)""")

---------------- PAYMENTS (NEW) ----------------
c.execute("""CREATE TABLE payments(
id INTEGER PRIMARY KEY AUTOINCREMENT,
student_id TEXT,
fee_type TEXT,
amount INTEGER,
date TEXT
)""")

conn.commit()
conn.close()

print("Database created successfully!")

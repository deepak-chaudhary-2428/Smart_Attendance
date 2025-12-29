from flask import Flask, render_template, request, redirect, session
import mysql.connector
from datetime import date

app = Flask(__name__)
app.secret_key = "attendance_secret"

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="smart_attendance"
    )

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "admin":
            session["user"] = "admin"
            return redirect("/home")
    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user" not in session:
        return redirect("/")

    con = get_db()
    cur = con.cursor(dictionary=True)

    if request.method == "POST":
        # ADD student
        if "name" in request.form and request.form["name"].strip() != "":
            cur.execute(
                "INSERT INTO students (name) VALUES (%s)",
                (request.form["name"],)
            )

        # REMOVE student
        if "delete_id" in request.form:
            sid = request.form["delete_id"]
            cur.execute("DELETE FROM attendance WHERE student_id = %s", (sid,))
            cur.execute("DELETE FROM students WHERE id = %s", (sid,))

        con.commit()

    cur.execute("SELECT * FROM students")
    students = cur.fetchall()
    con.close()

    return render_template("dashboard.html", students=students)

@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    if "user" not in session:
        return redirect("/")

    con = get_db()
    cur = con.cursor(dictionary=True)

    # get all students
    cur.execute("SELECT * FROM students")
    students = cur.fetchall()

    if request.method == "POST":
        today = date.today()
        records = []

        for s in students:
            status = request.form.get(str(s["id"]))

            cur.execute(
                "INSERT INTO attendance (student_id, status, date) VALUES (%s, %s, %s)",
                (s["id"], status, today)
            )

            # store for result page
            records.append({
                "name": s["name"],
                "status": status
            })

        con.commit()
        con.close()

        # 👉 open NEW page after submission
        return render_template(
            "attendance_result.html",
            records=records
        )

    return render_template("attendance.html", students=students)


@app.route("/select")
def select():
    if "user" not in session:
        return redirect("/")

    return render_template("select.html")

@app.route("/s_class")
def s_class():
    if "user" not in session:
        return redirect("/")

    return render_template("s_class.html")

@app.route("/s1_class")
def s1_class():
    if "user" not in session:
        return redirect("/")

    return render_template("s1_class.html")

@app.route("/home")
def home():
    return render_template("home.html")


app.run(debug=True)

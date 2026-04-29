from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from datetime import datetime, timedelta

app = Flask(__name__)

app.secret_key = "60f98ce0bd038fa832506f52146fbed5fb46096b9295dc49276d5232a66a0513"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_NAME = os.path.join(BASE_DIR, "smart_reminder.db")

# Opens a connection to the SQLite database and returns rows like dictionaries.
def get_db_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection

# Creates the reminders table if it does not already exist.
def create_database():
    connection = sqlite3.connect(DATABASE_NAME)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device_id TEXT NOT NULL,
            form_type TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            reminder_date TEXT,
            reminder_time TEXT,
            priority TEXT,
            status TEXT DEFAULT 'Pending',
            health_type TEXT,
            dosage TEXT,
            doctor_name TEXT,
            fitness_activity TEXT,
            fitness_duration TEXT,
            fitness_goal TEXT,
            work_task_type TEXT,
            work_deadline TEXT,
            work_notes TEXT,
            relationship_person TEXT,
            relationship_occasion TEXT,
            relationship_follow_up TEXT,
            custom_field TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Users table for simple auth
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


# ---------- Authentication helpers and routes ----------
def get_current_device_id():
    # prefer logged-in user's device id (username), then query/form param
    return session.get("device_id") or session.get("username") or request.args.get("device_id") or request.form.get("device_id")

def get_user_by_username(username):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    return user

def create_user(username, password):
    password_hash = generate_password_hash(password)
    conn = get_db_connection()
    try:
        conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, password_hash))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return False

    conn.close()
    return True

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("username"):
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            flash("Username and password required.")
            return render_template("register.html")

        success = create_user(username, password)
        if not success:
            flash("Username already taken.")
            return render_template("register.html")

        session["username"] = username
        session["device_id"] = username
        return redirect(url_for("home"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = get_user_by_username(username)
        if user and check_password_hash(user["password_hash"], password):
            session["username"] = username
            session["device_id"] = username
            next_url = request.args.get("next") or url_for("home")
            return redirect(next_url)
        flash("Invalid username or password.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("device_id", None)
    return redirect(url_for("home"))

# ---------- End auth helpers ----------

# Displays the home page with a dashboard of reminders for the current browser/device.
@app.route("/")
def home():
    device_id = get_current_device_id()
    connection = get_db_connection()
    status_filter = request.args.get("filter", "all")
    category_filter = request.args.get("category", "all")

    query = "SELECT * FROM reminders WHERE device_id = ?"
    params = [device_id]

    if status_filter == "completed":
        query += " AND status = ?"
        params.append("Completed")
    elif status_filter == "pending":
        query += " AND status != ?"
        params.append("Completed")

    if category_filter != "all":
        query += " AND form_type = ?"
        params.append(category_filter)

    query += " ORDER BY created_at DESC"

    if device_id:
        reminders = connection.execute(query, params).fetchall()
    else:
        reminders = []

    connection.close()

    now = datetime.now()
    soon = now + timedelta(hours=24)

    due_soon = []
    overdue = []

    for reminder in reminders:
        if reminder["reminder_date"] and reminder["status"] != "Completed":
            try:
                reminder_time = datetime.fromisoformat(reminder["reminder_date"])

                if now <= reminder_time <= soon:
                    due_soon.append(reminder)
                elif reminder_time < now:
                    overdue.append(reminder)

            except ValueError:
                pass

    return render_template(
        "index.html",
        reminders=reminders,
        device_id=device_id,
        status_filter=status_filter,
        category_filter=category_filter,
        due_soon=due_soon,
        overdue=overdue
    )

# Displays the about page with project information.
@app.route("/about")
def about():
    return render_template("about.html")

# Displays the reminder form and saves submitted reminders to the database.
@app.route("/add", methods=["GET", "POST"])
@login_required
def add_reminder():
    if request.method == "POST":
        device_id = get_current_device_id()
        form_type = request.form.get("form_type")
        title = request.form.get("title")
        description = request.form.get("description")
        reminder_date = request.form.get("reminder_date")
        reminder_time = request.form.get("reminder_time")
        priority = request.form.get("priority")

        health_type = request.form.get("health_type")
        dosage = request.form.get("dosage")
        doctor_name = request.form.get("doctor_name")

        fitness_activity = request.form.get("fitness_activity")
        fitness_duration = request.form.get("fitness_duration")
        fitness_goal = request.form.get("fitness_goal")

        work_task_type = request.form.get("work_task_type")
        work_deadline = request.form.get("work_deadline")
        work_notes = request.form.get("work_notes")

        relationship_person = request.form.get("relationship_person")
        relationship_occasion = request.form.get("relationship_occasion")
        relationship_follow_up = request.form.get("relationship_follow_up")

        custom_field = request.form.get("custom_field")

        connection = get_db_connection()
        connection.execute("""
            INSERT INTO reminders (
                device_id, form_type, title, description, reminder_date, reminder_time,
                priority, health_type, dosage, doctor_name,
                fitness_activity, fitness_duration, fitness_goal,
                work_task_type, work_deadline, work_notes,
                relationship_person, relationship_occasion, relationship_follow_up,
                custom_field
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            device_id, form_type, title, description, reminder_date, reminder_time,
            priority, health_type, dosage, doctor_name,
            fitness_activity, fitness_duration, fitness_goal,
            work_task_type, work_deadline, work_notes,
            relationship_person, relationship_occasion, relationship_follow_up,
            custom_field
        ))

        connection.commit()
        connection.close()

        return redirect(url_for("home"))

    return render_template("add_reminder.html")

# Marks a reminder as completed and returns the user to their reminder list.
@app.route("/complete/<int:reminder_id>", methods=["POST"])
@login_required
def complete_reminder(reminder_id):
    device_id = get_current_device_id()
    status_filter = request.args.get("filter", "all")
    category_filter = request.args.get("category", "all")

    connection = get_db_connection()
    connection.execute(
        "UPDATE reminders SET status = ? WHERE id = ? AND device_id = ?",
        ("Completed", reminder_id, device_id)
    )
    connection.commit()
    connection.close()

    return redirect(url_for("home", filter=status_filter, category=category_filter))

# Deletes a reminder and returns the user to their reminder list.
@app.route("/delete/<int:reminder_id>", methods=["POST"])
@login_required
def delete_reminder(reminder_id):
    device_id = get_current_device_id()

    connection = get_db_connection()
    connection.execute(
        "DELETE FROM reminders WHERE id = ? AND device_id = ?",
        (reminder_id, device_id)
    )
    connection.commit()
    connection.close()

    return redirect(url_for("home"))

# Displays an existing reminder and updates it after the edit form is submitted.
@app.route("/edit/<int:reminder_id>", methods=["GET", "POST"])
@login_required
def edit_reminder(reminder_id):
    device_id = get_current_device_id()

    connection = get_db_connection()

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        reminder_date = request.form.get("reminder_date")
        reminder_time = request.form.get("reminder_time")
        priority = request.form.get("priority")
        status = request.form.get("status")

        health_type = request.form.get("health_type")
        dosage = request.form.get("dosage")
        doctor_name = request.form.get("doctor_name")

        fitness_activity = request.form.get("fitness_activity")
        fitness_duration = request.form.get("fitness_duration")
        fitness_goal = request.form.get("fitness_goal")

        work_task_type = request.form.get("work_task_type")
        work_deadline = request.form.get("work_deadline")
        work_notes = request.form.get("work_notes")

        relationship_person = request.form.get("relationship_person")
        relationship_occasion = request.form.get("relationship_occasion")
        relationship_follow_up = request.form.get("relationship_follow_up")

        custom_field = request.form.get("custom_field")

        connection.execute("""
            UPDATE reminders
            SET title = ?, description = ?, reminder_date = ?, reminder_time = ?,
                priority = ?, status = ?,
                health_type = ?, dosage = ?, doctor_name = ?,
                fitness_activity = ?, fitness_duration = ?, fitness_goal = ?,
                work_task_type = ?, work_deadline = ?, work_notes = ?,
                relationship_person = ?, relationship_occasion = ?, relationship_follow_up = ?,
                custom_field = ?
            WHERE id = ? AND device_id = ?
        """, (
            title, description, reminder_date, reminder_time,
            priority, status,
            health_type, dosage, doctor_name,
            fitness_activity, fitness_duration, fitness_goal,
            work_task_type, work_deadline, work_notes,
            relationship_person, relationship_occasion, relationship_follow_up,
            custom_field,
            reminder_id, device_id
        ))

        connection.commit()
        connection.close()

        return redirect(url_for("home"))

    reminder = connection.execute(
        "SELECT * FROM reminders WHERE id = ? AND device_id = ?",
        (reminder_id, device_id)
    ).fetchone()

    connection.close()

    if reminder is None:
        return redirect(url_for("home"))

    return render_template(
        "edit_reminder.html",
        reminder=reminder,
        device_id=device_id
    )

# Displays one reminder with all saved details.
@app.route("/reminder/<int:reminder_id>")
def reminder_detail(reminder_id):
    device_id = get_current_device_id()

    connection = get_db_connection()
    reminder = connection.execute(
        "SELECT * FROM reminders WHERE id = ? AND device_id = ?",
        (reminder_id, device_id)
    ).fetchone()
    connection.close()

    if reminder is None:
        return redirect(url_for("home"))

    return render_template(
        "reminder_detail.html",
        reminder=reminder,
        device_id=device_id
    )

if __name__ == "__main__":
    create_database()
    app.run(debug=True)
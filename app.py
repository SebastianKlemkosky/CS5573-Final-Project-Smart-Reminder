from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE_NAME = "smart_reminder.db"

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

    connection.commit()
    connection.close()

# Displays the home page.
@app.route("/")
def home():
    return render_template("index.html")

# Displays the about page with project information.
@app.route("/about")
def about():
    return render_template("about.html")

# Displays the reminder form and saves submitted reminders to the database.
@app.route("/add", methods=["GET", "POST"])
def add_reminder():
    if request.method == "POST":
        device_id = request.form.get("device_id")
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

        return redirect(url_for("view_reminders", device_id=device_id))

    return render_template("add_reminder.html")

# Displays reminders that belong to the current browser/device.
@app.route("/reminders")
def view_reminders():
    device_id = request.args.get("device_id")

    connection = get_db_connection()

    if device_id:
        reminders = connection.execute(
            "SELECT * FROM reminders WHERE device_id = ? ORDER BY created_at DESC",
            (device_id,)
        ).fetchall()
    else:
        reminders = []

    connection.close()

    return render_template("view_reminders.html", reminders=reminders)


if __name__ == "__main__":
    create_database()
    app.run(debug=True)
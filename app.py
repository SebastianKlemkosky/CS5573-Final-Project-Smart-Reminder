from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/add")
def add_reminder():
    return render_template("add_reminder.html")

@app.route("/reminders")
def view_reminders():
    return render_template("view_reminders.html")

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, session
from database import init_db
from auth import register_user, authenticate_user
from jobs import add_job_application, get_user_applications

app = Flask(__name__)
app.secret_key = "super_secret_session_key_for_seng_project"

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if register_user(username, password):
            return redirect(url_for("login"))
        return "Registration failed. Username might be taken.", 400
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = authenticate_user(username, password)
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        return "Invalid username or password.", 401
    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    user_id = session["user_id"]
    
    if request.method == "POST":
        company_name = request.form.get("company_name")
        position = request.form.get("position")
        status = request.form.get("status")
        application_date = request.form.get("application_date")
        notes = request.form.get("notes")
        
        add_job_application(user_id, company_name, position, status, application_date, notes)
        return redirect(url_for("dashboard"))
        
    status_filter = request.args.get("status")
    applications = get_user_applications(user_id, status_filter)
    return render_template("dashboard.html", username=session["username"], applications=applications, current_filter=status_filter)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .models import User
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("home.home"))
    
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User(username, password)
        if user.login():
            flash("Login successful!", "success")
            return redirect("/")
        flash("Invalid username or password", "danger")
        return redirect(url_for("auth.login"))
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logout successful!", "success")
    return redirect(url_for("auth.login"))

@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        # TODO: gửi email reset nếu tồn tại
        flash("Please check your email to reset password", "info")
        return redirect(url_for("auth.forgot_password"))
    return render_template("forgot_pass.html")

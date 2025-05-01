from flask import Blueprint, render_template, request, redirect, url_for, session, flash
home_bp = Blueprint("home", __name__)
@home_bp.route("/")
@home_bp.route("/home")
def home():
    if not session.get("user"):
        flash("Please log in to continue.", "warning")
        return redirect(url_for("auth.login"))
    
    return render_template("home.html")
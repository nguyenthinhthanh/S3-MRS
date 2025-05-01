from flask import Blueprint, render_template, request, redirect, url_for, session, flash
checkin_bp = Blueprint("checkin", __name__)
@checkin_bp.route("/check-in")
def check_in():
    return redirect(url_for('home.home'))
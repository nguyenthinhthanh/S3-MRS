from flask import Blueprint, render_template, request, redirect, url_for, session, flash
notifications_bp = Blueprint("notifications", __name__)
@notifications_bp.route("/notifications")
def notifications():
    return redirect(url_for('home.home'))
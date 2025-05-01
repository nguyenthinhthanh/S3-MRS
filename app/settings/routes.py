from flask import Blueprint, render_template, request, redirect, url_for, session, flash
settings_bp = Blueprint("settings", __name__)
@settings_bp.route("/settings")
def settings():
    return redirect(url_for('home.home'))
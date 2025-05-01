from flask import Blueprint, render_template, request, redirect, url_for, session, flash
devices_bp = Blueprint("devices", __name__)
@devices_bp.route("/device-management")
def device_management():
    return redirect(url_for('home.home'))
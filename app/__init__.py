from flask import Flask
from app.auth.routes import auth_bp
from app.home.routes import home_bp
from app.reservations.routes import reservations_bp
from app.checkin.routes import checkin_bp
from app.settings.routes import settings_bp
from app.notifications.routes import notifications_bp
from app.devices.routes import devices_bp


def create_app():
    app = Flask(__name__)
    app.secret_key = "secret123"
    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(reservations_bp)
    app.register_blueprint(checkin_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(devices_bp)
    return app

from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 's3mrs_demo_secret'  # dùng cho session

# Dummy user (hard-coded)
USERS = {'student1': 'password123'}

# In-memory spaces data
spaces = [
    {"id": 1, "name": "Room A101", "type": "Group Study",
     "equipment": ["Whiteboard", "Projector", "AC"],
     "status": "available", "reserved_until": None},
    {"id": 2, "name": "Cubicle B202", "type": "Individual Study",
     "equipment": ["Power Outlet", "Lamp"],
     "status": "available", "reserved_until": None},
    {"id": 3, "name": "Room C303", "type": "Group Study",
     "equipment": ["Whiteboard", "Conference Phone"],
     "status": "available", "reserved_until": None},
    {"id": 4, "name": "Cubicle D404", "type": "Individual Study",
     "equipment": ["Power Outlet", "Monitor"],
     "status": "available", "reserved_until": None},
    {"id": 5, "name": "Room E505", "type": "Group Study",
     "equipment": ["Interactive Screen", "AC"],
     "status": "available", "reserved_until": None},
    {"id": 6, "name": "Cubicle F606", "type": "Individual Study",
     "equipment": ["Power Outlet", "Desk Lamp"],
     "status": "occupied",
     "reserved_until": (datetime.now() + timedelta(hours=2)).isoformat()}
]

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if USERS.get(username) == password:
            session['user'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']
        if not username or not password:
            flash('Username and password required', 'error')
        elif password != confirm:
            flash('Passwords do not match', 'error')
        elif username in USERS:
            flash('Username already exists', 'error')
        else:
            USERS[username] = password
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form['username']
        new_pass = request.form['new_password']
        confirm = request.form['confirm_password']
        if username not in USERS:
            flash('Username does not exist', 'error')
        elif not new_pass:
            flash('Password cannot be empty', 'error')
        elif new_pass != confirm:
            flash('Passwords do not match', 'error')
        else:
            USERS[username] = new_pass
            flash('Password updated! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('forgot.html')

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', user=session['user'])

@app.route('/api/spaces')
def get_spaces():
    return jsonify(spaces)

@app.route('/api/reserve', methods=['POST'])
def reserve_space():
    data = request.json
    space_id = data.get("id")
    duration = int(data.get("duration", 60))
    for sp in spaces:
        if sp["id"] == space_id and sp["status"] == "available":
            sp["status"] = "reserved"
            sp["reserved_until"] = (datetime.now() + timedelta(minutes=duration)).isoformat()
            return jsonify({"success": True, "space": sp})
    return jsonify({"success": False, "message": "Space not available"}), 400

@app.route('/api/checkin', methods=['POST'])
def checkin_space():
    data = request.json
    space_id = data.get("id")
    for sp in spaces:
        if sp["id"] == space_id and sp["status"] in ["reserved", "available"]:
            sp["status"] = "occupied"
            return jsonify({"success": True, "space": sp})
    return jsonify({"success": False, "message": "Cannot check-in"}), 400

@app.route('/api/checkout', methods=['POST'])
def checkout_space():
    data = request.json
    space_id = data.get("id")
    for sp in spaces:
        if sp["id"] == space_id:
            sp["status"] = "available"
            sp["reserved_until"] = None
            return jsonify({"success": True, "space": sp})
    return jsonify({"success": False, "message": "Space not found"}), 404

# Page routes
def register_page():
    pass

@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    # Lấy những phòng user đã đặt (status != 'available')
    my_reservations = [sp for sp in spaces if sp['status'] in ('reserved','occupied')]
    return render_template('home.html', reservations=my_reservations, user=session['user'])

@app.route('/reservations', methods=['GET', 'POST'])
def reservations_page():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        action = request.form.get('action')  # 'reserve', 'checkin', 'checkout'
        space_id = int(request.form['space_id'])
        for sp in spaces:
            if sp['id'] == space_id:
                if action == 'reserve' and sp['status'] == 'available':
                    # Lấy thời gian và địa điểm từ form
                    dt_str = request.form.get('datetime')  # định dạng 'YYYY-MM-DDTHH:MM'
                    equipment = request.form.get('equipment')
                    reserved_dt = datetime.fromisoformat(dt_str)
                    sp['status'] = 'reserved'
                    sp['reserved_until'] = reserved_dt.isoformat()
                    sp['equipment'] = equipment
                    flash(f"Reserved {sp['name']} at {reserved_dt.strftime('%Y-%m-%d %H:%M')} in {equipment}", 'success')
                elif action == 'checkin' and sp['status'] == 'reserved':
                    sp['status'] = 'occupied'
                    flash(f"Checked in to {sp['name']}", 'success')
                elif action == 'checkout' and sp['status'] in ('reserved','occupied'):
                    sp['status'] = 'available'
                    sp['reserved_until'] = None
                    # sp.pop('equipment', None)
                    flash(f"Checked out from {sp['name']}", 'success')
                else:
                    flash('Invalid action or wrong state', 'error')
                break
        return redirect(url_for('reservations_page'))

    # DS các không gian có thể đặt: lấy từ spaces
    return render_template('reservations.html', spaces=spaces)

@app.route('/checkin-out')
def checkin_out():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('checkin.html')

@app.route('/devices')
def devices():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('devices.html')

@app.route('/notifications')
def notifications():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('notifications.html')

@app.route('/settings')
def settings():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('settings.html')

if __name__ == "__main__":
    app.run(debug=True)
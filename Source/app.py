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
     "status": "occupied",
     "reserved_until": (datetime.now() + timedelta(hours=1)).isoformat()}
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

if __name__ == "__main__":
    app.run(debug=True)
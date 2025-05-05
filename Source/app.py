from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
from datetime import datetime, timedelta
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from flask import send_file

app = Flask(__name__)
app.secret_key = 's3mrs_demo_secret'  # dùng cho session

# Dummy user (hard-coded)
USERS = {'student1': 'password123'}

# Biến dữ liệu mới để lưu trữ người dùng với tên và vai trò
user_list = {
    'user1': 'Student',
    'user2': 'Teacher'
}
# In-memory spaces data
spaces = [
    {"id": 1, "name": "Room A101", "type": "Group Study",
     "equipment": ["Whiteboard", "Projector", "AC"],
     "status": "available", "reserved_from": None, "reserved_until": None},
    {"id": 2, "name": "Cubicle B202", "type": "Individual Study",
     "equipment": ["Power Outlet", "Lamp"],
     "status": "available", "reserved_from": None, "reserved_until": None},
    {"id": 3, "name": "Room C303", "type": "Group Study",
     "equipment": ["Whiteboard", "Conference Phone"],
     "status": "available", "reserved_from": None, "reserved_until": None},
    {"id": 4, "name": "Cubicle D404", "type": "Individual Study",
     "equipment": ["Power Outlet", "Monitor"],
     "status": "available", "reserved_from": None, "reserved_until": None},
    {"id": 5, "name": "Room E505", "type": "Group Study",
     "equipment": ["Interactive Screen", "AC"],
     "status": "available", "reserved_from": None, "reserved_until": None},
    {"id": 6, "name": "Cubicle F606", "type": "Individual Study",
     "equipment": ["Power Outlet", "Desk Lamp"],
     "status": "occupied", "reserved_from": None,
     "reserved_until": (datetime.now() + timedelta(hours=2)).replace(microsecond=0).isoformat()}
]
now = datetime.now()
RESERVATIONS = {
    1: [
        {
            "username": "student1",
            "start": (now - timedelta(minutes=10)).isoformat(),
            "end": (now + timedelta(minutes=30)).isoformat()
        }
    ],
    2: [
        {
            "username": "admin",
            "start": (now + timedelta(hours=1)).isoformat(),
            "end": (now + timedelta(hours=2)).isoformat()
        }
    ]
}
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if USERS.get(username) == password:
            session['user'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# Register and Forgot Password
@app.route('/register', methods=['POST'])
def register():
    global USERS
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    confirm = request.form.get('confirm', '')

    # Kiểm tra đầu vào
    if not username or not password or not confirm:
        flash('Username, password và confirm đều bắt buộc', 'danger')
    elif password != confirm:
        flash('Passwords do not match', 'danger')
    elif username in USERS:
        flash('Username already exists', 'danger')
    else:
        USERS[username] = password
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    # Nếu lỗi, render lại login.html với tab Register mở
    return redirect(url_for('login'))


@app.route('/forgot', methods=['GET', 'POST'])
def forgot_password():
    # if request.method == 'POST':
    #     username = request.form['username']
    #     new_pass = request.form['new_password']
    #     confirm = request.form['confirm_password']
    #     if username not in USERS:
    #         flash('Username does not exist', 'error')
    #     elif not new_pass:
    #         flash('Password cannot be empty', 'error')
    #     elif new_pass != confirm:
    #         flash('Passwords do not match', 'error')
    #     else:
    #         USERS[username] = new_pass
    #         flash('Password updated! Please log in.', 'success')
    #         return redirect(url_for('login'))
    return render_template('forgot.html')

# User account page
@app.route('/account')
def account():
    if 'user' not in session:
        return redirect(url_for('login'))
    # Lịch sử mọi reservation (đã checkout)
    history = [sp for sp in spaces if sp.get('reserved_from')]
    return render_template('account.html', user=session['user'], reservations_history=history)

@app.route('/')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('home'))

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
                    # nhận start and end
                    start_str = request.form.get('start_datetime')
                    end_str = request.form.get('end_datetime')
                    location = request.form.get('location')
                    sp['reserved_from'] = datetime.fromisoformat(start_str).isoformat()
                    sp['reserved_until'] = datetime.fromisoformat(end_str).isoformat()
                    sp['location'] = location
                    sp['status'] = 'reserved'
                    flash(f"Reserved {sp['name']} from {start_str.replace('T',' ')} to {end_str.replace('T',' ')} at {location}", 'success')
                elif action == 'checkin' and sp['status'] == 'reserved':
                    sp['status'] = 'occupied'
                    flash(f"Checked in to {sp['name']}", 'success')
                elif action == 'checkout' and sp['status'] in ('reserved','occupied'):
                    sp['status'] = 'available'
                    sp['reserved_from'] = None
                    sp['reserved_until'] = None
                    sp['location'] = None
                    flash(f"Cancelled reservation for {sp['name']}", 'success')
                else:
                    flash('Invalid action or wrong state', 'error')
                break
        return redirect(url_for('reservations_page'))

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

    now = datetime.now()
    history = [sp for sp in spaces if sp.get('reserved_from')]
    # Tìm các reservation sắp bắt đầu trong 30 phút tới
    soon = []
    for sp in history:
        start = datetime.fromisoformat(sp['reserved_from'])
        # Nếu start – now <= 30 phút và start > now
        if 0 < (start - now).total_seconds() <= 1800:
            soon.append(sp)

    if soon:
        # Xây dựng message chi tiết
        details = []
        for sp in soon:
            sf = datetime.fromisoformat(sp['reserved_from']).strftime('%Y-%m-%d %H:%M')
            details.append(f"{sp['name']} at {sf}")
        # Nối các chi tiết lại thành 1 chuỗi
        msg = "Sent reminders for: " + "; ".join(details)
        flash(msg, 'info')

    device_alerts = [
        {'device_name': 'Projector A101', 'message': 'Malfunction detected', 'timestamp': '2025-05-04 09:30'},
        {'device_name': 'AC Room C303', 'message': 'Filter needs replacement', 'timestamp': '2025-05-04 08:15'}
    ]
    return render_template('notifications.html',
                            user=session['user'],
                            reservations_history=history,
                            device_alerts=device_alerts,
                            reminders=soon)

@app.route('/settings')
def settings():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('settings.html', users=user_list, spaces=spaces)


@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form['username']
    role = request.form['role']
    if username and role and username not in user_list:
        user_list[username] = role
        flash(f"Đã thêm người dùng '{username}' với vai trò '{role}'.")
    else:
        flash("Không thể thêm người dùng. Có thể tên đã tồn tại hoặc thiếu thông tin.")
    return redirect(url_for('settings'))


@app.route('/edit_user', methods=['POST'])
def edit_user():
    old_username = request.form['old_username']
    new_username = request.form['new_username']
    new_role = request.form['new_role']
    if old_username in user_list:
        del user_list[old_username]
        user_list[new_username] = new_role
        flash(f"Đã cập nhật người dùng '{old_username}' thành '{new_username}' với vai trò '{new_role}'.")
    else:
        flash("Không tìm thấy người dùng cần sửa.")
    return redirect(url_for('settings'))



@app.route('/delete_user', methods=['POST'])
def delete_user():
    username = request.form['username']
    if username in user_list:
        del user_list[username]
        flash(f"Đã xóa người dùng '{username}'.")
    else:
        flash("Không tìm thấy người dùng để xóa.")
    return redirect(url_for('settings'))

@app.route('/export_report', methods=['POST'])
def export_report():
    if 'user' not in session:
        return redirect(url_for('login'))

   
    report_type = request.form.get('report_type')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    format_type = request.form.get('format')

   
    try:
        start = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    except Exception as e:
        flash('Invalid date format', 'error')
        return redirect(url_for('settings'))

    
    data = []
    for space_id, reservations in RESERVATIONS.items():
        space = next((s for s in spaces if s['id'] == space_id), None)
        for r in reservations:
            start_time = datetime.datetime.fromisoformat(r['start'])
            end_time = datetime.datetime.fromisoformat(r['end'])

           
            if start <= start_time <= end:
                data.append({
                    'username': r['username'],
                    'space_name': space['name'] if space else f'Room {space_id}',
                    'start': start_time.strftime('%Y-%m-%d %H:%M'),
                    'end': end_time.strftime('%Y-%m-%d %H:%M')
                })

   
    if format_type == 'pdf':
        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(50, height - 50, "Study Space Usage Report")

        
        pdf.setFont("Helvetica", 12)
        pdf.drawString(50, height - 80, f"Report Type: {report_type}")
        pdf.drawString(50, height - 100, f"From {start_date} to {end_date}")

       
        y = height - 140
        for entry in data:
            if y < 100:
                pdf.showPage()
                y = height - 50
            pdf.drawString(50, y, f"{entry['username']} | {entry['space_name']} | {entry['start']} - {entry['end']}")
            y -= 20

        pdf.save()
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="report.pdf", mimetype='application/pdf')

    return redirect(url_for('settings'))

@app.route('/check-in')
def scan_qr():
    return render_template('scan_qr.html')

@app.route('/check-in/validate-qr')
def validate_qr():
    try:
        room_id = int(request.args.get("room", ""))
    except ValueError:
        flash("Invalid room ID.", "error")
        return redirect("/check-in")

    user = session.get('user')
    if not user:
        flash("User not logged in.", "error")
        return redirect("/check-in")

    now = datetime.now()
    reservations = RESERVATIONS.get(room_id, [])

    match = next((
        r for r in reservations
        if r["username"] == user and
           datetime.fromisoformat(r["start"]) <= now <= datetime.fromisoformat(r["end"])
    ), None)

    if match:
        flash(f"Check-in successful for room {room_id}.", "success")
        return render_template('checkin.html')
    else:
        flash("No valid reservation found or invalid time.", "error")
        return redirect("/check-in")

# Color helper
def status_color(status):
    colors = {
        "dirty": "Dirty",
        "reserved": "Reserved",
        "occupied": "Occupied",
        "available": "Vacant"
    }
    return colors.get(status.lower(), "secondary")

@app.route("/device-management")
def space_list():
    return render_template("device_management.html", spaces=spaces, status_color=status_color)
@app.route('/device-management/room/<int:room_id>')
def view_dashboard(room_id):
    room = next((r for r in spaces if r["id"] == room_id), None)
    if not room:
        return "Room not found", 404
    return render_template('dashboard.html', room=room)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

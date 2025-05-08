from flask import Flask, jsonify, request, render_template, redirect, url_for, session, flash
from datetime import datetime, timedelta
import re

app = Flask(__name__)
app.secret_key = 's3mrs_demo_secret'  # dùng cho session

# Dummy user (hard-coded)
USERS = {'student1': 'password123'}

# Tạo danh sách 7 ngày liên tiếp với định dạng YYYY-MM-DD
days = [(datetime.today() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
# Tạo danh sách giờ từ 08:00 đến 22:00
hours = [f"{h}:00" for h in range(8, 23)]

# In-memory spaces data
spaces = [
    {"id": 1, "name": "Room A101", "type": "Group Study",
     "equipment": ["Whiteboard", "Projector", "AC"],
     "status": "available", "reserved_from": None, "reserved_until": None,
     "capacity": 30},

    {"id": 2, "name": "Cubicle B202", "type": "Individual Study",
     "equipment": ["Power Outlet", "Lamp"],
     "status": "available", "reserved_from": None, "reserved_until": None,
     "total_capacity": 4, "current_reservations": 1},

    {"id": 3, "name": "Room C303", "type": "Group Study",
     "equipment": ["Whiteboard", "Conference Phone"],
     "status": "available", "reserved_from": None, "reserved_until": None,
     "capacity": 25},

    {"id": 4, "name": "Cubicle D404", "type": "Individual Study",
     "equipment": ["Power Outlet", "Monitor"],
     "status": "available", "reserved_from": None, "reserved_until": None,
     "total_capacity": 4, "current_reservations": 2},

    {"id": 5, "name": "Room E505", "type": "Group Study",
     "equipment": ["Interactive Screen", "AC"],
     "status": "occupied", "reserved_from": None, "reserved_until": None,
     "capacity": 35},

    {"id": 6, "name": "Cubicle F606", "type": "Individual Study",
     "equipment": ["Power Outlet", "Desk Lamp"],
     "status": "occupied", "reserved_from": None,
     "reserved_until": (datetime.now() + timedelta(hours=2)).replace(microsecond=0).isoformat(),
     "total_capacity": 4, "current_reservations": 4},

    # Các mục mới cho Building A
    {"id": 7, "name": "Cubicle A102", "type": "Individual Study",
     "equipment": ["Power Outlet", "Lamp"],
     "status": "available", "reserved_from": None, "reserved_until": None,
     "total_capacity": 4, "current_reservations": 0},

    {"id": 8, "name": "Cubicle A103", "type": "Individual Study",
     "equipment": ["Power Outlet", "Lamp"],
     "status": "available", "reserved_from": None, "reserved_until": None,
     "total_capacity": 4, "current_reservations": 1},

    {"id": 9, "name": "Open Space C301", "type": "Open Study Area",
     "equipment": ["Whiteboard", "AC"],
     "status": "available", "reserved_from": None, "reserved_until": None,
     "total_capacity": 50, "current_reservations": 0}
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
    ],
    5: [
        {
            "username": "admin",
            "start": (now).isoformat(),
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
    return render_template('settings.html')

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

def update_spaces_with_reservations():
    """
    Cập nhật trạng thái ban đầu cho các room dựa trên thời gian hiện tại.
    (Chỉ dùng cho việc render ban đầu; các cập nhật sau dựa vào selected time qua AJAX.)
    """
    for room in spaces:
        room_id = room["id"]
        if room_id in RESERVATIONS:
            current_time = datetime.now().isoformat()
            for res in RESERVATIONS[room_id]:
                res_start = res["start"]
                res_end = res["end"]
                if res_start <= current_time <= res_end:
                    room["reserved_from"] = res_start
                    room["reserved_until"] = res_end
                    room["status"] = "reserved"
                    break
                else:
                    room["status"] = "available"

update_spaces_with_reservations()

# ----------------------- Nhóm phòng theo tòa/tầng -----------------------
floors_data = {}
floors_summary = {}

for space in spaces:
    tokens = space["name"].split()
    token_found = None
    for token in tokens[1:]:
        if re.match(r'^[A-Z]\d+', token, re.I):
            token_found = token
            break
    if token_found:
        building_letter = token_found[0].upper()
        floor_num = token_found[1] if len(token_found) > 1 and token_found[1].isdigit() else ""
        floor_key = f"{building_letter}_Floor{floor_num}" if floor_num else f"{building_letter}_Floor"
    else:
        building_letter = space["name"][0].upper()
        floor_key = f"{building_letter}_Floor"
    if floor_key not in floors_data:
        floors_data[floor_key] = []
    floors_data[floor_key].append(space)

for floor, rooms in floors_data.items():
    summary = {}
    for room in rooms:
        rtype = room["type"]
        summary[rtype] = summary.get(rtype, 0) + 1
    floors_summary[floor] = summary

# ----------------------- Routes -----------------------
@app.route('/search-space')
def search_space_page():
    now = datetime.now()
    current_hour = now.hour
    days = [(datetime.today() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    hours = [f"{h}:00" for h in range(current_hour, 22)]
    return render_template("search_space.html", days=days, hours=hours,
                           floors_data=floors_data, floors_summary=floors_summary,
                           reservations=RESERVATIONS)

@app.route('/get-room-info', methods=["GET"])
def get_room_info():
    room_id = request.args.get("room_id", type=int)
    selected_day = request.args.get("day")
    selected_hour = request.args.get("hour")
    selectedDT = None
    if selected_day and selected_hour:
        try:
            selectedDT = datetime.fromisoformat(f"{selected_day}T{selected_hour}")
        except Exception:
            selectedDT = None

    room = next((s for s in spaces if s["id"] == room_id), None)
    if room:
        detail = "<ul>"
        detail += f"<li><strong>Equipment:</strong> {', '.join(room.get('equipment', []))}</li>"
        if room["type"] == "Group Study":
            detail += f"<li><strong>Capacity:</strong> {room.get('capacity')}</li>"
            # Dùng RESERVATIONS trực tiếp cho nhóm Group Study.
            res_data = RESERVATIONS.get(room_id, [])
            matched = None
            if selectedDT:
                for res in res_data:
                    resStart = datetime.fromisoformat(res["start"])
                    resEnd = datetime.fromisoformat(res["end"])
                    if resStart <= selectedDT <= resEnd:
                        matched = res
                        break
            if matched:
                detail += f"<li><strong>Status:</strong> Reserved</li>"
                detail += f"<li><strong>Reserved from:</strong> {matched['start'].replace('T', ' ')}</li>"
                detail += f"<li><strong>Reserved until:</strong> {matched['end'].replace('T', ' ')}</li>"
            else:
                detail += f"<li><strong>Status:</strong> Available</li>"
        else:
            # Với các phòng Individual Study / Open Study Area,
            # hiển thị số đặt / tổng sức chứa nếu có.
            current = 0
            if room_id in RESERVATIONS:
                # Số lượng đặt là số phần tử trong danh sách
                current = len(RESERVATIONS[room_id])
            total = room.get('total_capacity', room.get('capacity', 0))
            detail += f"<li><strong>Bookings:</strong> {current} / {total}</li>"
        detail += "</ul>"
        return detail
    return "No details available", 404

@app.route('/filter-reservations', methods=["GET"])
def filter_reservations():
    selected_day = request.args.get("day")  # Format: YYYY-MM-DD
    selected_hour = request.args.get("hour")  # Format: HH:MM
    if not selected_day or not selected_hour:
         return jsonify([]), 400
    try:
         selected_dt = datetime.fromisoformat(f"{selected_day}T{selected_hour}")
    except Exception as e:
         return jsonify({"error": "Invalid datetime format"}), 400

    filtered = []
    for room in spaces:
         room_id = room["id"]
         if room_id in RESERVATIONS:
             for res in RESERVATIONS[room_id]:
                 res_start = datetime.fromisoformat(res["start"])
                 res_end = datetime.fromisoformat(res["end"])
                 if res_start <= selected_dt <= res_end:
                     filtered.append({
                         "room_id": room_id,
                         "room_name": room["name"],
                         "start": res["start"],
                         "end": res["end"],
                         "status": room["status"],
                         "username": res["username"]
                     })
    return jsonify(filtered)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime, timedelta

reservations_bp = Blueprint("reservation", __name__)
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
@reservations_bp.route('/reservations', methods=['GET', 'POST'])
def reservations_page():
    if 'user' not in session:
        return redirect(url_for('auth.login'))

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
        return redirect(url_for('reservation.reservations_page'))

    # DS các không gian có thể đặt: lấy từ spaces
    return render_template('reservations.html', spaces=spaces)

@reservations_bp.route('/api/spaces')
def get_spaces():
    return jsonify(spaces)

@reservations_bp.route('/api/reserve', methods=['POST'])
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

@reservations_bp.route('/api/checkin', methods=['POST'])
def checkin_space():
    data = request.json
    space_id = data.get("id")
    for sp in spaces:
        if sp["id"] == space_id and sp["status"] in ["reserved", "available"]:
            sp["status"] = "occupied"
            return jsonify({"success": True, "space": sp})
    return jsonify({"success": False, "message": "Cannot check-in"}), 400

@reservations_bp.route('/api/checkout', methods=['POST'])
def checkout_space():
    data = request.json
    space_id = data.get("id")
    for sp in spaces:
        if sp["id"] == space_id:
            sp["status"] = "available"
            sp["reserved_until"] = None
            return jsonify({"success": True, "space": sp})
    return jsonify({"success": False, "message": "Space not found"}), 404
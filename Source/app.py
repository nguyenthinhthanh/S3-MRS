from flask import Flask, jsonify, request, render_template
from datetime import datetime, timedelta

app = Flask(__name__)

# In‑memory data store
spaces = [
    {"id": 1, "name": "Room A101", "type": "Group Study",
     "equipment": ["Whiteboard", "Projector", "AC"],
     "status": "available", "reserved_until": None},
    {"id": 2, "name": "Cubicle B202", "type": "Individual Study",
     "equipment": ["Power Outlet", "Lamp"],
     "status": "occupied",
     "reserved_until": (datetime.now() + timedelta(hours=1)).isoformat()}
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/spaces")
def get_spaces():
    return jsonify(spaces)

@app.route("/api/reserve", methods=["POST"])
def reserve_space():
    data = request.json
    space_id = data.get("id")
    duration = int(data.get("duration", 60))  # minutes
    for sp in spaces:
        if sp["id"] == space_id and sp["status"] == "available":
            sp["status"] = "reserved"
            sp["reserved_until"] = (datetime.now() + timedelta(minutes=duration)).isoformat()
            return jsonify({"success": True, "space": sp})
    return jsonify({"success": False, "message": "Space not available"}), 400

@app.route("/api/checkin", methods=["POST"])
def checkin_space():
    data = request.json
    space_id = data.get("id")
    for sp in spaces:
        if sp["id"] == space_id and sp["status"] in ["reserved", "available"]:
            sp["status"] = "occupied"
            return jsonify({"success": True, "space": sp})
    return jsonify({"success": False, "message": "Cannot check-in"}), 400

@app.route("/api/checkout", methods=["POST"])
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
from flask import Flask, request, jsonify, render_template
from models import db, Service, Appointment
from datetime import datetime, timedelta, time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///booking.db'
db.init_app(app)

BUSINESS_START = time(9, 0)
BUSINESS_END = time(17, 0)

with app.app_context():
    db.create_all()
    if Service.query.count() == 0:
        db.session.add_all([
            Service(name="Haircut", duration_minutes=30, price=25),
            Service(name="Beard Trim", duration_minutes=15, price=10),
            Service(name="Haircut + Beard", duration_minutes=45, price=32),
        ])
        db.session.commit()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/services")
def get_services():
    services = Service.query.all()
    return jsonify([{"id": s.id, "name": s.name, "duration_minutes": s.duration_minutes, "price": s.price} for s in services])

@app.route("/api/availability")
def get_availability():
    service_id = request.args.get("service_id", type=int)
    date_str = request.args.get("date")  # expects YYYY-MM-DD
    service = Service.query.get_or_404(service_id)
    day = datetime.strptime(date_str, "%Y-%m-%d").date()

    slots = []
    current = datetime.combine(day, BUSINESS_START)
    end = datetime.combine(day, BUSINESS_END)
    duration = timedelta(minutes=service.duration_minutes)

    booked = Appointment.query.filter(
        Appointment.status == "booked",
        db.func.date(Appointment.start_time) == day.isoformat()
    ).all()

    while current + duration <= end:
        conflict = any(
            current < b.start_time + timedelta(minutes=b.service.duration_minutes) and
            b.start_time < current + duration
            for b in booked
        )
        if not conflict:
            slots.append(current.strftime("%H:%M"))
        current += timedelta(minutes=15)

    return jsonify(slots)

@app.route("/api/appointments", methods=["POST"])
def create_appointment():
    data = request.get_json()
    appt = Appointment(
        service_id=data["service_id"],
        customer_name=data["customer_name"],
        customer_email=data["customer_email"],
        start_time=datetime.strptime(data["start_time"], "%Y-%m-%d %H:%M"),
    )
    db.session.add(appt)
    db.session.commit()
    return jsonify({"id": appt.id, "status": "booked"}), 201

@app.route("/api/appointments")
def list_appointments():
    appts = Appointment.query.filter_by(status="booked").order_by(Appointment.start_time).all()
    return jsonify([{
        "id": a.id, "service": a.service.name, "customer_name": a.customer_name,
        "start_time": a.start_time.strftime("%Y-%m-%d %H:%M"), "status": a.status
    } for a in appts])

@app.route("/api/appointments/<int:appt_id>/cancel", methods=["POST"])
def cancel_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    appt.status = "cancelled"
    db.session.commit()
    return jsonify({"id": appt.id, "status": "cancelled"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
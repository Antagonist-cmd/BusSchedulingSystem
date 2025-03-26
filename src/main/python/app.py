from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import sessionmaker
from flask import jsonify
from sqlalchemy import func
import json


# ✅ Initialize Flask
app = Flask(__name__)
app.secret_key = "new_secret_key_123"
app.permanent_session_lifetime = timedelta(days=1)

# ✅ PostgreSQL Connection
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres.xoahudvbqmcvdxotkfhe:databasepass243@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ Initialize Extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# ✅ Models
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False)

    def is_active(self):
        return True  # Mark all users as active unless you have a specific 'active' column


class Bus(db.Model):
    __tablename__ = 'buses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    bus_number = db.Column(db.String(50), nullable=False)

class Route(db.Model):
    __tablename__ = 'routes'
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    distance_km = db.Column(db.Integer, nullable=False)
    coordinates = db.Column(db.Text, nullable=True) 

class Schedule(db.Model):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    bus = db.relationship('Bus', backref=db.backref('schedules', lazy='joined'))
    route = db.relationship('Route', backref=db.backref('schedules', lazy='joined'))
    total_seats = db.Column(db.Integer, nullable=False, default=40)


class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'), nullable=False)
    seat_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False)

    user = db.relationship('User', backref=db.backref('tickets', lazy=True))
    schedule = db.relationship('Schedule', backref=db.backref('tickets', lazy=True))



# ✅ Create Tables
with app.app_context():
    db.create_all()

# ✅ User Loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ✅ Routes
@app.route("/")
def home():
    return render_template("home.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # ✅ Use PBKDF2 for password hashing
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please login.", "success")
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        # ✅ Check using PBKDF2
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('home'))
    
    total_users = User.query.count()
    total_buses = Bus.query.count()
    total_routes = Route.query.count()
    total_schedules = Schedule.query.count()
    total_tickets = Ticket.query.count()
    
    # ✅ Corrected: Use "source" and "destination" instead of "start_location" and "end_location"
    schedules = (
        Schedule.query
        .join(Bus)
        .join(Route)
        .add_columns(
            Schedule.id, Schedule.departure_time, Schedule.arrival_time,
            Bus.name.label("bus_name"), Bus.bus_number,
            Route.source.label("start_location"),  # Fixed column name
            Route.destination.label("end_location")  # Fixed column name
        )
        .all()
    )
    
    recent_tickets = (
        Ticket.query
        .join(User)
        .join(Schedule)
        .join(Bus)
        .join(Route)
        .order_by(Ticket.id.desc())
        .limit(5)
        .all()
    )
    
    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        total_buses=total_buses,
        total_routes=total_routes,
        total_schedules=total_schedules,
        total_tickets=total_tickets,
        recent_tickets=recent_tickets,
        schedules=schedules
    )




@app.route('/admin_access', methods=['GET', 'POST'])
def admin_access():
    if request.method == 'POST':
        admin_key = request.form.get('admin_key')
        if admin_key == "confidentialshit":  # Set your secure key here
            return redirect(url_for('admin_signup'))
        else:
            flash('Invalid admin key!', 'danger')

    return render_template('admin_access.html')

@app.route('/admin_signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        new_admin = User(username=username, password=password, role='admin')
        db.session.add(new_admin)
        db.session.commit()
        flash("Admin account created successfully!", "success")
        return redirect(url_for('login'))

    return render_template('admin_signup.html')

@app.route('/manage_buses')
@login_required
def manage_buses():
    if current_user.role != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('home'))
    
    buses = Bus.query.all()
    return render_template('manage_buses.html', buses=buses)
# ✅ Add a Bus
@app.route('/admin/add_bus', methods=['GET', 'POST'])
@login_required
def add_bus():
    if current_user.role != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':
        name = request.form.get('name')
        capacity = request.form.get('capacity')
        bus_number = request.form.get('bus_number')  # Make sure to handle this

        if name and capacity and bus_number:
            new_bus = Bus(name=name, capacity=int(capacity), bus_number=bus_number)
            db.session.add(new_bus)
            db.session.commit()
            flash("Bus added successfully!", "success")
            return redirect(url_for('manage_buses'))
        else:
            flash("All fields are required!", "danger")

    return render_template('add_bus.html')



# ✅ Edit a Bus
@app.route('/admin/edit_bus/<int:bus_id>', methods=['GET', 'POST'])
@login_required
def edit_bus(bus_id):
    if current_user.role != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('home'))

    bus = Bus.query.get_or_404(bus_id)

    if request.method == 'POST':
        bus.name = request.form.get('name')
        bus.capacity = request.form.get('capacity')
        bus.bus_number = request.form.get('bus_number')  # Add this
        db.session.commit()
        flash("Bus updated successfully!", "success")
        return redirect(url_for('manage_buses'))

    return render_template('edit_bus.html', bus=bus)



# ✅ Delete a Bus
@app.route('/admin/delete_bus/<int:bus_id>', methods=['POST'])
@login_required
def delete_bus(bus_id):
    if current_user.role != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('home'))
    
    bus = Bus.query.get(bus_id)
    if bus:
        db.session.delete(bus)
        db.session.commit()
        flash("Bus deleted successfully!", "success")
    else:
        flash("Bus not found!", "danger")
    
    return redirect(url_for('manage_buses'))



# ✅ View Routes (Admin)
@app.route('/admin/routes')
@login_required
def admin_routes():
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    
    routes = Route.query.all()
    print(routes)  # ✅ Debugging line to confirm routes data is fetched
    
    return render_template('manage_routes.html', routes=routes)


# ✅ Add Route (Admin)
@app.route('/admin/add_route', methods=['GET', 'POST'])
@login_required
def add_route():
    if current_user.role != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':
        source = request.form.get('source')
        destination = request.form.get('destination')
        distance_km = request.form.get('distance_km')

        if source and destination and distance_km:
            new_route = Route(source=source, destination=destination, distance_km=int(distance_km))
            db.session.add(new_route)
            db.session.commit()
            flash("Route added successfully!", "success")
            return redirect(url_for('admin_routes'))
        else:
            flash("All fields are required!", "danger")

    return render_template('add_route.html')

# ✅ Delete Route (Admin)
@app.route('/delete_route/<int:route_id>', methods=['POST'])
@login_required
def delete_route(route_id):
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    
    route = Route.query.get(route_id)
    if route:
        db.session.delete(route)
        db.session.commit()
        flash('Route deleted successfully!', 'success')
    else:
        flash('Route not found!', 'danger')

    return redirect(url_for('manage_routes'))


@app.route('/manage_routes')
@login_required
def manage_routes():
    if current_user.role != 'admin':
        return redirect(url_for('login'))
    routes = Route.query.all()
    return render_template('manage_routes.html', routes=routes)

@app.route('/edit_route/<int:route_id>', methods=['GET', 'POST'])
@login_required
def edit_route(route_id):
    if current_user.role != 'admin':
        return redirect(url_for('login'))

    route = Route.query.get(route_id)
    if request.method == 'POST':
        route.source = request.form['source']
        route.destination = request.form['destination']
        route.distance_km = request.form['distance_km']
        db.session.commit()
        flash('Route updated successfully!', 'success')
        return redirect(url_for('manage_routes'))

    return render_template('edit_route.html', route=route)



@app.route('/user_dashboard')
@login_required
def user_dashboard():
    schedules = db.session.query(
        Schedule.id,
        Bus.name.label("name"),  # ✅ Get bus name from Bus table
        Bus.bus_number,
        Schedule.departure_time,
        Schedule.arrival_time,
        Route.source.label("start_location"),
        Route.destination.label("end_location"),
        Bus.capacity.label("total_seats"),  # ✅ Fetch capacity from Bus table instead
        db.func.count(Ticket.id).label("booked_seats")
    ).join(Bus, Schedule.bus_id == Bus.id  # ✅ Ensure proper join
    ).join(Route, Schedule.route_id == Route.id
    ).outerjoin(Ticket, Schedule.id == Ticket.schedule_id
    ).group_by(Schedule.id, Bus.name, Bus.bus_number, Route.source, Route.destination, Bus.capacity
    ).all()

    # ✅ Convert tuples to dictionaries (Flask cannot directly access tuple fields)
    schedules = [
        {
            "id": row[0],
            "name": row[1],  # ✅ Now accessible in HTML
            "bus_number": row[2],
            "departure_time": row[3],
            "arrival_time": row[4],
            "start_location": row[5],
            "end_location": row[6],
            "total_seats": row[7],  # ✅ Now correctly fetching from Bus table
            "booked_seats": row[8],
            "available_seats": row[7] - row[8]  # ✅ Correct calculation
        }
        for row in schedules
    ]

    return render_template('user_dashboard.html', schedules=schedules)





@app.route('/view_schedules')
@login_required
def view_schedules():
    schedules = db.session.query(
        Schedule.id,
        Bus.name.label("name"),
        Bus.bus_number,
        Schedule.departure_time,
        Schedule.arrival_time,
        Route.source.label("start_location"),
        Route.destination.label("end_location"),
        Schedule.total_seats,  # Ensure this is fetched
        db.func.count(Ticket.id).label("booked_seats")  # Count booked tickets
    ).join(Bus, Schedule.bus_id == Bus.id
    ).join(Route, Schedule.route_id == Route.id
    ).outerjoin(Ticket, Schedule.id == Ticket.schedule_id  # Left join to count tickets
    ).group_by(Schedule.id, Bus.name, Bus.bus_number, Route.source, Route.destination).all()

    return render_template('view_schedules.html', schedules=schedules)




@app.route('/admin/schedules', methods=['GET'])
@login_required
def manage_schedules():
    if current_user.role != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('home'))
    
    schedules = Schedule.query.all()
    buses = Bus.query.all()
    routes = Route.query.all()
    return render_template('manage_schedules.html', schedules=schedules, buses=buses, routes=routes)


@app.route('/admin/add_schedule', methods=['GET', 'POST'])
@login_required
def add_schedule():
    if current_user.role != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('home'))

    if request.method == 'POST':
        bus_id = request.form.get('bus_id')
        route_id = request.form.get('route_id')
        departure_time = request.form.get('departure_time')
        arrival_time = request.form.get('arrival_time')
        price = request.form.get('price')

        if bus_id and route_id and departure_time and arrival_time and price:
            new_schedule = Schedule(
                bus_id=bus_id,
                route_id=route_id,
                departure_time=departure_time,
                arrival_time=arrival_time,
                price=price
            )
            db.session.add(new_schedule)
            db.session.commit()
            flash('Schedule added successfully!', 'success')
            return redirect(url_for('manage_schedules'))
        else:
            flash('All fields are required!', 'danger')

    buses = Bus.query.all()
    routes = Route.query.all()
    return render_template('add_schedule.html', buses=buses, routes=routes)


@app.route('/admin/delete_schedule/<int:schedule_id>', methods=['POST'])
@login_required
def delete_schedule(schedule_id):
    if current_user.role != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('home'))

    schedule = Schedule.query.get(schedule_id)
    if schedule:
        db.session.delete(schedule)
        db.session.commit()
        flash('Schedule deleted successfully!', 'success')
    else:
        flash('Schedule not found!', 'danger')

    return redirect(url_for('manage_schedules'))

@app.route('/book_ticket', methods=['POST'])
@login_required
def book_ticket():
    try:
        schedule_id = request.form.get('schedule_id')
        selected_seats = request.form.getlist('selected_seats')  # Fetch multiple selected seats

        if not schedule_id:
            flash("Invalid schedule selected!", "danger")
            return redirect(url_for('view_schedules'))

        schedule = Schedule.query.get(int(schedule_id))
        if not schedule:
            flash("Schedule not found!", "danger")
            return redirect(url_for('view_schedules'))

        bus = Bus.query.get(schedule.bus_id)
        if not bus:
            flash("Bus information not found!", "danger")
            return redirect(url_for('view_schedules'))

        # Fetch already booked seats
        booked_seats = {seat[0] for seat in db.session.query(Ticket.seat_number)
                        .filter(Ticket.schedule_id == schedule_id).all()}

        # Ensure seats are selected
        if not selected_seats:
            flash("No seats selected!", "danger")
            return redirect(url_for('seat_status', schedule_id=schedule_id, mode='book'))

        selected_seats = request.form.get('selected_seats')
        if selected_seats:
            selected_seats = list(map(int, selected_seats.split(',')))  # Convert comma-separated values to a list
        else:
            selected_seats = []  # Convert to integers

        print(f"Selected Seats: {selected_seats}")    

        # Validate seat selection
        for seat_number in selected_seats:
            if seat_number < 1 or seat_number > bus.capacity:
                flash(f"Invalid seat selection: {seat_number}", "danger")
                return redirect(url_for('seat_status', schedule_id=schedule_id, mode='book'))
            if seat_number in booked_seats:
                flash(f"Seat {seat_number} is already booked!", "danger")
                return redirect(url_for('seat_status', schedule_id=schedule_id, mode='book'))

        # Book each selected seat
        for seat_number in selected_seats:
            new_ticket = Ticket(
                user_id=current_user.id,
                schedule_id=schedule_id,
                seat_number=seat_number,
                status='confirmed'
            )
            db.session.add(new_ticket)

        db.session.commit()
        flash("Tickets booked successfully!", "success")

        # ✅ Redirect to seat status page to show updated seats
        return redirect(url_for('seat_status', schedule_id=schedule_id))

    except Exception as e:
        db.session.rollback()  # Rollback to avoid partial commits
        print(f"Error: {e}")  # Debugging
        flash(f"An error occurred: {e}", "danger")
        return redirect(url_for('view_schedules'))



import random
def generate_seat_number():
    return f"{random.randint(1, 40)}"


@app.route('/my_tickets')
@login_required
def my_tickets():
    tickets = Ticket.query.join(Schedule).join(Bus).filter(Ticket.user_id == current_user.id).all()
    return render_template('my_tickets.html', tickets=tickets)
    tickets = db.session.query(
        Ticket.id,
        Bus.name.label("name"),
        Bus.bus_number,
        Route.source.label("start_location"),
        Route.destination.label("end_location"),
        Schedule.departure_time, Schedule.arrival_time,
        Ticket.seat_number, Ticket.status
    ).join(Schedule, Ticket.schedule_id == Schedule.id) \
     .join(Bus, Schedule.bus_id == Bus.id) \
     .join(Route, Schedule.route_id == Route.id) \
     .filter(Ticket.user_id == current_user.id).all()
    
    return render_template('my_tickets.html', tickets=tickets)


@app.route('/cancel_ticket/<int:ticket_id>', methods=['POST'])
@login_required
def cancel_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if not ticket or ticket.user_id != current_user.id:
        flash("Invalid ticket!", "danger")
        return redirect(url_for('my_tickets'))

    db.session.delete(ticket)
    db.session.commit()

    flash("Ticket cancelled successfully!", "success")
    
    # ✅ Redirect to seat_status to refresh booked seats
    return redirect(url_for('seat_status', schedule_id=ticket.schedule_id))


def generate_seats(schedule_id, bus_id):
    """Generate seats for a schedule based on bus capacity."""
    total_seats = db.session.execute(
        "SELECT total_seats FROM bus WHERE id = :bus_id",
        {"bus_id": bus_id}
    ).fetchone()[0]

    # Insert seats as available
    for seat_number in range(1, total_seats + 1):
        db.session.execute(
            "INSERT INTO ticket_bookings (schedule_id, seat_number) VALUES (:schedule_id, :seat_number)",
            {"schedule_id": schedule_id, "seat_number": seat_number}
        )

    db.session.commit()

from decimal import Decimal  # ✅ Import Decimal for proper conversion

@app.route('/seat_status/<int:schedule_id>')
@login_required
def seat_status(schedule_id):
    mode = request.args.get('mode', 'view')  # Get mode (default: view)

    # Fetch schedule details
    schedule = Schedule.query.filter_by(id=schedule_id).first()
    if not schedule:
        flash("Schedule not found!", "danger")
        return redirect(url_for('view_schedules'))

    # ✅ Fetch correct bus details (fixing total_seats issue)
    bus = Bus.query.filter_by(id=schedule.bus_id).first()
    if not bus:
        flash("Bus not found!", "danger")
        return redirect(url_for('view_schedules'))

    total_seats = bus.capacity  # ✅ Fetch from 'buses' table
    price_per_seat = float(schedule.price)  # ✅ Convert Decimal to float

    # Fetch booked seats
    booked_tickets = Ticket.query.filter_by(schedule_id=schedule_id).all()
    booked_seats = [ticket.seat_number for ticket in booked_tickets]
    booked_count = len(booked_seats)

    # ✅ Generate correct seat layout
    seats = [
        {"seat_number": i + 1, "status": "booked" if (i + 1) in booked_seats else "available"}
        for i in range(total_seats)
    ]

    return render_template(
        'seat_status.html',
        seats=seats,
        schedule_id=schedule_id,
        total_seats=total_seats,
        booked_count=booked_count,
        booked_seats=booked_seats,
        price_per_seat=price_per_seat,
        mode=mode
    )


@app.route('/plan_journey', methods=['GET'])
@login_required
def plan_journey():
    current_station = request.args.get('current_station')
    destination = request.args.get('destination')
    
    if not current_station or not destination:
        flash("Please enter both your current station and destination.", "danger")
        return redirect(url_for('user_dashboard'))
    
    # Query your routes table to find a matching route
    route = Route.query.filter_by(source=current_station, destination=destination).first()
    if not route:
        flash("No direct route found. Please try different stations.", "warning")
        return redirect(url_for('user_dashboard'))
    
    # Get schedules for the route
    schedules = db.session.query(
        Schedule.id,
        Bus.name.label("bus_name"),
        Bus.bus_number,
        Schedule.departure_time,
        Schedule.arrival_time,
        Schedule.price,
        Bus.capacity
    ).join(Bus, Schedule.bus_id == Bus.id
    ).filter(Schedule.route_id == route.id).all()
    
    # Convert schedules to dictionaries for the template
    schedules = [
        {
            "id": row[0],
            "bus_name": row[1],
            "bus_number": row[2],
            "departure_time": row[3],
            "arrival_time": row[4],
            "price": row[5],
            "capacity": row[6]
        }
        for row in schedules
    ]
    
    return render_template('plan_journey.html',
                           current_station=current_station,
                           destination=destination,
                           schedules=schedules)

@app.route('/get_buses', methods=['POST'])
def get_buses():
    source = (request.form.get('source') or "").strip()
    destination = (request.form.get('destination') or "").strip()

    # Query database for matching routes (case-insensitive)
    routes = Route.query.filter(
        func.lower(Route.source) == source.lower(),
        func.lower(Route.destination) == destination.lower()
    ).all()

    if not routes:
        return jsonify({"error": "No routes found"}), 404

    buses = []
    route_coordinates = []

    for route in routes:
        schedules = Schedule.query.filter_by(route_id=route.id).all()
        
        for schedule in schedules:
            bus = Bus.query.get(schedule.bus_id)
            if bus:
                buses.append({
                    "bus_name": bus.name,
                    "departure": schedule.departure_time.strftime("%H:%M"),
                    "arrival": schedule.arrival_time.strftime("%H:%M"),
                    "price": float(schedule.price)
                })

        # Fetch route coordinates
        try:
            if route.coordinates:
                coords = json.loads(route.coordinates) if isinstance(route.coordinates, str) else route.coordinates
                route_coordinates.extend(coords)  # Append instead of overwriting
        except json.JSONDecodeError:
            pass  # Ignore decoding errors

    return jsonify({"buses": buses, "route": route_coordinates})




if __name__ == '__main__':
    app.run(debug=True)

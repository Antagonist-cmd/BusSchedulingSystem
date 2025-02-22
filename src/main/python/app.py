# ✅ Initialize Extensionsfrom flask import Flask, render_template, request, redirect, url_for, flash
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from sqlalchemy import select
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

# ✅ Initialize Flask
app = Flask(__name__)
app.secret_key = "new_secret_key_123"
app.permanent_session_lifetime = timedelta(days=1)

# ✅ Fixed MySQL Connection URI (URL-encoded '@' symbol in password)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:sqlpass%402435@localhost/bus_scheduling_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ Initialize Extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"

# ✅ Models
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)

class Bus(db.Model):
    __tablename__ = 'buses'
    bus_id = db.Column(db.Integer, primary_key=True)
    bus_name = db.Column(db.String(100), nullable=False)
    bus_number = db.Column(db.String(50), unique=True, nullable=False)
    total_seats = db.Column(db.Integer, nullable=False)

class Route(db.Model):
    __tablename__ = 'routes'
    route_id = db.Column(db.Integer, primary_key=True)
    start_location = db.Column(db.String(100), nullable=False)
    end_location = db.Column(db.String(100), nullable=False)

class Schedule(db.Model):
    __tablename__ = 'schedules'
    schedule_id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.bus_id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.route_id'), nullable=False)
    departure_time = db.Column(db.String(50), nullable=False)
    arrival_time = db.Column(db.String(50), nullable=False)

    bus = db.relationship('Bus', backref=db.backref('schedules', lazy=True))
    route = db.relationship('Route', backref=db.backref('schedules', lazy=True))

class Ticket(db.Model):
    __tablename__ = 'tickets'
    ticket_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.schedule_id'), nullable=False)
    seat_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False)

    user = db.relationship('User', backref=db.backref('tickets', lazy=True))
    schedule = db.relationship('Schedule', backref=db.backref('tickets', lazy=True))

# ✅ Create Tables
with app.app_context():
    db.create_all()

# ✅ User Loader for Flask-Login
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
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        new_user = User(username=username, password=password, role='user')
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please login.", "success")
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user:
            print(f"User found: {user.username}")
            print(f"Stored Hash from DB: {user.password}")
            print(f"Entered Password: {password}")

            if bcrypt.check_password_hash(user.password, password):
                print("✅ Password matches!")
                login_user(user)
                flash("Login successful!", "success")

                if hasattr(user, 'role') and user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                return redirect(url_for('user_dashboard'))
            else:
                print("❌ Password does not match!")
        
        flash("Invalid username or password", "danger")

    return render_template('login.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('user_dashboard'))
    return render_template('admin_dashboard.html')

@app.route('/user_dashboard')
@login_required
def user_dashboard():
    schedules = db.session.query(
        Schedule.schedule_id, Bus.bus_name, Bus.bus_number,
        Schedule.departure_time, Schedule.arrival_time,
        Route.start_location, Route.end_location
    ).join(Bus).join(Route).all()

    return render_template('user_dashboard.html', schedules=schedules)

@app.route('/add_bus', methods=['GET', 'POST'])
@login_required
def add_bus():
    if request.method == 'POST':
        new_bus = Bus(
            bus_name=request.form['bus_name'],
            bus_number=request.form['bus_number'],
            total_seats=request.form['total_seats']
        )
        db.session.add(new_bus)
        db.session.commit()
        flash("Bus added successfully!", "success")
        return redirect(url_for('admin_dashboard'))
    return render_template('add_bus.html')

@app.route('/view_schedules')
@login_required
def view_schedules():
    schedules = db.session.query(
        Schedule.schedule_id, Bus.bus_name, Bus.bus_number,
        Schedule.departure_time, Schedule.arrival_time,
        Route.start_location, Route.end_location
    ).join(Bus).join(Route).all()

    return render_template('view_schedules.html', schedules=schedules)

@app.route('/book_ticket', methods=['POST'])
@login_required
def book_ticket():
    schedule_id = request.form.get('schedule_id')
    user_id = current_user.id

    if Ticket.query.filter_by(user_id=user_id, schedule_id=schedule_id).first():
        flash("You have already booked a ticket for this schedule.", "warning")
        return redirect(url_for('user_dashboard'))

    booked_seats = Ticket.query.filter_by(schedule_id=schedule_id).count()
    new_ticket = Ticket(user_id=user_id, schedule_id=schedule_id, seat_number=booked_seats + 1, status='booked')
    db.session.add(new_ticket)
    db.session.commit()

    flash("Ticket booked successfully!", "success")
    return redirect(url_for('my_tickets'))

@app.route('/my_tickets')
@login_required
def my_tickets():
    tickets = db.session.execute(
        select(
            Ticket.ticket_id,
            Ticket.seat_number,
            Ticket.status,
            Schedule.departure_time,
            Schedule.arrival_time,
            Bus.bus_name,
            Route.start_location,
            Route.end_location
        ).join(Schedule, Ticket.schedule_id == Schedule.schedule_id)
         .join(Bus, Schedule.bus_id == Bus.bus_id)
         .join(Route, Schedule.route_id == Route.route_id)
         .filter(Ticket.user_id == current_user.id)
    ).all()

    return render_template('my_tickets.html', tickets=tickets)  # Ensure 'tickets' is passed


@app.route('/cancel_ticket', methods=['POST'])
@login_required
def cancel_ticket():
    ticket_id = request.form.get('ticket_id')
    ticket = Ticket.query.filter_by(ticket_id=ticket_id, user_id=current_user.id).first()

    if ticket:
        db.session.delete(ticket)
        db.session.commit()
        flash("Ticket canceled successfully!", "success")
    else:
        flash("Ticket not found!", "danger")

    return redirect(url_for('my_tickets'))


if __name__ == '__main__':
    app.run(debug=True)

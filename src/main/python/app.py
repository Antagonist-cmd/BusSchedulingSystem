from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash

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
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')

class Bus(db.Model):
    __tablename__ = 'buses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

class Route(db.Model):
    __tablename__ = 'routes'
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    distance_km = db.Column(db.Integer, nullable=False)

class Schedule(db.Model):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    departure_time = db.Column(db.String(50), nullable=False)
    arrival_time = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Numeric, nullable=False)

    bus = db.relationship('Bus', backref=db.backref('schedules', lazy=True))
    route = db.relationship('Route', backref=db.backref('schedules', lazy=True))

class Ticket(db.Model):
    __tablename__ = 'tickets'
    ticket_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedules.id'), nullable=False)
    seat_number = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), nullable=False)

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
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html')

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



@app.route('/user_dashboard')
@login_required
def user_dashboard():
    schedules = db.session.query(
        Schedule.id,
        Bus.name.label("bus_name"),
        Schedule.departure_time, Schedule.arrival_time,
        Route.source, Route.destination
    ).join(Bus).join(Route).all()

    return render_template('user_dashboard.html', schedules=schedules)


@app.route('/view_schedules')
@login_required
def view_schedules():
    schedules = db.session.query(
        Schedule.id,
        Bus.name,
        Schedule.departure_time, Schedule.arrival_time,
        Route.source, Route.destination
    ).join(Bus, Schedule.bus_id == Bus.id).join(Route, Schedule.route_id == Route.id).all()

    return render_template('view_schedules.html', schedules=schedules)

@app.route('/book_ticket', methods=['POST'])
@login_required
def book_ticket():
    try:
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
    except Exception as e:
        flash(f"Error booking ticket: {e}", "danger")

    return redirect(url_for('my_tickets'))


@app.route('/my_tickets')
@login_required
def my_tickets():
    try:
        tickets = db.session.query(
            Ticket.ticket_id,
            Ticket.seat_number,
            Ticket.status,
            Schedule.departure_time,
            Schedule.arrival_time,
            Bus.name.label("bus_name"),
            Route.source,
            Route.destination
        ).join(Schedule).join(Bus).join(Route).filter(Ticket.user_id == current_user.id).all()
    except Exception as e:
        flash(f"Error fetching tickets: {e}", "danger")
        tickets = []

    return render_template('my_tickets.html', tickets=tickets)

@app.route('/cancel_ticket', methods=['POST'])
@login_required
def cancel_ticket():
    try:
        ticket_id = request.form.get('ticket_id')
        ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()

        if ticket:
            db.session.delete(ticket)
            db.session.commit()
            flash("Ticket canceled successfully!", "success")
        else:
            flash("Ticket not found!", "danger")
    except Exception as e:
        flash(f"Error canceling ticket: {e}", "danger")

    return redirect(url_for('my_tickets'))

if __name__ == '__main__':
    app.run(debug=True)

import csv
from app import db
from models import Bus, Route, Schedule  # Adjust if you have a different structure

def seed_buses():
    with open('buses.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            bus = Bus(
                name=row['name'],
                capacity=int(row['capacity']),
                bus_number=row['bus_number'],
                seat_price=float(row['seat_price'])  # if applicable
            )
            db.session.add(bus)
    db.session.commit()
    print("Buses seeded successfully.")

def seed_routes():
    with open('routes.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            route = Route(
                source=row['source'],
                destination=row['destination'],
                distance_km=int(row['distance_km'])
            )
            db.session.add(route)
    db.session.commit()
    print("Routes seeded successfully.")

def seed_schedules():
    with open('schedules.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            schedule = Schedule(
                bus_id=int(row['bus_id']),
                route_id=int(row['route_id']),
                departure_time=row['departure_time'],  # ensure proper datetime format if needed
                arrival_time=row['arrival_time'],
                price=float(row['price']),
                total_seats=int(row['total_seats'])  # if your schedules table stores this
            )
            db.session.add(schedule)
    db.session.commit()
    print("Schedules seeded successfully.")

if __name__ == "__main__":
    seed_buses()
    seed_routes()
    seed_schedules()

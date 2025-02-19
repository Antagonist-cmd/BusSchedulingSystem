CREATE DATABASE IF NOT EXISTS bus_scheduling_db;
USE bus_scheduling_db;

CREATE TABLE bus (
    id INT PRIMARY KEY AUTO_INCREMENT,
    number VARCHAR(10) NOT NULL UNIQUE,
    capacity INT NOT NULL CHECK (capacity > 0)
);

CREATE TABLE route (
    id INT PRIMARY KEY AUTO_INCREMENT,
    source VARCHAR(50) NOT NULL,
    destination VARCHAR(50) NOT NULL,
    distance_km INT NOT NULL CHECK (distance_km > 0)
);

CREATE TABLE schedule (
    id INT PRIMARY KEY AUTO_INCREMENT,
    bus_id INT NOT NULL,
    route_id INT NOT NULL,
    departure_time TIME NOT NULL,
    arrival_time TIME NOT NULL,
    FOREIGN KEY (bus_id) REFERENCES bus(id) ON DELETE CASCADE,
    FOREIGN KEY (route_id) REFERENCES route(id) ON DELETE CASCADE
);

-- Index for faster lookup
CREATE INDEX idx_route ON route(source, destination);

package main;

import java.sql.*;

public class Main {

    private static Connection conn;

    public static void main(String[] args) {
        try {
            // Establish connection to the database
            conn = DBConnection.connect();  // This line throws SQLException
            System.out.println("Database connected successfully!");

            // Fetch and display all buses
            System.out.println("All Buses:");
            fetchAllBuses();

            // Fetch and display all routes
            System.out.println("\nAll Routes:");
            fetchAllRoutes();

            // Add a new bus to the database
            System.out.println("\nAdding a new bus...");
            addBus("BUS101", 50);

            // Add a new route to the database
            System.out.println("\nAdding a new route...");
            addRoute("New York", "Los Angeles", 4500);

            // Add a new schedule for the bus and route
            System.out.println("\nAdding a new schedule...");
            addSchedule(1, 1, "08:00:00", "18:00:00");

        } catch (SQLException e) {
            System.err.println("Error connecting to the database: " + e.getMessage());
            e.printStackTrace();
        }
    }

    // Method to fetch all buses
    private static void fetchAllBuses() {
        String query = "SELECT * FROM Bus";
        try (Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(query)) {
            while (rs.next()) {
                System.out.println("Bus ID: " + rs.getInt("id") + ", Number: " + rs.getString("number") + ", Capacity: " + rs.getInt("capacity"));
            }
        } catch (SQLException e) {
            System.err.println("Error fetching buses: " + e.getMessage());
        }
    }

    // Method to fetch all routes
    private static void fetchAllRoutes() {
        String query = "SELECT * FROM Route";
        try (Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(query)) {
            while (rs.next()) {
                System.out.println("Route ID: " + rs.getInt("id") + ", Source: " + rs.getString("source") + ", Destination: " + rs.getString("destination") + ", Distance: " + rs.getInt("distance_km"));
            }
        } catch (SQLException e) {
            System.err.println("Error fetching routes: " + e.getMessage());
        }
    }

    // Method to add a bus to the database
    private static void addBus(String number, int capacity) {
        String query = "INSERT INTO Bus (number, capacity) VALUES (?, ?)";
        try (PreparedStatement pstmt = conn.prepareStatement(query)) {
            pstmt.setString(1, number);
            pstmt.setInt(2, capacity);
            int rowsAffected = pstmt.executeUpdate();
            System.out.println("Bus added successfully! Rows affected: " + rowsAffected);
        } catch (SQLException e) {
            System.err.println("Error adding bus: " + e.getMessage());
        }
    }

    // Method to add a route to the database
    private static void addRoute(String source, String destination, int distance) {
        String query = "INSERT INTO Route (source, destination, distance_km) VALUES (?, ?, ?)";
        try (PreparedStatement pstmt = conn.prepareStatement(query)) {
            pstmt.setString(1, source);
            pstmt.setString(2, destination);
            pstmt.setInt(3, distance);
            int rowsAffected = pstmt.executeUpdate();
            System.out.println("Route added successfully! Rows affected: " + rowsAffected);
        } catch (SQLException e) {
            System.err.println("Error adding route: " + e.getMessage());
        }
    }

    // Method to add a schedule to the database
    private static void addSchedule(int busId, int routeId, String departureTime, String arrivalTime) {
        String query = "INSERT INTO Schedule (bus_id, route_id, departure_time, arrival_time) VALUES (?, ?, ?, ?)";
        try (PreparedStatement pstmt = conn.prepareStatement(query)) {
            pstmt.setInt(1, busId);
            pstmt.setInt(2, routeId);
            pstmt.setString(3, departureTime);
            pstmt.setString(4, arrivalTime);
            int rowsAffected = pstmt.executeUpdate();
            System.out.println("Schedule added successfully! Rows affected: " + rowsAffected);
        } catch (SQLException e) {
            System.err.println("Error adding schedule: " + e.getMessage());
        }
    }
}


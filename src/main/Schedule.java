package main;

import java.sql.Time;

public class Schedule {
    private int scheduleId;
    private int busId;
    private int routeId;
    private Time departureTime;
    private Time arrivalTime;

    public Schedule(int scheduleId, int busId, int routeId, Time departureTime, Time arrivalTime) {
        this.scheduleId = scheduleId;
        this.busId = busId;
        this.routeId = routeId;
        this.departureTime = departureTime;
        this.arrivalTime = arrivalTime;
    }

    public void displaySchedule() {
        System.out.println("Schedule ID: " + scheduleId + ", Bus ID: " + busId + ", Route ID: " + routeId + 
            ", Departure: " + departureTime + ", Arrival: " + arrivalTime);
    }
}


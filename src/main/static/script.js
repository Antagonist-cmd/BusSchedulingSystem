// Load data on page load
document.addEventListener("DOMContentLoaded", function () {
    fetchBuses();
    fetchRoutes();
    fetchSchedules();
});

function fetchBuses() {
    fetch("/buses")
        .then(response => response.json())
        .then(buses => {
            let busList = document.getElementById("bus-list");
            let busSelect = document.getElementById("bus-select");

            if (busList) busList.innerHTML = "";
            if (busSelect) busSelect.innerHTML = "";

            buses.forEach(bus => {
                let li = document.createElement("li");
                li.textContent = `Bus ${bus.number} (Capacity: ${bus.capacity})`;
                if (busList) busList.appendChild(li);

                let option = document.createElement("option");
                option.value = bus.id;
                option.textContent = `Bus ${bus.number}`;
                if (busSelect) busSelect.appendChild(option);
            });
        })
        .catch(error => console.error("Error fetching buses:", error));
}

function fetchRoutes() {
    fetch("/routes")
        .then(response => response.json())
        .then(routes => {
            let routeList = document.getElementById("route-list");
            let routeSelect = document.getElementById("route-select");

            if (routeList) routeList.innerHTML = "";
            if (routeSelect) routeSelect.innerHTML = "";

            routes.forEach(route => {
                let li = document.createElement("li");
                li.textContent = `Route: ${route.start_point} → ${route.end_point}`;
                if (routeList) routeList.appendChild(li);

                let option = document.createElement("option");
                option.value = route.id;
                option.textContent = `${route.start_point} → ${route.end_point}`;
                if (routeSelect) routeSelect.appendChild(option);
            });
        })
        .catch(error => console.error("Error fetching routes:", error));
}

function fetchSchedules() {
    fetch("/schedules")
        .then(response => response.json())
        .then(schedules => {
            let scheduleList = document.getElementById("schedule-list");
            if (scheduleList) scheduleList.innerHTML = "";

            schedules.forEach(schedule => {
                let li = document.createElement("li");
                li.textContent = `Bus ${schedule.bus_id} - Route: ${schedule.route_id} - Departure: ${schedule.departure_time}`;
                if (scheduleList) scheduleList.appendChild(li);
            });
        })
        .catch(error => console.error("Error fetching schedules:", error));
}

function addBus() {
    let number = document.getElementById("bus-number").value;
    let capacity = document.getElementById("bus-capacity").value;

    if (!number || !capacity) {
        alert("Please fill in all bus details.");
        return;
    }

    fetch("/buses", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ number, capacity })
    })
        .then(() => fetchBuses())
        .catch(error => console.error("Error adding bus:", error));
}

function addRoute() {
    let start = document.getElementById("route-start").value;
    let end = document.getElementById("route-end").value;

    if (!start || !end) {
        alert("Please enter start and end points.");
        return;
    }

    fetch("/routes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ start_point: start, end_point: end })
    })
        .then(() => fetchRoutes())
        .catch(error => console.error("Error adding route:", error));
}

function assignBus() {
    let busId = document.getElementById("bus-select").value;
    let routeId = document.getElementById("route-select").value;

    if (!busId || !routeId) {
        alert("Please select a bus and a route.");
        return;
    }

    fetch("/assign-bus", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bus_id: busId, route_id: routeId })
    })
        .then(() => alert("Bus assigned to route!"))
        .catch(error => console.error("Error assigning bus:", error));
}

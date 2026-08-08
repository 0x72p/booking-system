let selectedSlot = null;

async function loadServices() {
    const res = await fetch("/api/services");
    const services = await res.json();
    const select = document.getElementById("service");
    services.forEach(s => {
        const opt = document.createElement("option");
        opt.value = s.id;
        opt.textContent = `${s.name} (${s.duration_minutes} min - $${s.price})`;
        select.appendChild(opt);
    });
}

async function loadSlots() {
    const serviceId = document.getElementById("service").value;
    const date = document.getElementById("date").value;
    if (!serviceId || !date) return;

    const res = await fetch(`/api/availability?service_id=${serviceId}&date=${date}`);
    const slots = await res.json();
    const container = document.getElementById("slots");
    container.innerHTML = "";
    selectedSlot = null;

    if (slots.length === 0) {
        container.textContent = "No slots available that day.";
        return;
    }

    slots.forEach(time => {
        const div = document.createElement("div");
        div.className = "slot";
        div.textContent = time;
        div.onclick = () => {
            document.querySelectorAll(".slot").forEach(el => el.classList.remove("selected"));
            div.classList.add("selected");
            selectedSlot = time;
        };
        container.appendChild(div);
    });
}

async function bookAppointment() {
    const serviceId = document.getElementById("service").value;
    const date = document.getElementById("date").value;
    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const message = document.getElementById("message");

    if (!selectedSlot || !name || !email) {
        message.textContent = "Please fill in all fields and pick a time.";
        message.style.color = "red";
        return;
    }

    const res = await fetch("/api/appointments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            service_id: serviceId,
            customer_name: name,
            customer_email: email,
            start_time: `${date} ${selectedSlot}`
        })
    });

    if (res.ok) {
        message.textContent = "Booked! See you then.";
        message.style.color = "green";
        loadSlots();
    } else {
        message.textContent = "Something went wrong.";
        message.style.color = "red";
    }
}

document.getElementById("service").addEventListener("change", loadSlots);
document.getElementById("date").addEventListener("change", loadSlots);

loadServices();
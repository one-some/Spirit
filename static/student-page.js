// Leaderboard
async function fetchLeaderboard(limitf = 25, scoreconditionf = ">0", rankconditionf = ">0", sortf = "points_desc",) {
    const r = await fetch(`/api/students.json?limit=${limitf}&sort=${sortf}&scorecondition=${scoreconditionf}&rankcondition=${rankconditionf}`);
    const j = await r.json();

    for (const el of document.querySelectorAll(`.leaderboard .listing`)) {
        el.remove();
    }

    for (const el of document.querySelectorAll(`.leaderboard`)) {
        let place = 1;
        for (const student of j) {
            renderStudent(el, place, student);
            student.place = place;
            place++;
        }
    }
}

function renderStudent(parent, place, student) {
    const cont = $e("div", parent, { classes: ["listing"] });

    const left = $e("div", cont);
    const right = $e("div", cont);
    $e("span", left, { innerText: place, classes: ["place"] });
    const nameEl = $e("span", left, { innerText: student.name, classes: ["name"] });
    $e("span", left, { innerText: `(${student.grade}th)`, classes: ["grade"] });
    $e("span", right, {
        innerText: student.points.toLocaleString(),
        classes: ["points"],
        title: "Points"
    });

    if (student.name === USERNAME) {
        cont.classList.add("you");
        nameEl.innerText = `${student.name} (You)`;
        $el("#si-place").innerText = `#${place}`;
    }

    cont.addEventListener("click", function () {
        editStudent(student);
    });
}

fetchLeaderboard();

// Events
const eventContainer = $el("#event-container");

function makeEvent(event) {
    const cont = $e("div", eventContainer, { classes: ["listing"], });
    $e("span", cont, { innerText: event.name, classes: ["name"] });
    $e("span", cont, { innerText: event.desc, classes: ["desc"] });
    const bottom = $e("div", cont, { classes: ["event-bottom"] });
    $e("span", bottom, { innerText: event.location, classes: ["location"] });
    const imGoingButton = $e("button", bottom, { innerText: "I'm Going!" });

    let interested = event.interested;
    imGoingButton.classList.toggle("going", interested);

    imGoingButton.addEventListener("click", async function () {
        interested = !interested;
        imGoingButton.classList.toggle("going", interested);
        await fetch(`/api/events/${event.id}/interest.json`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ interested: interested })
        });
    });
}

async function fetchEvents() {
    let r = await fetch("/api/events.json");
    let j = await r.json();

    for (const el of eventContainer.querySelectorAll(".listing")) {
        el.remove();
    }

    for (const event of j) {
        makeEvent(event);
    }
}

fetchEvents();

// Auth
async function Logout() {
    await fetch("/logout");             // Sends for the server which deletes your session and thus logs you out.
    window.location.replace("/login");  // Takes you to the login page.
}
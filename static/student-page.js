// From index.js
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
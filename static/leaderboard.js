const prizeContainer = $el("#prize-container");
const addPrizeCont = $el("#add-prize-cont");

let prizeCommitsLocked = true;
let prizeData;

const LEADERBOARD_DEBUG = false;

async function init() {
    makeInitPrizeColumn();

    let pr = await fetch("/api/prizes.json");
    prizeData = await pr.json();
    updatePrizeModal();
    prizeCommitsLocked = false;

    await fetchStats();
}

function makeInitPrizeColumn() {
    const prize = $e("div", prizeContainer, { id: "add-prize-cont", classes: ["prize"] });
    const addButton = $e("span", prize, { innerText: "add", classes: ["delete-btn", "material-icons"] });
    const nameInput = $e("input", prize, { placeholder: "Name", classes: ["name", "inline-input"] });
    const descInput = $e("input", prize, { placeholder: "Description", classes: ["desc", "inline-input"] });
    const pointsInput = $e("input", prize, { type: "number", placeholder: "Points Required", classes: ["points", "inline-input"] });

    addButton.addEventListener("click", async function () {
        if (!rejectAddAttemptIfBad()) return;
        const newPrize = {
            name: nameInput.value,
            desc: descInput.value,
            points: pointsInput.value,
        }

        const r = await fetch("/api/prize.json", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(newPrize)
        });

        nameInput.value = "";
        descInput.value = "";
        pointsInput.value = "";

        prizeData = await r.json();
        updatePrizeModal();
    });
}

function rejectAddAttemptIfBad() {
    const prizeEl = $el("#add-prize-cont");
    const [nameEl, descEl, pointsEl] = [
        prizeEl.querySelector(".name"),
        prizeEl.querySelector(".desc"),
        prizeEl.querySelector(".points"),
    ];

    let prize = {
        name: cleanUserInput(nameEl.value) || null,
        desc: cleanUserInput(descEl.value) || null,
        points: parseInt(cleanUserInput(pointsEl.value)),
    };

    let dataInvalid = false;

    // Check if data is valid; if not, mark the data as invalid and add a visual marker for the user. 
    if (!prize.name) {
        nameEl.classList.add("bad-input");
        nameEl.setAttribute("old-title", nameEl.getAttribute("title"));
        nameEl.setAttribute("title", "This field is required.");
        dataInvalid = true;
    }

    if (!prize.points && prize.points !== 0) {
        pointsEl.classList.add("bad-input");
        pointsEl.setAttribute("old-title", pointsEl.getAttribute("title"));
        pointsEl.setAttribute("title", "This field is required.");
        dataInvalid = true;
    }

    return !dataInvalid;
}

$el("#draw-prizes-button").addEventListener("click", async function () {
    if (!prizeData.length) {
        if (LEADERBOARD_DEBUG) console.log("No prizes!");
        showModal("no-prizes");
        return;
    }

    updatePrizeModal();

    let r = await fetch("/api/draw_results.json");
    let j = await r.json();

    const modalEl = getModalContent("prize-winners");
    const winnerCont = modalEl.querySelector("#winner-cont")

    winnerCont.innerHTML = "";

    let tDat = [
        ["From", "Name", "Points", "Prize"]
    ];

    for (const [k, v] of Object.entries(j)) {
        let prettyKey = {
            "9": "9th Grade Random Draw",
            "10": "10th Grade Random Draw",
            "11": "11th Grade Random Draw",
            "12": "12th Grade Random Draw",
            "top": "Most Points Accumulated"
        }[k] || "Other";
        tDat.push([prettyKey, v.student.name, v.student.points.toLocaleString(), v.prize]);
    }
    $table(tDat, winnerCont);

    showModal("prize-winners");
});

$el("#add-prizes-button").addEventListener("click", function () {
    closeModals();
    showModal("prize-editor");
});

$el("#edit-prizes-button").addEventListener("click", function () {
    closeModals();
    showModal("prize-editor");
});

function addPrizeRow(prizeId = null, name = "", desc = "", points = null) {
    const prize = $e("div", prizeContainer, { classes: ["prize"] }, { before: addPrizeCont });
    const deleteButton = $e("span", prize, { innerText: "delete", classes: ["delete-btn", "material-icons"] });
    const nameInput = $e("input", prize, { value: name, placeholder: "Name", classes: ["name", "inline-input"] });
    const descInput = $e("input", prize, { value: desc, placeholder: "Description (Optional)", classes: ["desc", "inline-input"] });
    const pointsInput = $e("input", prize, { value: points, type: "number", placeholder: "Points Required", classes: ["points", "inline-input"] });

    for (const input of [nameInput, descInput, pointsInput]) {
        input.addEventListener("change", async function () {
            if (prizeId === null) {
                console.error("Can't edit placeholder (No id)");
                return;
            }

            const newPrize = {
                name: nameInput.value,
                desc: descInput.value,
                points: pointsInput.value,
            }

            const r = await fetch(`/api/prize/${prizeId}.json`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(newPrize)
            });
        });
    }

    deleteButton.addEventListener("click", async function () {
        if (prizeId === null) {
            console.error("Can't delete placeholder");
            return;
        }
        // TODO: Confirmation

        prize.remove();

        // If we removed the last prize we need to add another one. The 1 is to account for the dummy one for adding
        if (document.getElementsByClassName("prize").length === 1) addPrizeRow();

        const r = await fetch(`/api/prize/${prizeId}.json`, {
            method: "DELETE"
        });

        if (r.ok) {
            createNotification("Success", "Prize removed.");
        }
    });
}

function cleanUserInput(input) {
    return input.trim();
}

function getPrizeData() {
    // Returns an array of prizes if data is valid, undefined otherwise.
    let dat = [];
    let dataInvalid = false;

    // Mark all fields visually valid initially
    for (const invalidEl of document.querySelectorAll(".bad-input")) {
        invalidEl.classList.remove("bad-input");
        invalidEl.setAttribute("title", invalidEl.getAttribute("og-title"));
    }

    // Look for data and check validity
    for (const prizeEl of document.querySelectorAll("#prize-container > .prize")) {
        if (prizeEl.id === "add-prize-cont") continue;

        const [nameEl, descEl, pointsEl] = [
            prizeEl.querySelector(".name"),
            prizeEl.querySelector(".desc"),
            prizeEl.querySelector(".points"),
        ];

        let prize = {
            name: cleanUserInput(nameEl.value) || null,
            desc: cleanUserInput(descEl.value) || null,
            points: parseInt(cleanUserInput(pointsEl.value)),
        };

        // Check if data is valid; if not, mark the data as invalid and add a visual marker for the user. 
        if (!prize.name) {
            nameEl.classList.add("bad-input");
            nameEl.setAttribute("old-title", nameEl.getAttribute("title"));
            nameEl.setAttribute("title", "This field is required.");
            dataInvalid = true;
        }

        if (!prize.points && prize.points !== 0) {
            pointsEl.classList.add("bad-input");
            pointsEl.setAttribute("old-title", pointsEl.getAttribute("title"));
            pointsEl.setAttribute("title", "This field is required.");
            dataInvalid = true;
        }

        dat.push(prize);
    }

    if (LEADERBOARD_DEBUG) console.table(dat);

    if (dataInvalid) return undefined;

    return dat;
}

function updatePrizeModal() {
    // Delete old
    for (const prizeEl of document.querySelectorAll(".prize")) {
        if (prizeEl.id === "add-prize-cont") continue;
        prizeEl.remove();
    }

    let prizesAdded = 0;
    for (const prize of prizeData) {
        if (LEADERBOARD_DEBUG) console.log("Adding prizes to modal:", prize);
        addPrizeRow(prizesAdded, prize.name, prize.desc, prize.points_required);
        prizesAdded++;
    }

    if (!prizesAdded) addPrizeRow();
}

function formatGradeNum(num) {
    return `${num}th Grade`;
}

async function fetchStats() {
    let r = await fetch("/api/stats.json");
    let j = await r.json();

    const options = {
        animated: false,
        // responsive: true,
    }

    const colors = [
        "#ef9991",
        "#c0ea91",
        "#90c7d1",
        "#c683e6",
    ];

    for (const chart of [
        { id: "att-ratio-by-grade", type: "bar", key: "attendance_ratio_by_grade", label: "Attendance Percentage", map: x => Math.ceil(x * 100) },
        { id: "avg-att-by-grade", type: "bar", key: "avg_attendances_by_grade", label: "Average Attendance Count", map: x => x.toFixed(2) },
        { id: "points-by-grade", type: "pie", key: "points_by_grade", label: "Points By Grade", map: x => x.toFixed(2) },
    ]) {
        const canvas = $el(`#ch-${chart.id}`);
        canvas.style.height = "150px";
        new Chart(
            canvas,
            {
                type: chart.type,
                data: {
                    labels: Object.keys(j[chart.key]).map(formatGradeNum),
                    datasets: [
                        {
                            label: chart.label,
                            data: Object.values(j[chart.key]).map(chart.map),
                            backgroundColor: colors
                        }
                    ]
                },
                options: options,
            }
        );
    }
}

init();

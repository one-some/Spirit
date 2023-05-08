const prizeContainer = $el("#prize-container");
const addPrizeCont = $el("#add-prize-cont");

let prizeCommitsLocked = true;
let prizeData;

const LEADERBOARD_DEBUG = false;

async function init() {
    let pr = await fetch("/api/prizes.json");
    prizeData = await pr.json();
    updatePrizeModal();
    prizeCommitsLocked = false;

    await fetchStats();
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

function addPrizeRow(name = "", desc = "", points = null) {
    tryCommitPrizeData();

    const prize = $e("div", prizeContainer, { classes: ["prize"] }, { before: addPrizeCont });
    const deleteButton = $e("span", prize, { innerText: "delete", classes: ["delete-btn", "material-icons"] });
    const nameInput = $e("input", prize, { value: name, placeholder: "Name", classes: ["name", "inline-input"] });
    const descInput = $e("input", prize, { value: desc, placeholder: "Description", classes: ["desc", "inline-input"] });
    const pointsInput = $e("input", prize, { value: points, type: "number", placeholder: "Points Required", classes: ["points", "inline-input"] });

    for (const input of [nameInput, descInput, pointsInput]) {
        input.addEventListener("change", function () {
            if (LEADERBOARD_DEBUG) console.log("ouch");
            tryCommitPrizeData();
        });
    }

    deleteButton.addEventListener("click", function () {
        // TODO: Confirmation

        prize.remove();

        // If we removed the last prize we need to add another one. The 1 is to account for the dummy one for adding
        if (document.getElementsByClassName("prize").length === 1) addPrizeRow();

        tryCommitPrizeData();
    });
}

$el("#add-prize-cont .delete-btn").addEventListener("click", () => addPrizeRow());

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

async function tryCommitPrizeData() {
    let dat = getPrizeData();

    // Prevent data races and other issues.
    // Wow Gavin, that's really racist.
    if (prizeCommitsLocked) return;

    // Data is invalid, return.
    if (!dat) return;

    if (LEADERBOARD_DEBUG) console.log("Pushing", dat);

    await fetch("/api/set_prizes.json", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(dat)
    });
}

function updatePrizeModal() {
    let prizesAdded = 0;

    // Delete old
    for (const prizeEl of document.querySelectorAll(".prize")) {
        if (prizeEl.id === "add-prize-cont") continue;
        prizeEl.remove();
    }

    for (const prize of prizeData) {
        if (LEADERBOARD_DEBUG) console.log("Adding prizes to modal:", prize);
        addPrizeRow(prize.name, prize.desc, prize.points_required);
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
        "#540a03",
        "#2e5403",
        "#034654",
        "#3a0354",
    ]

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

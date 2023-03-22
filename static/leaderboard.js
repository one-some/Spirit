const leaderboard = $el("#leaderboard");
const prizeContainer = $el("#prize-container");
const addPrizeCont = $el("#add-prize-cont");

async function init() {
    let r = await fetch("/api/students.json?limit=25&sort=points_desc");
    let j = await r.json();

    let place = 1;
    for (const student of j) {
        renderStudent(leaderboard, place, student)
        place++;
    }
}

$el("#draw-prizes-button").addEventListener("click", async function () {
    let pr = await fetch("/api/prizes.json");
    let prizes = await pr.json();

    if (!prizes.length) {
        console.log("No prizes!");
        showModal("no-prizes");
        return;
    }

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

function addPrizeRow() {
    tryCommitPrizeData();

    const prize = $e("div", prizeContainer, { classes: ["prize"] }, { before: addPrizeCont });
    const deleteButton = $e("span", prize, { innerText: "delete", classes: ["delete-btn", "material-icons"] });
    const nameInput = $e("input", prize, { placeholder: "Name", classes: ["name", "inline-input"] });
    const descInput = $e("input", prize, { placeholder: "Description", classes: ["desc", "inline-input"] });
    const pointsInput = $e("input", prize, { type: "number", placeholder: "Points Required", classes: ["points", "inline-input"] });

    for (const input of [nameInput, descInput, pointsInput]) {
        input.addEventListener("change", function() {
            console.log("ouch");
            tryCommitPrizeData();
        });
    }

    deleteButton.addEventListener("click", function() {
        // TODO: Confirmation

        prize.remove();

        // If we removed the last prize we need to add another one. The 1 is to account for the dummy one for adding
        if (document.getElementsByClassName("prize").length === 1) addPrizeRow();

        tryCommitPrizeData();
    });
}

$el("#add-prize-cont .delete-btn").addEventListener("click", addPrizeRow);

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

    console.table(dat);

    if (dataInvalid) return undefined;

    return dat;
}

function tryCommitPrizeData() {
    let dat = getPrizeData();

    // Data is invalid, return.
    if (!dat) return;

    console.log("Pushing", dat);
}

addPrizeRow();
init();

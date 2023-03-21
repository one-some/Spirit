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

$el("#add-prize-cont .delete-btn").addEventListener("click", function () {
    const prize = $e("div", prizeContainer, { classes: ["prize"] }, { before: addPrizeCont });
    const deleteButton = $e("span", prize, { innerText: "delete", classes: ["delete-btn", "material-icons"] });
    const nameInput = $e("input", prize, { placeholder: "Name", classes: ["name", "inline-input"] });
    const descInput = $e("input", prize, { placeholder: "Description", classes: ["desc", "inline-input"] });
    const pointsInput = $e("input", prize, { type: "number", placeholder: "Points Required", classes: ["points", "inline-input"] });
});

init();

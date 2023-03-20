const leaderboard = $el("#leaderboard");

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

$el("#add-prizes-button").addEventListener("click", function() {
    closeModals();
    showModal("prize-editor");
});

init();

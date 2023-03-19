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

init();

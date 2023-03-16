const miniLeaderboard = $el("#mini-leaderboard");

function makeEntry(place, name, grade, points) {
    console.log(name, grade, points);
    const cont = $e("div", miniLeaderboard, { classes: ["listing"] });
    $e("span", cont, { innerText: place, classes: ["place"] });
    $e("span", cont, { innerText: name, classes: ["name"] });
    $e("span", cont, { innerText: grade, classes: ["grade"] });
    $e("span", cont, { innerText: points, classes: ["points"] });
}


async function init() {
    let r = await fetch("/api/students.json?limit=25&sort=points_desc");
    let j = await r.json();
    console.log(j);

    let place = 1;
    for (const student of j) {
        makeEntry(place, student.name, student.grade, student.points);
        place++;
    }
}

init();
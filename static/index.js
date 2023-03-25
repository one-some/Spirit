// TODO: Account
const USER_NAME = "John";

const miniLeaderboard = $el("#mini-leaderboard");

function renderStudent(parent, place, student) {
    const cont = $e("div", parent, { classes: ["listing"] });
    const left = $e("div", cont);
    const right = $e("div", cont);
    $e("span", left, { innerText: place, classes: ["place"] });
    $e("span", left, { innerText: student.name, classes: ["name"] });
    $e("span", left, { innerText: `(${student.grade}th)`, classes: ["grade"] });
    $e("span", right, {
        innerText: student.points.toLocaleString(),
        classes: ["points"],
        title: "Points"
    });
}

async function initLeaderboard() {
    let r = await fetch("/api/students.json?limit=25&sort=points_desc");
    let j = await r.json();

    let place = 1;
    for (const student of j) {
        renderStudent(miniLeaderboard, place, student);
        place++;
    }
}

async function init() {
    initLeaderboard();
}

init();


// Greeting
// TODO: Actually have correct time
let greetingPossibilities = ["Good afternoon, %s", "Welcome, %s", "Greetings, %s"];
let greeting = greetingPossibilities[Math.floor(Math.random() * greetingPossibilities.length)].replaceAll("%s", USER_NAME);
$el("#greeting").innerText = greeting;
// TODO: Account
const USER_NAME = "Mr. Doe";

const leaderboard = $el("#leaderboard")
const miniLeaderboard = $el("#mini-leaderboard");
const leaderboardStudents = $el("#mini-leaderboard-students");
const studentViewer = $el('.student-viewer');
const studentEditorButtons = $el('#student-editor-buttons');
const studentCreatorButtons = $el("#student-creator-buttons");
const studentDefaultButtons = $el("#student-default-buttons");
const deleteStudentModal = $el("#confirm-delete");

studentEditorButtons.style.display = "none";
studentCreatorButtons.style.display = "none";

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
    cont.addEventListener("click", function () {
        editStudent(student);
    })
}

let currentStudent;

function editStudent(studentData) {

    studentEditorButtons.style.display = "block"
    if(greyed === false){
        currentStudent = studentData;
        studentViewer.querySelector("#student-name").value = studentData.name;
        studentViewer.querySelector("#student-points").value = studentData.points;
        studentViewer.querySelector("#student-grade").value = studentData.grade;
        studentDefaultButtons.querySelector("#add-student").style.backgroundColor = "grey";
        studentDefaultButtons.querySelector("#delete").style.backgroundColor = "grey";
        studentDefaultButtons.querySelector("#batch-add").style.backgroundColor = "grey";
        greyed = true;
    }
}




async function fetchLeaderboard() {
    let r = await fetch("/api/students.json?limit=25&sort=points_desc");
    let j = await r.json();

    for (const el of document.querySelectorAll("#mini-leaderboard .listing")) {
        el.remove();
    }

    for (const el of document.querySelectorAll("#leaderboard .listing")) {
        el.remove();
    }

    let place = 1;
    for (const student of j) {
        // We should consider using flask for this instead.
        renderStudent(miniLeaderboard, place, student);
        renderStudent(leaderboard, place, student);
        renderStudent(leaderboardStudents, place, student);
        student.place = place;
        place++;
    }
}

async function init() {
    fetchLeaderboard();
}

init();


// Greeting
// TODO: Actually have correct time
let greetingPossibilities = ["Good afternoon, %s", "Welcome, %s", "Greetings, %s"];
let greeting = greetingPossibilities[Math.floor(Math.random() * greetingPossibilities.length)].replaceAll("%s", USER_NAME);
$el("#greeting").innerText = greeting;

// TODO: Account
// const USER_NAME = "Mr. Doe";
const logoutbutton = $el("#logout");
const leaderboard = $el("#leaderboard")
const miniLeaderboard = $el("#mini-leaderboard");
const leaderboardStudents = $el("#mini-leaderboard-students");
const studentViewer = $el('.student-viewer');
const studentEditorButtons = $el('#student-editor-buttons');
const studentCreatorButtons = $el("#student-creator-buttons");
const studentDefaultButtons = $el("#student-default-buttons");
const deleteStudentModal = $el("#confirm-delete");
const batchAddModal = $el("#batch-add");

const sortButton = $el("#dropdown");

sortButton.addEventListener("click", function () {
    sortButton.querySelector(".dropdown-content").style.display = "block";
})

document.addEventListener("click", (function(event) { 
    var $target = $(event.target);
    if(!$target.closest('#dropdown').length && 
    $('.dropdown-content').is(":visible")) {
      $('.dropdown-content').hide();
    }        
  }))

function applyFilters () {
    tempScore = document.getElementById("score").closest("#score").value;
    let patterna = /^[><=][0-9][0-9]*$/;
    let patternb = /^[><]=[0-9][0-9]*$/;


    if (tempScore.match(patterna) || tempScore.match(patternb)){
        scoreCondition = tempScore
    }
    else if(tempScore == ""){}//do nothing if no input
    else{
        document.getElementById("score").closest("#score").value = "Invalid Value!"
    }

    tempRank = document.getElementById("rank").closest("#rank").value;

    if (tempRank.match(patterna) || tempRank.match(patternb)){
        rankCondition = tempRank
    }
    else if(tempRank == ""){} // do nothing if no input
    else{
        document.getElementById("rank").closest("#Rank").value = "Invalid Value!"
    }
    if(limit = ""){} //do nothing if no input
    else{
        limit = document.getElementById("limit").closest("#limit").value;
    }
    fetchLeaderboard(limit, scoreCondition, rankCondition);
}
logoutbutton.addEventListener('click', function () {
    Logout();
})

async function Logout() {
    await fetch("/logout");
    window.location.replace("/login");
}

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
        studentDefaultButtons.style.display = "none";
        greyed = true;
    }
}

var limit;
var scoreCondition;
var rankCondition;
var sort;


async function fetchLeaderboard(limitf = 25, scoreconditionf = ">0", rankconditionf = ">0", sortf = "points_desc", ) {

    let r = await fetch(`/api/students.json?limit=${limitf}&sort=${sortf}&scorecondition=${scoreconditionf}&rankcondition=${rankconditionf}`);
    let j = await r.json();

    for (const el of document.querySelectorAll(`.leaderboard .listing`)) {
        el.remove();
    }
    for(const el of document.querySelectorAll(`.leaderboard`)){
        let place = 1;
        for (const student of j) {
            renderStudent(el, place, student);
            student.place = place;
            place++;
        }
}   }

async function init() {
    fetchLeaderboard(limit, scoreCondition, rankCondition, sort);
}

init();


// Greeting
// TODO: Actually have correct time
// let greetingPossibilities = ["Good afternoon, %s", "Welcome, %s", "Greetings, %s"];
// let greeting = greetingPossibilities[Math.floor(Math.random() * greetingPossibilities.length)].replaceAll("%s", USER_NAME);
// $el("#greeting").innerText = greeting;

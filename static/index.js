// TODO: Account
// const USER_NAME = "Mr. Doe";
const logoutbutton = $el("#logout");                                // Refers to the logout button at the top next to the logo
const leaderboard = $el("#leaderboard");                             // The next three refer to the three leaderboards on three tabs on the 
const miniLeaderboard = $el("#mini-leaderboard");
const leaderboardStudents = $el("#mini-leaderboard-students");
const studentViewer = $el('.student-viewer');                       // Refers to the right side of the student tab
const studentEditorButtons = $el('#student-editor-buttons');        // Refers to the buttons that show up when you click on a student to edit it
const studentCreatorButtons = $el("#student-creator-buttons");      // Refers to the buttons that pop up when you click "Add Student"
const studentDefaultButtons = $el("#student-default-buttons");      // Refers to the buttons that are by default on the right side of the students tab for teachers
const batchAddModal = $el("#batch-add");                            // Refers to the modal that pops up when you want to add students from a list
const sortButton = $el("#dropdown");                                // Refers to the menu that pops up when you want to filter the leaderboard
const mailList = $el("#mail");
/* $el() is a function that searches for elements (see utils.js). The
top ten lines of code are just assigning elements to constant variables
so that do things with them later.    */

sortButton.addEventListener("click", function () {
    sortButton.querySelector(".dropdown-content").style.display = "block";          // Makes the webpage listen fro a click on the filter leaderboard button so the dropdown menu pops up
});


document.addEventListener("click", (function (event) {
    var $target = $(event.target);
    if (!$target.closest('#dropdown').length &&
        $('.dropdown-content').is(":visible")) {
        $('.dropdown-content').hide();
    }
}));                                                                              // Makes it so that the dropdown menu for filtering students disappears when you click outside of the menu


async function Logout() {
    await fetch("/logout");             // Sends for the server which deletes your session and thus logs you out.
    window.location.replace("/login");  // Takes you to the login page.
}

studentEditorButtons.style.display = "none";        // Hides the buttons in the student tab that are not there by default.
studentCreatorButtons.style.display = "none";       // They will appear when you click on a student to edit or click "Add Student" respectively
// The function for these is in "students.js"


function renderStudent(parent, student) {                                    // This is the function that takes the response from the server when you do fetchLeaderboard(), which is a student represented as json,
    const cont = $e("div", parent, { classes: ["listing"] });                // And then renders it as a listing in the leaderboard
    const left = $e("div", cont);                                            // Creates a div for the left side of the listing for the rank, name, and grade
    const right = $e("div", cont);                                          // Creates a div for the right side for the points
    const rank = $e("span", left, { innerText: student.rank, classes: ["place"] });     // Creates a box for the place
    if ([1, 2, 3].includes(student.rank)) {
        rank.classList.add(`rank${student.rank}`);                                      // If you are 1st, 2nd, or 3rd, it adds a special class to color you gold, silver, or bronze
    }
    $e("span", left, { innerText: student.name, classes: ["name"] });
    $e("span", left, { innerText: `(${student.grade}th)`, classes: ["grade"] });        // Creates elements for the grade, rank, and name of the student for the leaderboard
    $e("span", right, {
        innerText: student.points.toLocaleString(),
        classes: ["points"],
        title: "Points"
    });
    cont.addEventListener("click", function () {
        editStudent(student);                                                           // Creates an event listener so that when you click on a student their info shows in the editor
    });
}

let currentStudent;

function editStudent(studentData) {

    studentEditorButtons.style.display = "block";
    if (greyed === false) {
        currentStudent = studentData;
        studentViewer.querySelector("#student-name").value = studentData.name;      //
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


async function fetchLeaderboard(
    limitf = 25,
    scoreconditionf = ">-1",
    rankconditionf = ">-1",
    sortf = "points_desc"
) {
    let r = await fetch(`/api/students.json?limit=${limitf}&sort=${sortf}&scorecondition=${scoreconditionf}&rankcondition=${rankconditionf}`);
    let j = await r.json();

    console.log(j);

    for (const el of document.querySelectorAll(`.leaderboard .listing`)) {
        el.remove();
    }
    for (const el of document.querySelectorAll(`.leaderboard`)) {
        let place = 1;
        for (const student of j) {
            renderStudent(el, student);
            console.log("rendered");
            student.place = place;
            place++;
        }
    }
}

async function getInbox() {
    let r = await fetch("/api/get_inbox");
    let j = await r.json();
    console.log(j);
    console.log(j[1]);
    console.log(mailList);
    for (const el of document.querySelectorAll("#mail .listing")) {
        el.remove();
    }
    for (const request of j) {
        makeMail(mailList, request);
        console.log("hi");
    }
}

async function makeMail(parent, request) {
    listing = $e("div", parent, { classes: ["listing"] });
    right = $e("div", listing)
    let acceptButton = $e("button", listing, { innerText: "check", classes: ["mail-confirm", "material-icons"] })
    acceptButton.addEventListener("click", async function () {
        listing.remove();
        await confirmOrDenyAddStudent(request.id, "accept");
        getInbox();
    })
    let denybutton = $e("button", listing, { innerText: "close", classes: ["mail-deny", "material-icons"] })
    denybutton.addEventListener("click", async function () {
        listing.remove();
        await confirmOrDenyAddStudent(request.id, "deny");
        getInbox();
    })
    $e("span", right, { innerText: request.operation + " " });
    $e("span", right, { innerText: request.role });
    bottomText = $e("div", right, { classes: ['bottom-text'] })
    $e("span", bottomText, { innerText: "Name: " + request.name + "; " });
    $e("span", bottomText, { innerText: "Email: " + request.email + "; " });
    if (request.grade != "NULL") {
        $e("span", bottomText, { innerText: "Grade: " + request.grade + ";" });
    }
}

async function confirmOrDenyAddStudent(ID, approval) {
    if (approval == "deny") {
        await fetch("/api/deny", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                request_id: ID,
            })
        });
        console.log(JSON.stringify({
            request_id: ID,
        }))
    }
    else if (approval == "accept") {
        await fetch("/api/accept_student_add", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                request_id: ID,
            })
        });
        console.log(JSON.stringify({
            request_id: ID,
        }))
    }

}


async function init() {
    fetchLeaderboard(limit, scoreCondition, rankCondition, sort);
    getInbox();
}

init();


// Greeting
// TODO: Actually have correct time
// let greetingPossibilities = ["Good afternoon, %s", "Welcome, %s", "Greetings, %s"];
// let greeting = greetingPossibilities[Math.floor(Math.random() * greetingPossibilities.length)].replaceAll("%s", USER_NAME);
// $el("#greeting").innerText = greeting;
const batchCSVInput = batchAddModal.querySelector("#file");
const studentSearchInput = $el("#search-input");
const gradeCheckboxes = {
    9: $el("#search-grade-9th"),
    10: $el("#search-grade-10th"),
    11: $el("#search-grade-11th"),
    12: $el("#search-grade-12th"),
};

// Initalization in case reload kept old stuff
studentSearchInput.value = "";
for (const checkbox of Object.values(gradeCheckboxes)) {
    checkbox.checked = true;
}

var greyed = false;

studentDefaultButtons.querySelector("#add-student").addEventListener("click", function () {
    addStudent();
});

studentCreatorButtons.querySelector("#cancel").addEventListener("click", function () {
    cancelNewStudent();
});

studentCreatorButtons.querySelector("#save-student").addEventListener("click", function () {
    saveNewStudent();
});

batchAddModal.querySelector("#upload").addEventListener("click", batchAdd);

$el("#delete-student-button").addEventListener("click", async function () {
    const doIt = await modalConfirm("Are you sure you want to delete this student?", "Delete", "Cancel");

    if (doIt) {
        deleteStudent();
    }
});

async function saveNewStudent() {
    await fetch("/api/new_save_student.json", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            student_name: studentViewer.querySelector("#student-name").value,
            student_grade: studentViewer.querySelector("#student-grade").value,
            student_points: studentViewer.querySelector("#student-points").value,
            student_email: studentViewer.querySelector("#student-email").value
        })
    });
    createNotification("Success!", "New student saved successfully.");
    fetchLeaderboard(limit, scoreCondition, rankCondition, sort);
}
function addStudent() {
    if (greyed === false) {
        studentCreatorButtons.style.display = "block";
        studentDefaultButtons.style.display = "none";
        greyed = true;
    }
}


async function saveStudent() {
    await fetch("/api/save_student.json", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            student_id: currentStudent.id,
            student_name: studentViewer.querySelector("#student-name").value,
            student_grade: studentViewer.querySelector("#student-grade").value,
            student_points: studentViewer.querySelector("#student-points").value,
            student_email: studentViewer.querySelector("#student-email").value
        })
    });
    createNotification("Success!", "Student saved successfully.");
    fetchLeaderboard(limit, scoreCondition, rankCondition, sort);
}

function resetStudent() {
    studentData = currentStudent;
    studentViewer.querySelector("#student-name").value = studentData.name;
    studentViewer.querySelector("#student-points").value = studentData.points;
    studentViewer.querySelector("#student-grade").value = studentData.grade;
    studentViewer.querySelector("#student-email").value = studentData.email;
}

function cancelStudent() {
    studentViewer.querySelector("#student-name").value = "";
    studentViewer.querySelector("#student-points").value = "";
    studentViewer.querySelector("#student-grade").value = "";
    studentViewer.querySelector("#student-email").value = "";
    studentEditorButtons.style.display = "none";
    studentDefaultButtons.style.display = "block";

    greyed = false;
}

function cancelNewStudent() {
    studentCreatorButtons.style.display = "none";
    studentViewer.querySelector("#student-name").value = "";
    studentViewer.querySelector("#student-points").value = "";
    studentViewer.querySelector("#student-grade").value = "";
    studentViewer.querySelector("#student-email").value = "";
    studentDefaultButtons.style.display = "block";
    greyed = false;
}

async function promptDeleteStudent() {
    const doIt = await modalConfirm("Are you sure you want to delete this student?", "Delete", "Cancel");
}

async function deleteStudent() {
    await fetch("/api/delete_student.json", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            student_id: currentStudent.id
        })
    });
    createNotification("Success!", "Student deleted successfully.");
    closeModals();
    cancelStudent();
    fetchLeaderboard(limit, scoreCondition, rankCondition, sort);
}

async function batchAdd() {
    // Thanks to https://stackoverflow.com/a/40826943 :^)
    const formData = new FormData();
    formData.append("file", batchCSVInput.files[0]);

    await fetch("/api/batch_add", {
        method: "POST",
        body: formData,
    });

    createNotification("Success!", "Students added successfully.");

    fetchLeaderboard(limit, scoreCondition, rankCondition, sort);
    console.log("refreshed leaderboard!");
    closeModals();
}

function getFilters() {
    let rankCondition = ">0";
    if ($el("#min-rank-toggle").checked) {
        const rankThreshold = parseInt($el("#min-rank").value);
        rankCondition = `<${rankThreshold + 1}`;
    }

    let scoreCondition = ">-1";
    if ($el("#min-score-toggle").checked) {
        const scoreThreshold = $el("#min-score").value;
        scoreCondition = `>${scoreThreshold - 1}`;
    }

    return { rank: rankCondition, score: scoreCondition }
}

async function updateStudentSearch() {
    // TODO: Fix placement to use values from server instead of just nth result
    let queryBits = [`q=${studentSearchInput.value}`, "limit=25", "sort=points_desc"];

    const filters = getFilters();

    if (filters.score) {
        queryBits.push(`scorecondition=${filters.score}`)
    }

    if (filters.rank) {
        queryBits.push(`rankcondition=${filters.rank}`)
    }

    // let r = await fetch(`/api/students.json?limit=${limitf}&sort=${sortf}&scorecondition=${scoreconditionf}&rankcondition=${rankconditionf}`);

    for (const [grade, checkbox] of Object.entries(gradeCheckboxes)) {
        console.log(grade, checkbox);
        queryBits.push(`show_${grade}th=${checkbox.checked}`);
    }

    let r = await fetch("/api/students.json?" + queryBits.join("&"));
    let j = await r.json();
    console.log(r.url);

    for (const el of document.querySelectorAll("#mini-leaderboard-students .listing")) {
        el.remove();
    }

    // Stuff from index.js
    let place = 1;
    for (const student of j) {
        renderStudent(leaderboardStudents, student);
        student.place = place;
        place++;
    }
}

// Update search when user types
studentSearchInput.addEventListener("input", updateStudentSearch);

for (const checkbox of Object.values(gradeCheckboxes)) {
    // Make it clickable all over it
    checkbox.parentNode.addEventListener("click", function (event) {
        // If the node is the label or the checkbox itself, clicking it
        // like this will cancel out the actual click (which normally works).
        // Only handle this if we're clicking the div.
        if (event.target !== this) return;
        checkbox.click();
    });

    // Update search when its changed
    checkbox.addEventListener("change", updateStudentSearch);
}

// Search criteria settings updater
for (const rowEl of document.querySelectorAll(".row-setting")) {
    const topEl = rowEl.querySelector(".row-top");
    const bottomEl = rowEl.querySelector(".row-bottom");
    const checkboxEl = topEl.querySelector('input[type="checkbox"]');
    const inputEl = rowEl.querySelector("input.main-setting-input");
    const valueEl = rowEl.querySelector(".row-setting-value");

    rowEl.addEventListener("click", function (event) {
        if (event.target !== this) return;
        checkboxEl.click();
    });

    inputEl.addEventListener("input", function () {
        valueEl.innerText = this.value;
    });

    inputEl.addEventListener("change", function() {
        updateStudentSearch();
    });

    checkboxEl.addEventListener("input", function () {
        bottomEl.classList.toggle("hidden", !checkboxEl.checked);
        updateStudentSearch();
    });

    valueEl.innerText = inputEl.value;
    bottomEl.classList.toggle("hidden", !checkboxEl.checked);
}
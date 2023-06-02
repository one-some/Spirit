const batchCSVInput = batchAddModal.querySelector("#file");

var greyed = false;

studentDefaultButtons.querySelector("#add-student").addEventListener("click", function () {
    addStudent();
})

studentCreatorButtons.querySelector("#cancel").addEventListener("click", function () {
    cancelNewStudent();
})

studentCreatorButtons.querySelector("#save-student").addEventListener("click", function () {
    saveNewStudent();
})

deleteStudentModal.querySelector("#delete").addEventListener("click", function () {
    deleteStudent();
})

batchAddModal.querySelector("#upload").addEventListener("click", batchAdd);

async function saveNewStudent () {
    await fetch("/api/new_save_student.json", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            student_name: studentViewer.querySelector("#student-name").value, 
            student_grade: studentViewer.querySelector("#student-grade").value,
            student_points: studentViewer.querySelector("#student-points").value
        })
    })
    fetchLeaderboard()
}
function addStudent(){
    if(greyed === false){
        studentCreatorButtons.style.display = "block";
        studentDefaultButtons.style.display = "none"
        greyed = true;
    }
}


async function saveStudent(){
    await fetch("/api/save_student.json", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            student_id: currentStudent.id,
            student_name: studentViewer.querySelector("#student-name").value, 
            student_grade: studentViewer.querySelector("#student-grade").value,
            student_points: studentViewer.querySelector("#student-points").value
        })
    })
    fetchLeaderboard();
}

function resetStudent(){
    studentData = currentStudent;
    studentViewer.querySelector("#student-name").value = studentData.name;
    studentViewer.querySelector("#student-points").value = studentData.points;
    studentViewer.querySelector("#student-grade").value = studentData.grade;
}

function cancelStudent() {
    studentViewer.querySelector("#student-name").value = "";
    studentViewer.querySelector("#student-points").value = "";
    studentViewer.querySelector("#student-grade").value = "";
    studentEditorButtons.style.display = "none";
    studentDefaultButtons.style.display = "block";

    greyed = false;
}

function cancelNewStudent() {
    studentCreatorButtons.style.display = "none";
    studentViewer.querySelector("#student-name").value = "";
    studentViewer.querySelector("#student-points").value = "";
    studentViewer.querySelector("#student-grade").value = "";
    studentDefaultButtons.style.display = "block";
    greyed = false;
}

async function deleteStudent(){
    await fetch("/api/delete_student.json", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            student_id: currentStudent.id
        })
    })
    closeModals();
    cancelStudent();
    fetchLeaderboard();
}

async function batchAdd() {
    // Thanks to https://stackoverflow.com/a/40826943 :^)
    const formData = new FormData();
    formData.append("file", batchCSVInput.files[0]);

    await fetch ("/api/batch_add", {
        method: "POST",
        body: formData,
    });

    fetchLeaderboard();
    console.log("refreshed leaderboard!")
    closeModals();
}
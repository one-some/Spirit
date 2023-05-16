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
}
function addStudent(){
    if(greyed === false){
        studentCreatorButtons.style.display = "block";
        studentDefaultButtons.querySelector("#add-student").style.backgroundColor = "grey";
        studentDefaultButtons.querySelector("#delete").style.backgroundColor = "grey";
        studentDefaultButtons.querySelector("#batch-add").style.backgroundColor = "grey";
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
    studentDefaultButtons.querySelector("#add-student").style.backgroundColor = "";
    studentDefaultButtons.querySelector("#delete").style.backgroundColor = "";
    studentDefaultButtons.querySelector("#batch-add").style.backgroundColor = "";

    greyed = false;
}

function cancelNewStudent() {
    studentCreatorButtons.style.display = "none";
    studentViewer.querySelector("#student-name").value = "";
    studentViewer.querySelector("#student-points").value = "";
    studentViewer.querySelector("#student-grade").value = "";
    studentDefaultButtons.querySelector("#add-student").style.backgroundColor = "";
    studentDefaultButtons.querySelector("#delete").style.backgroundColor = "";
    studentDefaultButtons.querySelector("#batch-add").style.backgroundColor = "";

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
    console.log(leaderboardStudents.children[currentStudent.place]);
    leaderboardStudents.children[currentStudent.place - 1].remove();
}
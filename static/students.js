studentDefaultButtons.querySelector("#add-student").addEventListener("click", function () {
    addStudent();
})

studentCreatorButtons.querySelector("#cancel").addEventListener("click", function () {
    cancelNewStudent();
})

studentCreatorButtons.querySelector("#save-student").addEventListener("click", function () {
    saveNewStudent();
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
    studentCreatorButtons.style.display = "block";
    studentDefaultButtons.querySelector("#add-student").style.backgroundColor = "grey";
    studentDefaultButtons.querySelector("#cancel").style.backgroundColor = "grey";
    studentDefaultButtons.querySelector("#batch-add").style.backgroundColor = "grey";
    studentViewer.querySelector("#student-name").value = "";
    studentViewer.querySelector("#student-points").value = "";
    studentViewer.querySelector("#student-grade").value = "";
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
    studentDefaultButtons.querySelector("#cancel").style.backgroundColor = "";
    studentDefaultButtons.querySelector("#batch-add").style.backgroundColor = "";
}

function cancelNewStudent() {
    studentViewer.querySelector("#student-name").value = "";
    studentViewer.querySelector("#student-points").value = "";
    studentViewer.querySelector("#student-grade").value = "";
    studentCreatorButtons.style.display = "none";
    studentDefaultButtons.querySelector("#add-student").style.backgroundColor = "";
    studentDefaultButtons.querySelector("#cancel").style.backgroundColor = "";
    studentDefaultButtons.querySelector("#batch-add").style.backgroundColor = "";
}
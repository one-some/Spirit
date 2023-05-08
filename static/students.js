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
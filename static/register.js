function showStudentRegister() {
    $el("#register-student").style.display = "block";
    $el("#choose-role").style.display = "none";
}

function showAdminRegister() {
    $el("#register-admin").style.display = "block";
    $el("#choose-role").style.display = "none";
}



function appear() {

    const schoolName = $el("#school-name")
    const schoolNameLabel = $el("#school-name-label")
    console.log(schoolName.style.display);

    if(schoolName.style.display == 'block'){
        schoolName.style.display = 'none';
        schoolNameLabel.style.display = 'none';
    }
    else{
        schoolName.style.display = 'block';
        schoolNameLabel.style.display = 'block';
    }
    

    console.log(schoolName.style.display)

}
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
    console.log(schoolName.style.dislpay);

    if(schoolName.style.dislpay == 'none'){
        schoolName.style.display = 'block';
    }
    else{
        schoolName.style.dislpay = 'none';
    }
    

    console.log(schoolName.style.dislpay)

}
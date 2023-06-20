function showStudentRegister() {
    $el("#register-student").style.display = "block";
    $el("#choose-role").style.display = "none";
}

function showAdminRegister() {
    $el("#register-admin").style.display = "block";
    $el("#choose-role").style.display = "none";
}



function appear() {

    console.log($el("#school-name").style.dislpay);

    $el("#school-name").style.dislpay = 'none';

    console.log($el("#school-name").style.dislpay)

}
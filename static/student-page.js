
const points = Number($el("#points").innerText);
var goal = function (){ 
    var foo;
    for(var x = 0; x < points; x+= 5000){
        foo = x;
        console.log("foo: ", foo);
    }
    return foo + 5000;
}();
console.log("points: ", points);
console.log("goal: ",  goal);
var elem = document.getElementById("myBar");
var width = 1;


elem.style.width = Math.round( 1000 * (points / goal + Number.EPSILON)) / 10 + "%"; // multiplies by 1000 to be accurate to 3 decimal places, but then divides by 10 (instead of / 1000 * 100) to turn into a percent.
elem.style.borderRadius = '500px';


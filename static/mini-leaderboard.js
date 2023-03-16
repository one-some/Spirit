const miniLeaderboard = $el("#mini-leaderboard");

function makeEntry(place, name, grade, points) {
    console.log(name, grade, points);
    const cont = $e("div", miniLeaderboard, { classes: ["listing"] });
    $e("span", cont, { innerText: place, classes: ["place"] });
    $e("span", cont, { innerText: name, classes: ["name"] });
    $e("span", cont, { innerText: grade, classes: ["grade"] });
    $e("span", cont, { innerText: points, classes: ["points"] });
}

for (const entry of [
    [1, "Sam", 11, 8251],
    [2, "Shelly", 12, 7251],
    [3, "Bob", 9, 4343],
    [4, "Jane", 10, 2343],
]) {
    makeEntry(...entry);
}

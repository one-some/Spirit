const suggestionContainer = $el("#search-suggestions");
const searchInput = $el("#search-input");

searchInput.focus();

searchInput.addEventListener("input", async function(event) {
    let encoded = encodeURIComponent(this.value);
    let r = await fetch(`/api/suggest.json?q=${encoded}`);
    let j = await r.json();

    // Clear
    suggestionContainer.innerHTML = "";

    for (const suggestion of j) {
        console.log(suggestion);
        renderSuggestion(suggestion.name, suggestion.points, suggestion.grade);
    }
});

function renderSuggestion(name, points, grade) {
    const suggestion = $e("div", suggestionContainer, {classes: ["suggestion"]});
    $e("span", suggestion, {classes: ["name"], innerText: name});
    const bottom = $e("div", suggestion, {classes: ["bottom"]});
    $e("span", bottom, {classes: ["grade"], innerText: `Grade: ${grade}`});
    $e("span", bottom, {classes: ["points"], innerText: `Points: ${points}`});
}

function deselectTabs() {
    for (const content of document.querySelectorAll("[tab-id]")) {
        content.classList.remove("selected");
    }

    for (const tabButton of document.querySelectorAll("[sidebar-button]")) {
        tabButton.classList.remove("selected");
    }
}

for (const tabButton of document.querySelectorAll("[sidebar-button]")) {
    let tabID = tabButton.getAttribute("sidebar-button");
    tabButton.addEventListener("click", function () {
        deselectTabs();

        let title = tabButton.getAttribute("title");
        if (title) document.title = `${title} - Spirit`;

        let tabURL = { home: "/", events: "/events", leaderboard: "/leaderboard" }[tabID];
        if (tabURL) window.history.pushState({}, null, tabURL);

        tabButton.classList.add("selected");
        const tabContent = $el(`[tab-id="${tabID}"]`);
        tabContent.classList.add("selected");
    });
}

// Click first tab

let targetTab = {
    "/": "home",
    "/events": "events",
    "/leaderboard": "leaderboard",
}[window.location.pathname] || "home";


window.addEventListener("load", function () {
    $el(`[sidebar-button="${targetTab}"]`).click();
});

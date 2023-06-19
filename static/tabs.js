function deselectTabs() {
    for (const content of document.querySelectorAll("[tab-id]")) {
        content.classList.remove("selected");
    }

    for (const tabButton of document.querySelectorAll("[sidebar-button]")) {
        tabButton.classList.remove("selected");
    }
}

function selectTab(tabID) {
    const tabButton = $el(`[sidebar-button="${tabID}"]`);
    deselectTabs();

    let title = tabButton.getAttribute("title");
    if (title) document.title = `${title} - Spirit`;

    let tabURL = { home: "/", students: "/students", leaderboard: "/leaderboard", documentation: "/documentation", "audit-log": "/audit-log", inbox: "/inbox" }[tabID];
    if (tabURL) window.history.pushState({}, null, tabURL);

    tabButton.classList.add("selected");
    const tabContent = $el(`[tab-id="${tabID}"]`);
    tabContent.classList.add("selected");

}

for (const tabButton of document.querySelectorAll("[sidebar-button]")) {
    let tabID = tabButton.getAttribute("sidebar-button");
    tabButton.addEventListener("click", function () {
        selectTab(tabID);
    });
}

// Click first tab

let targetTab = {
    "/": "home",
    "/events": "events",
    "/students": "students",
    "/leaderboard": "leaderboard",
    "/documentation": "documentation",
    "/audit-log": "audit-log",
    "/inbox": "inbox"
}[window.location.pathname] || "home";


window.addEventListener("load", function () {
    $el(`[sidebar-button="${targetTab}"]`).click();
});

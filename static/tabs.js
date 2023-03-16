function deselectTabs() {
    for (const content of document.querySelectorAll("[tab-id]")) {
        content.classList.remove("selected");
    }

    for (const tabButton of document.querySelectorAll("[sidebar-button]")) {
        tabButton.classList.remove("selected");
    }
}

for (const tabButton of document.querySelectorAll("[sidebar-button]")) {
    let tabName = tabButton.getAttribute("sidebar-button");
    tabButton.addEventListener("click", function() {
        deselectTabs();
        tabButton.classList.add("selected");
        const tabContent = $el(`[tab-id="${tabName}"]`);
        tabContent.classList.add("selected");
    });
}

// Click first tab

window.addEventListener("load", function() {
    $el("[sidebar-button]").click();
});

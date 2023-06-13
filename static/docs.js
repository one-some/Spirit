const docTab = $el('[tab-id="documentation"]');

function clearHighlight() {
    for (const highlight of document.querySelectorAll(".highlight")) {
        highlight.classList.remove("highlight");
    }
}

function revealElement(element) {
    // Select correct tab
    const elementTabID = element.closest("[tab-id]").getAttribute("tab-id");
    selectTab(elementTabID);

    // Just in case
    clearHighlight();
    element.classList.add("highlight");

    // Same as anim time
    setTimeout(clearHighlight, 1500);
}

function hookElementDescendantsForElementReferences(tree) {
    for (const anchor of tree.querySelectorAll("a")) {
        const targetSelector = anchor.getAttribute("element");
        if (!targetSelector) continue;

        anchor.classList.add("element-link");

        const targetEl = $el(targetSelector);
        if (!targetEl) {
            alert(`Bad selector ${targetSelector}`);
            continue;
        }

        anchor.href = "#";
        anchor.addEventListener("click", function (event) {
            revealElement(targetEl);
            event.preventDefault();
        });
    }
}

hookElementDescendantsForElementReferences(docTab);
const modalContainer = $el("#modal-container");
let currentModalEl;

modalContainer.classList.add("hidden");

for (const content of document.querySelectorAll("modal-content")) {
    const modal = $e("modal", modalContainer, { classes: ["hidden"] });
    const titlebar = $e("div", modal, { classes: ["titlebar"] });
    const title = $e("span", titlebar, { innerText: content.getAttribute("modal-title") })

    modal.addEventListener("click", function(event) {
        // Do not hide window when clicking in it.
        event.stopPropagation();
    })

    // Moves it
    modal.appendChild(content);
}

modalContainer.addEventListener("click", function () {
    if (!currentModalEl) return;

    modalContainer.classList.add("hidden");
    currentModalEl.classList.add("hidden");
});

function getModalContent(modalID) {
    // Just a convenience function
    return $el(`[modal-id="${modalID}"]`);
}

function showModal(modalID) {
    currentModalEl = $el(`[modal-id="${modalID}"]`).closest("modal");
    currentModalEl.classList.remove("hidden");
    modalContainer.classList.remove("hidden");
}
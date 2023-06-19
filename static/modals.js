const modalContainer = $el("#modal-container");
let currentModalEl;

modalContainer.classList.add("hidden");

for (const content of document.querySelectorAll("modal-content")) {
    const modal = $e("modal", modalContainer, { classes: ["hidden"] });
    const titlebar = $e("div", modal, { classes: ["titlebar"] });
    const title = $e("span", titlebar, { innerText: content.getAttribute("modal-title") });

    modal.addEventListener("click", function (event) {
        // Do not hide window when clicking in it.
        event.stopPropagation();
    });

    // Moves it
    modal.appendChild(content);
}

function closeModals() {
    if (!currentModalEl) return;

    modalContainer.classList.add("hidden");
    currentModalEl.classList.add("hidden");
}

modalContainer.addEventListener("click", closeModals);
document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") closeModals();
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

// Confirmation
const confirmPrompt = $el("#confirm-prompt");
const confirmYesButton = $el("#confirm-delete #delete");
const confirmNoButton = $el("#confirm-delete #cancel");

function modalConfirm(prompt, yesText = "Yes", noText = "No") {
    confirmPrompt.innerText = prompt;
    confirmYesButton.innerText = yesText;
    confirmNoButton.innerText = noText;

    return new Promise(function (resolve, reject) {
        showModal("confirm");

        confirmYesButton.onclick = function () {
            closeModals();
            resolve(true);
        };

        confirmNoButton.onclick = function () {
            closeModals();
            resolve(false);
        };
    });
}
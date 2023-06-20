const notificationContainer = $el("#notification-container");

function createNotification(title, body) {
    const notEl = $e("div", notificationContainer, { classes: ["notification"] });
    const titleEl = $e("span", notEl, { innerText: title, classes: ["n-title"] });
    const bodyEl = $e("span", notEl, { innerText: body, classes: ["n-body"] });

    setTimeout(function () {
        notEl.remove();
    }, 5000);
}
const LOG_SELECTED_CLASS = "log-selected";

const auditLogEl = $el("#audit-log");
const auditDetailTextEl = $el("#audit-detail-text");
let initDetailShown = false;

async function tryRevertAuditEvent(eventId) {
    const doIt = await modalConfirm("Really revert the database to this point in time? This action is not reversable.", "Revert", "Cancel");
    if (!doIt) return;
    console.log("TODO: REVERT TO", eventId);
}

function showAuditEventDetails(entry) {
    if (!entry.details) return;

    const date = new Date(entry.time * 1000);
    let actionDeets = [];

    for (const [key, value] of Object.entries(entry.details)) {
        actionDeets.push(`- ${key}: ${value}`);
    };

    actionDeets = actionDeets.join("\n");

    auditDetailTextEl.innerText = `Time: ${date.toLocaleString()}
    User Responsible: ${entry.user}
    Action Type: ${entry.action}
    Can Revert: ${entry.has_checkpoint ? "Yes" : "No"}`;

    if (actionDeets) auditDetailTextEl.innerText += `\nAction Details: \n${actionDeets}`;

}

function highlightEntry(el) {
    for (const highlighted of document.getElementsByClassName(LOG_SELECTED_CLASS)) {
        highlighted.classList.remove(LOG_SELECTED_CLASS);
    }

    el.classList.add(LOG_SELECTED_CLASS);
}

function renderAuditLogEntry(entry) {
    const entryEl = $e("div", auditLogEl, { classes: ["audit-log-entry"] });
    const date = new Date(entry.time * 1000);
    const timeEl = $e("span", entryEl, { innerText: date.toLocaleString(), classes: ["al-time"] });
    const userEl = $e("span", entryEl, { innerText: entry.user, classes: ["al-user"] });
    const actionEl = $e("span", entryEl, { innerText: entry.action, classes: ["al-action"] });

    if (entry.has_checkpoint) {
        $e("spacer", entryEl);
        const revertEl = $e(
            "span",
            entryEl,
            {
                innerText: "update",
                title: "Revert to this point",
                classes: ["al-revert", "material-icons"]
            }
        );

        revertEl.addEventListener("click", async function (event) {
            event.stopPropagation();
            await tryRevertAuditEvent(entry.event_id);
        });
    }

    entryEl.addEventListener("click", function () {
        highlightEntry(entryEl);
        showAuditEventDetails(entry);
    });

    if (!initDetailShown) {
        initDetailShown = true;
        highlightEntry(entryEl);
        showAuditEventDetails(entry);
    }
}

async function loadAuditLog() {
    const r = await fetch("/api/audit_log.json");
    const j = await r.json();

    for (const entry of j) {
        renderAuditLogEntry(entry);
    }
}

loadAuditLog();
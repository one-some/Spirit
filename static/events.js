const ea_nameEl = $el("#event-name");
const ea_descEl = $el("#event-desc");
const ea_locationEl = $el("#event-location");
const ea_timeEl = $el("#event-daterange");
const ea_pointsEl  = $el("#event-points");

for (const input of [ea_nameEl, ea_descEl, ea_locationEl, ea_timeEl, ea_pointsEl]) {
    input.addEventListener("input", function() {
        this.classList.remove("bad-input");
    });
}

function getNewEventData() {

    // Mark all fields visually valid initially
    for (const invalidEl of document.querySelectorAll(".bad-input")) {
        invalidEl.classList.remove("bad-input");
        invalidEl.setAttribute("title", invalidEl.getAttribute("og-title"));
    }

    let dat = {
        name: ea_nameEl.value || null,
        desc: ea_descEl.value || null,
        location: ea_locationEl.value || null,
        time: ea_timeEl.value || null,
        points: parseInt(ea_pointsEl.value),
    };

    let invalidEls = [];


    if (!dat.name) invalidEls.push(ea_nameEl);
    if (!dat.desc) invalidEls.push(ea_descEl);
    if (!dat.location) invalidEls.push(ea_locationEl);
    if (!dat.time) invalidEls.push(ea_timeEl);
    if (isNaN(dat.points) || dat.points < 0) invalidEls.push(ea_pointsEl);

    for (const el of invalidEls) {
        el.classList.add("bad-input");
        el.setAttribute("old-title", ea_nameEl.getAttribute("title"));
        el.setAttribute("title", "This field is required.");
    }

    if (invalidEls.length) return undefined;
    return dat;
}

$el("#create-event-button").addEventListener("click", async function () {
    console.log("HI")
    let dat = getNewEventData();

    await fetch("/api/create_event.json", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(dat)
    });

    if (dat) closeModals();
});

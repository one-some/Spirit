const miniEvents = $el("#mini-events");
const addEventButton = $el("#add-event-in-listing");

const eventViewer = $el('[modal-id="event-viewer"]');

const ea_nameEl = $el("#event-name");
const ea_descEl = $el("#event-desc");
const ea_locationEl = $el("#event-location");
const ea_timeEl = $el("#event-daterange");
const ea_pointsEl = $el("#event-points");

let currentDateRange = {};

for (const input of [ea_nameEl, ea_descEl, ea_locationEl, ea_timeEl, ea_pointsEl]) {
    input.addEventListener("input", function () {
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
        time_start: currentDateRange.start,
        time_end: currentDateRange.end,
        //time: ea_timeEl.value || null,
        points: parseInt(ea_pointsEl.value),
    };

    let invalidEls = [];


    if (!dat.name) invalidEls.push(ea_nameEl);
    if (!dat.desc) invalidEls.push(ea_descEl);
    if (!dat.location) invalidEls.push(ea_locationEl);
    if (!(dat.time_start || dat.time_end)) invalidEls.push(ea_timeEl);
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

    // Data is invalid. We've let the user know so just do nothing
    if (!dat) return;

    await fetch("/api/create_event.json", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(dat)
    });

    closeModals();
});

// Date picker
$(function () {
    $('input[name="datetimes"]').daterangepicker({
        opens: "right",
        timePicker: true,
        startDate: moment().startOf('hour'),
        endDate: moment().startOf('hour').add(32, 'hour'),
        autoApply: true,
        locale: { format: 'M/DD hh:mm A' }
    }, function (start, end, label) {
        currentDateRange.start = Math.floor(start.unix() / 1000);
        currentDateRange.end = Math.floor(end.unix() / 1000);
        console.log("BOOM");
    });
});

addEventButton.addEventListener("click", function () {
    showModal("event-creator");
});


function makeEvent(event) {
    const cont = $e("div", miniEvents, { classes: ["listing"], }, { before: addEventButton });
    $e("span", cont, { innerText: event.name, classes: ["name"] });
    $e("span", cont, { innerText: event.desc, classes: ["desc"] });
    $e("span", cont, { innerText: event.location, classes: ["location"] });
    cont.addEventListener("click", function() {
        editEvent(event);
    })
}

function editEvent(eventData) {
    eventViewer.querySelector("#event-name").value = eventData.name;
    eventViewer.querySelector("#event-desc").value = eventData.desc;
    eventViewer.querySelector("#event-location").value = eventData.location;
    eventViewer.querySelector("#event-location").value = eventData.location;
    eventViewer.querySelector("#event-points").value = eventData.points;
    showModal("event-viewer");
}


async function initEvents() {
    let r = await fetch("/api/events.json");
    let j = await r.json();

    for (const event of j) {
        makeEvent(event);
    }
    editEvent(j[j.length - 1]);
}

initEvents();
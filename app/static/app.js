function getElement(selector){
    return document.querySelector(selector);
}
// osetri dynamicky text pred vlozenim cez innerHTML aby sa nevykonal ako HTML kod
function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}
// zobrazi vysleodk alebo chybu v konkretnom HTML elemente
function showResult(element, type, html) {
    element.hidden = false;
    element.className = `result-panel ${type}`;
    element.innerHTML = html;
}
// nacita JWT token ulozeny v prehliadaci, ak existuje token tak user je prihlaseny
function getToken() {
    return localStorage.getItem("access_token");
}

function clearAuth() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
}
// nastavi elementy na neviditelne
function setElementVisible(element, visible) {
    if (!element) return;
    element.hidden = !visible;
    if(visible){
        element.hidden=false;
        element.style.display="";

    }else{
        element.hidden=true;
        element.style.display="none";
    }
}

// metoda, ktora urcuje ci sa zobrazi login/register, alebo len odhlasenie
function showEmptyState(container, message) {
    container.innerHTML = "";
    const paragraph = document.createElement("p");
    paragraph.className = "empty-state";
    paragraph.textContent = message;
    container.append(paragraph);
}
function updateAuthNavigation() {
    const guestActions = document.querySelector("[data-guest-actions]");
    const userActions = document.querySelector("[data-user-actions]");
    const currentUser = document.querySelector("[data-current-user]");
    const isLoggedIn = Boolean(getToken());

    if (!guestActions || !userActions) return;

    setElementVisible(guestActions, !isLoggedIn);
    setElementVisible(userActions, isLoggedIn);

    if (currentUser && isLoggedIn) {
        currentUser.textContent = localStorage.getItem("username") || "Logged-in user";
    }
}

function handleUnauthorizedResponse(response) {
    if (response.status !== 401) return;
    clearAuth();
    updateAuthNavigation();
}

// zisti aktualne prihlaseneho usera.
function authHeaders(extraHeaders = {}) {
    const headers = {...extraHeaders};
    const token = getToken();
    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }
    return headers;
}

async function readError(response) {
    try {
        const payload = await response.json();
        return payload.detail || "The operation could not be completed.";
    } catch {
        return "The operation could not be completed.";
    }
}
// nacita udaje o aktualne prihlaseneho pouzivatela
async function loadEvents() {
    const list = getElement("#eventsList");

    if (!getToken()) {
        showEmptyState(list, "Log in to view your study events.");
        return;
    }
    showEmptyState(list, "Loading your events...");

    try {
        const response = await fetch("/events/", {
            headers: authHeaders(),
        });
        if (!response.ok) {
            handleUnauthorizedResponse(response);
            throw new Error(await readError(response));
        }

        const events = await response.json();
        if (events.length === 0) {
            showEmptyState(list, "No events yet. Create your first study block.");
            return;
        }
        list.innerHTML="";
        events.forEach((event)=>{
            const article= document.createElement("article");
            article.className="event-item";
            const content= document.createElement("div");
            const date= document.createElement("span");
            date.className= "event-date";
            date.textContent= event.date;
            const title= document.createElement("strong");
            title.textContent= event.title;
            const time= document.createElement("small");
            time.textContent= `${event.start} - ${event.end}`;
            const button= document.createElement("button");
            button.className="icon-button";
            button.type="button";
            button.dataset.deleteEvent= event.id;
            button.textContent= "Delete";
            content.append(date,title,time);
            article.append(content,button);
            list.append(article);
        });
    } catch (error) {
        showEmptyState(list, error.message);
    }
}
async function handleStudyPlan(event){
    event.preventDefault();
    const form= event.currentTarget;
    const output= getElement("#studyPlanResult");
    if(!getToken()){
        showResult(output,"error","Log in before creating a study plan.");
        return;
    }
    const payload= {
        subject: form.subject.value,
        title: form.title.value,
        task_type: form.task_type.value,
        difficulty: Number(form.difficulty.value),
        pages_count: Number(form.pages_count.value),
        start_date: form.start_date.value,
        test_date: form.test_date.value,
        preferred_start_time: `${form.preferred_start_time.value}:00`,
        max_minutes_per_day: Number(form.max_minutes_per_day.value)
    };
    try {
        const response = await fetch("/events/study_plan", {
            method: "POST",
            headers: authHeaders({"Content-Type": "application/json"}),
            body: JSON.stringify(payload),
        });
        if (!response.ok) {
            handleUnauthorizedResponse(response);
            throw new Error(await readError(response));
        }

        const result = await response.json();
        const blockItems = result.blocks.map((block) => `
            <li>
                ${escapeHtml(block.date)}:
                ${escapeHtml(block.start_time)} - ${escapeHtml(block.end_time)}
                (${escapeHtml(block.minutes)} min)
            </li>
        `).join("");

        showResult(output, "success", `
            Study plan created.<br>
            Blocks created: <strong>${result.block_count}</strong><br>
            Total estimated time: <strong>${result.total_minutes} minutes</strong>
            <ul>${blockItems}</ul>
        `);

        form.reset();
        setDefaultDates();
        await loadEvents();
    } catch (error) {
        showResult(output, "error", escapeHtml(error.message));
    }
}
// Event listeners -study form
getElement("#studyPlanForm")?.addEventListener("submit", handleStudyPlan);

// predict form
getElement("#predictForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const output = getElement("#predictResult");

    const payload = {
        subject: form.subject.value,
        task_type: form.task_type.value,
        difficulty: Number(form.difficulty.value),
        pages_count: Number(form.pages_count.value),
        days_until_test: Number(form.days_until_test.value),
    };

    try {
        const response = await fetch("/events/predict", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            handleUnauthorizedResponse(response);
            throw new Error(await readError(response));
        }

        const result = await response.json();
        showResult(output, "success", `
            <strong class="result-number">${escapeHtml(result.formatted)}</strong>
            Total estimate: ${result.predicted_minutes} minutes.
            With regular study, that is about <strong>${result.daily_minutes} minutes per day</strong>.
        `);
    } catch (error) {
        showResult(output, "error", escapeHtml(error.message));
    }
});

getElement("#manualForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const output = getElement("#manualResult");

    if (!getToken()) {
        showResult(output, "error", "Log in before saving an event.");
        return;
    }

    const payload = {
        title: form.title.value,
        date: form.date.value,
        start: `${form.start.value}:00`,
        end: `${form.end.value}:00`,
        sync_to_google: form.sync_to_google.checked,
    };

    try {
        const response = await fetch("/events/", {
            method: "POST",
            headers: authHeaders({"Content-Type": "application/json"}),
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            handleUnauthorizedResponse(response);
            throw new Error(await readError(response));
        }

        const result = await response.json();
        showResult(output, "success", `<strong>${escapeHtml(result.title)}</strong><br>${escapeHtml(result.message)}`);
        form.reset();
        setDefaultDates();
        await loadEvents();
    } catch (error) {
        showResult(output, "error", escapeHtml(error.message));
    }
});

getElement("#eventsList").addEventListener("click", async (event) => {
    const button = event.target.closest("[data-delete-event]");
    if (!button) return;

    try {
        const response = await fetch(`/events/${button.dataset.deleteEvent}`, {
            method: "DELETE",
            headers: authHeaders(),
        });
        if (!response.ok) {
            handleUnauthorizedResponse(response);
            throw new Error(await readError(response));
        }
        await loadEvents();
    } catch (error) {
        window.alert(error.message);
    }
});

getElement("#reloadEvents").addEventListener("click", () => {
    void loadEvents();
});

getElement("#logoutButton")?.addEventListener("click", () => {
    clearAuth();
    updateAuthNavigation();
    void loadEvents();
});
// helper funkcia, ktora nastavi aktualny datum ako default pre prazdny datum
function setDefaultDates() {
    const today = new Date().toISOString().split("T")[0];
    document.querySelectorAll('input[type="date"]').forEach((input) => {
        if (!input.value) input.value = today;
    });
}

setDefaultDates();
updateAuthNavigation();
void loadEvents();

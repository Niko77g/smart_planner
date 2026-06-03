const $ = (selector) => document.querySelector(selector);
// pripravy text pred vlozeni do HTML aby sa user text nepraval ako HTML
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
// metoda, ktora urcuje ci sa zobrazi login register, alebo len odlasenie
function updateAuthNavigation() {
    const guestActions = document.querySelector("[data-guest-actions]");
    const userActions = document.querySelector("[data-user-actions]");
    const currentUser = document.querySelector("[data-current-user]");
    const isLoggedIn = Boolean(getToken());

    if (!guestActions || !userActions) return;

    guestActions.hidden = isLoggedIn;
    userActions.hidden = !isLoggedIn;

    if (currentUser && isLoggedIn) {
        currentUser.textContent = localStorage.getItem("username") || "Prihlásený používateľ";
    }
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
        return payload.detail || "Operáciu sa nepodarilo dokončiť.";
    } catch {
        return "Operáciu sa nepodarilo dokončiť.";
    }
}
// nacita udaje o aktualne prihlaseneho pouzivatela
async function loadEvents() {
    const list = $("#eventsList");

    if (!getToken()) {
        list.innerHTML = '<p class="empty-state">Pre zobrazenie udalostí sa musíš najprv prihlásiť.</p>';
        return;
    }

    list.innerHTML = '<p class="empty-state">Načítavam udalosti...</p>';

    try {
        const response = await fetch("/events/", {
            headers: authHeaders(),
        });
        if (!response.ok) {
            throw new Error(await readError(response));
        }

        const events = await response.json();
        if (events.length === 0) {
            list.innerHTML = '<p class="empty-state">Zatiaľ tu nemáš žiadne udalosti.</p>';
            return;
        }

        list.innerHTML = events.map((event) => `
            <article class="event-item">
                <div>
                    <span class="event-date">${escapeHtml(event.date)}</span>
                    <strong>${escapeHtml(event.title)}</strong>
                    <small>${escapeHtml(event.start)} - ${escapeHtml(event.end)}</small>
                </div>
                <button class="icon-button" type="button" data-delete-event="${event.id}">Odstrániť</button>
            </article>
        `).join("");
    } catch (error) {
        list.innerHTML = `<p class="empty-state">${escapeHtml(error.message)}</p>`;
    }
}

$("#predictForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const output = $("#predictResult");

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
            throw new Error(await readError(response));
        }

        const result = await response.json();
        showResult(output, "success", `
            <strong class="result-number">${escapeHtml(result.formatted)}</strong>
            Celkový odhad je ${result.predicted_minutes} minút.
            Pri pravidelnom učení je to približne <strong>${result.daily_minutes} minút denne</strong>.
        `);
    } catch (error) {
        showResult(output, "error", escapeHtml(error.message));
    }
});

$("#manualForm").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const output = $("#manualResult");

    if (!getToken()) {
        showResult(output, "error", 'Pred uložením udalosti sa musíš najprv prihlásiť.');
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

$("#eventsList").addEventListener("click", async (event) => {
    const button = event.target.closest("[data-delete-event]");
    if (!button) return;

    try {
        const response = await fetch(`/events/${button.dataset.deleteEvent}`, {
            method: "DELETE",
            headers: authHeaders(),
        });
        if (!response.ok) {
            throw new Error(await readError(response));
        }
        await loadEvents();
    } catch (error) {
        window.alert(error.message);
    }
});

$("#reloadEvents").addEventListener("click", loadEvents);

$("#logoutButton")?.addEventListener("click", () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    updateAuthNavigation();
    loadEvents();
});

function setDefaultDates() {
    const today = new Date().toISOString().split("T")[0];
    document.querySelectorAll('input[type="date"]').forEach((input) => {
        if (!input.value) input.value = today;
    });
}

setDefaultDates();
updateAuthNavigation();
loadEvents();

document.querySelectorAll(".password-toggle").forEach((button) => {
    button.addEventListener("click", () => {
        const input = button.parentElement.querySelector("input");
        const showPassword = input.type === "password";
        input.type = showPassword ? "text" : "password";
        button.textContent = showPassword ? "Skryť" : "Zobraziť";
    });
});

async function readError(response) {
    try {
        const payload = await response.json();
        return payload.detail || "Operáciu sa nepodarilo dokončiť.";
    } catch {
        return "Operáciu sa nepodarilo dokončiť.";
    }
}

function showMessage(message, type, text) {
    message.hidden = false;
    message.className = `auth-message ${type}`;
    message.textContent = text;
}

async function login(username, password) {
    const response = await fetch("/auth/login", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({username, password}),
    });

    if (!response.ok) {
        throw new Error(await readError(response));
    }

    return response.json();
}

document.querySelector(".auth-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const message = document.querySelector(".auth-message");
    const username = form.username.value.trim();
    const password = form.password.value;

    if (form.dataset.authForm === "register") {
        if (form.password.value !== form.password_confirm.value) {
            showMessage(message, "error", "Heslá sa nezhodujú.");
            return;
        }
    }

    try {
        if (form.dataset.authForm === "register") {
            const response = await fetch("/auth/register", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({username, password}),
            });

            if (!response.ok) {
                throw new Error(await readError(response));
            }
        }

        const token = await login(username, password);
        localStorage.setItem("access_token", token.access_token);
        localStorage.setItem("username", username);
        window.location.href = "/";
    } catch (error) {
        showMessage(message, "error", error.message);
    }
});

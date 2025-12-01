async function apiPost(url, data) {
    const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(data),
    });

    const json = await res.json().catch(() => ({}));
    if (!res.ok || json.success === false) {
        throw new Error(json.message || json.error || "Request failed");
    }
    return json;
}

// Simple toast helper
function toast(msg, type = "info") {
    let el = document.createElement("div");
    el.className = `toast toast-${type}`;
    el.textContent = msg;
    document.body.appendChild(el);
    requestAnimationFrame(() => (el.style.opacity = "1"));
    setTimeout(() => {
        el.style.opacity = "0";
        setTimeout(() => el.remove(), 300);
    }, 2500);
}

// Password show/hide toggles
document.addEventListener("click", (e) => {
    const btn = e.target.closest(".toggle-password");
    if (!btn) return;
    const input = btn.parentElement?.querySelector("input[type='password'], input[type='text']");
    if (!input) return;
    if (input.type === "password") {
        input.type = "text";
        btn.setAttribute("aria-label", "Hide password");
    } else {
        input.type = "password";
        btn.setAttribute("aria-label", "Show password");
    }
});

// REGISTER
const registerForm = document.getElementById("register-form");
if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const name = registerForm.querySelector("input[name='name']")?.value?.trim() || null;
        const email = registerForm.querySelector("input[name='email']").value.trim();
        const password = registerForm.querySelector("input[name='password']").value;
        const confirm_password = registerForm.querySelector("input[name='confirm_password']").value;

        try {
            await apiPost("/auth/register", { name, email, password, confirm_password });
            toast("Registration successful. Check your email to confirm your account.", "success");
            // Keep user on the same page or redirect to login where they can log in after confirming
            setTimeout(() => { window.location.href = "/auth/login"; }, 800);
        } catch (err) {
            toast("Register error: " + err.message, "error");
        }
    });
}

// LOGIN
const loginForm = document.getElementById("login-form");
if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = loginForm.querySelector("input[name='email']").value.trim();
        const password = loginForm.querySelector("input[name='password']").value;

        try {
            await apiPost("/auth/login", { email, password });
            window.location.href = "/dashboard";
        } catch (err) {
            toast("Login error: " + err.message, "error");
        }
    });
}

// LOGOUT
const logoutBtn = document.getElementById("logout-btn");
if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
        try {
            await apiPost("/auth/logout", {});
            window.location.href = "/";
        } catch (err) {
            toast("Logout error: " + err.message, "error");
        }
    });
}

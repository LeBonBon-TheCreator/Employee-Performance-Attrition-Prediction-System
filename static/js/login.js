const form = document.getElementById("loginForm");
const password = document.getElementById("password");
const togglePassword = document.getElementById("togglePassword");

// Toggle password visibility
togglePassword.addEventListener("click", () => {
    const type = password.getAttribute("type") === "password" ? "text" : "password";
    password.setAttribute("type", type);
    togglePassword.textContent = type === "password" ? "👁" : "❌";
});

// Login form submit
form.addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    const passwordValue = password.value.trim();

    if (!email || !passwordValue) {
        alert("Please enter email and password.");
        return;
    }

    try {
        const response = await fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: email, password: passwordValue })
        });

        const data = await response.json();

        if (data.success) {
            // Store session info in localStorage (optional)
            localStorage.setItem("user_id", data.id);
            localStorage.setItem("role", data.role);

            // Redirect to Flask dashboard route
            if (data.dashboard) {
                // Use absolute path to avoid wrong relative redirects
                window.location.href = data.dashboard;
            } else {
                // Fallback if dashboard URL missing
                window.location.href = data.role.toLowerCase() === "admin" ? "/admin-dashboard" : "/employee-dashboard";
            }
        } else {
            alert(data.message || "Login failed.");
        }

    } catch (error) {
        console.error("Login error:", error);
        alert("Server connection failed.");
    }
});
// =========================
// Worklytics Reset Password
// =========================
const newPassword = document.getElementById("newPassword");
const confirmPassword = document.getElementById("confirmPassword");
const toggleNew = document.getElementById("toggleNew");
const toggleConfirm = document.getElementById("toggleConfirm");
const form = document.getElementById("resetForm");

// Toggle new password visibility
toggleNew.addEventListener("click", () => {
    const type = newPassword.getAttribute("type") === "password" ? "text" : "password";
    newPassword.setAttribute("type", type);
    toggleNew.textContent = type === "password" ? "👁" : "❌";
});

// Toggle confirm password visibility
toggleConfirm.addEventListener("click", () => {
    const type = confirmPassword.getAttribute("type") === "password" ? "text" : "password";
    confirmPassword.setAttribute("type", type);
    toggleConfirm.textContent = type === "password" ? "👁" : "❌";
});

// Form submit
form.addEventListener("submit", async function(e) {
    e.preventDefault();

    const passwordValue = newPassword.value.trim();
    const confirmValue = confirmPassword.value.trim();
    const email = localStorage.getItem("reset_email"); // stored during forgot password

    if (!email) {
        alert("Session expired. Please request OTP again.");
        window.location.href = "/forgot-password";  // Flask route
        return;
    }

    if (!passwordValue || !confirmValue) {
        alert("Please fill all fields.");
        return;
    }

    if (passwordValue !== confirmValue) {
        alert("Passwords do not match!");
        return;
    }

    try {
        const response = await fetch("/api/reset-password", {  // relative Flask API route
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                email: email,
                new_password: passwordValue
            })
        });

        const data = await response.json();

        if (data.success) {
            alert("Password reset successful. Please login.");

            localStorage.removeItem("reset_email");
            window.location.href = "/login"; // redirect to Flask login route
        } else {
            alert(data.message || "Reset failed.");
        }

    } catch (error) {
        console.error("Reset password error:", error);
        alert("Server error. Try again.");
    }
});
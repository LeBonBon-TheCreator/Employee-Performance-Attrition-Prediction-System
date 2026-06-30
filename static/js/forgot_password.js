const form = document.getElementById("forgotForm");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const email = document.getElementById("email").value.trim();
    if (!email) {
        alert("Please enter your email.");
        return;
    }

    try {
        const response = await fetch("/api/forgot-password", {  // Use relative path
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email })
        });

        const data = await response.json();

        if (data.success) {
            alert(data.message || "OTP sent to your email.");
            localStorage.setItem("reset_email", email); // store the email for next step

            // Redirect to OTP verification page (relative path)
            window.location.href = `/otp-verification?email=${encodeURIComponent(email)}`;
        } else {
            alert(data.message || "Email not found.");
        }
    } catch (error) {
        console.error("Forgot password error:", error);
        alert("Server connection failed.");
    }
});
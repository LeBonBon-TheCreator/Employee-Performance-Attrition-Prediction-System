// Multi-input OTP handling
const inputs = document.querySelectorAll(".otp-input");

inputs.forEach((input, index) => {
    input.addEventListener("input", () => {
        if (input.value.length === 1 && index < inputs.length - 1) {
            inputs[index + 1].focus();
        }
    });

    input.addEventListener("keydown", (e) => {
        if (e.key === "Backspace" && input.value === "" && index > 0) {
            inputs[index - 1].focus();
        }
    });
});

// OTP form submission
document.getElementById("otpForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    // Combine all OTP inputs into a single string
    let otp = "";
    inputs.forEach(input => otp += input.value.trim());

    if (!otp) {
        alert("Please enter the OTP.");
        return;
    }

    const email = localStorage.getItem("reset_email"); // email saved during forgot password
    if (!email) {
        alert("No email found. Please start the forgot password process again.");
        window.location.href = "/forgot-password";
        return;
    }

    try {
        const response = await fetch("/api/verify-otp", {  // relative path
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: email, otp: otp })
        });

        const data = await response.json();

        if (data.success) {
            alert("OTP verified! Proceed to reset your password.");
            window.location.href = "/reset-password";  // relative route
        } else {
            alert(data.message || "Invalid OTP. Please try again.");
        }
    } catch (error) {
        console.error("OTP verification error:", error);
        alert("Server connection failed.");
    }
});

// ================================
// Resend OTP
// ================================
document.querySelector(".resend").addEventListener("click", async function (e) {
    e.preventDefault();

    const email = localStorage.getItem("reset_email");

    if (!email) {
        alert("Session expired. Please request OTP again.");
        window.location.href = "/forgot-password";
        return;
    }

    try {
        const response = await fetch("/api/forgot-password", {  // relative path
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: email })
        });

        const data = await response.json();

        if (data.success) {
            alert("New OTP sent to your email.");
        } else {
            alert(data.message || "Failed to resend OTP.");
        }

    } catch (error) {
        console.error(error);
        alert("Server error. Try again.");
    }
});
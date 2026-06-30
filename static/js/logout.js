// ================================
// Admin Dashboard Logout
// ================================
const logoutBtn = document.getElementById("logoutBtn");

logoutBtn.addEventListener("click", async (e) => {
    e.preventDefault();
    try {
        const response = await fetch("/logout", { method: "POST" });
        const data = await response.json();
        if (data.success) {
            window.location.href = "/login"; // redirect to Flask login route
        } else {
            alert("Logout failed.");
        }
    } catch (error) {
        console.error(error);
        alert("Server error. Try again.");
    }
});
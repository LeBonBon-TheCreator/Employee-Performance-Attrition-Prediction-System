document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
});

async function loadDashboard() {
    try {
        const response = await fetch('/api/get-my-data');
        const result = await response.json();

        if (result.success) {
            const data = result.data;

            // 1. Sidebar Profile (Name and Position)
            document.getElementById('side_name').innerText = data.employee_name;
            document.getElementById('side_role').innerText = data.position;
            document.getElementById('welcome_name').innerText = data.employee_name;
        }
    } catch (err) {
        console.error("Dashboard error:", err);
    }
}

document.getElementById('changePasswordForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const msgBox = document.getElementById('messageBox');
    
    const formData = {
        current_password: document.getElementById('current_password').value,
        new_password: document.getElementById('new_password').value,
        confirm_password: document.getElementById('confirm_password').value
    };

    try {
        const response = await fetch('/api/change-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });
        const result = await response.json();

        msgBox.innerText = result.message;
        msgBox.className = result.success ? "message-box msg-success" : "message-box msg-error";
        
        if (result.success) {
            document.getElementById('changePasswordForm').reset();
        }
    } catch (err) {
        msgBox.innerText = "An error occurred. Please try again.";
        msgBox.className = "message-box msg-error";
    }
});
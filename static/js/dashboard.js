const POWER_AUTOMATE_URL = "https://defaultae5ed6e2682f4436a3d2d07186f2c1.da.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/f3c31c86d784408f91a96f72ae6bd571/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=LURo_vCNle_qE65dBEk128fR4WyYT53W1l_aMXkh6PU";

document.addEventListener('DOMContentLoaded', function() {
    const syncBtn = document.getElementById('syncBtn');
    if (syncBtn) {
        syncBtn.addEventListener('click', refreshDashboard);
    }
});

async function refreshDashboard() {
    const btn = document.getElementById('syncBtn');
    const overlay = document.getElementById('loadingOverlay');
    const iframe = document.getElementById('pbiIframe');
    const statusText = document.getElementById('statusText');

    // Check if elements exist to avoid the "Cannot read properties of null" error
    if (!btn || !overlay || !iframe || !statusText) {
        console.error("Required HTML elements (IDs) are missing in dashboard.html");
        return;
    }

    // 1. UI Feedback
    btn.disabled = true;
    overlay.style.display = "flex"; // Ensure your CSS handles .loading-overlay display
    statusText.innerText = "Triggering Cloud Refresh...";

    try {
        // 2. Trigger Power Automate
        await fetch(POWER_AUTOMATE_URL, {
            method: 'POST',
            mode: 'no-cors', 
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ "trigger": "manual_sync" })
        });

        statusText.innerText = "Gateway syncing data...";

        // 3. Buffer for Data Gateway to finish
        setTimeout(() => {
            statusText.innerText = "Reloading Visuals...";
            
            // Refresh iframe
            const currentSrc = iframe.src;
            iframe.src = ''; 
            iframe.src = currentSrc;

            // 4. Reset
            setTimeout(() => {
                overlay.style.display = "none";
                btn.disabled = false;
                statusText.innerText = "Active Insights";
            }, 2000);

        }, 12000);

    } catch (error) {
        console.error("Sync failed:", error);
        overlay.style.display = "none";
        btn.disabled = false;
        statusText.innerText = "Sync Error";
    }
}
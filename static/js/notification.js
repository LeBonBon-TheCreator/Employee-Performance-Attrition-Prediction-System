document.addEventListener('DOMContentLoaded', function() {
    const bellIcon = document.querySelector('.notification-bell');
    const notificationDot = document.querySelector('.notification-dot');

    fetch('/api/risk-stats')
        .then(response => response.json())
        .then(data => {
            if (data.high_risk_count > 0) {
                // Always show the red dot if there is risk
                notificationDot.style.display = 'block';

                // Check if the sound has already played in this session
                const hasPlayed = sessionStorage.getItem('risk_alert_played');

                if (!hasPlayed) {
                    // Create a one-time click listener to bypass browser autoplay blocks
                    const playOnce = () => {
                        const audio = new Audio('/static/sounds/notification.wav');
                        audio.play().catch(e => console.log("Playback interaction required"));
                        
                        // Set the flag so it doesn't play again this session
                        sessionStorage.setItem('risk_alert_played', 'true');
                        
                        document.removeEventListener('click', playOnce);
                    };
                    document.addEventListener('click', playOnce);
                }

                bellIcon.onclick = () => {
                    const modal = document.getElementById('risk-alert-box');
                    document.getElementById('risk-count-text').innerText = 
                        `There are ${data.high_risk_count} employees identified as High Risk.`;
                    modal.style.display = 'block';
                };
            }
        });
});

// Function to check risk and set up the alert
function checkRiskNotifications() {
    fetch('/api/risk-stats')
        .then(response => response.json())
        .then(data => {
            if (data.high_risk_count > 0) {
                const bellIcon = document.querySelector('.notification-bell');
                const notificationDot = document.querySelector('.notification-dot');
                
                notificationDot.style.display = 'block';

                // We "prime" the audio to play on the first click anywhere on the page
                const playAlert = () => {
                    const audio = new Audio('/static/sounds/notification.wav');
                    audio.play().catch(e => console.log("Playback failed:", e));
                    // Remove listener so it only plays once
                    document.removeEventListener('click', playAlert);
                };
                
                document.addEventListener('click', playAlert);

                bellIcon.onclick = () => {
                    const modal = document.getElementById('risk-alert-box');
                    const text = document.getElementById('risk-count-text');
                    // Set the count dynamically
                    text.innerText = `There are currently ${data.high_risk_count} employees identified as High Risk.`;
                    modal.style.display = 'block';
                    notificationDot.style.display = 'none';
                };

                // Close modal when 'x' is clicked
                document.querySelector('.close-btn').onclick = () => {
                    document.getElementById('risk-alert-box').style.display = 'none';
                };
            }
        });
}

document.addEventListener('DOMContentLoaded', checkRiskNotifications);
document.addEventListener('DOMContentLoaded', () => {
    loadDashboard();
});

async function loadDashboard() {
    try {
        const response = await fetch('/api/get-my-data');
        const result = await response.json();

        if (result.success) {
            const data = result.data;
            const review = result.review;
            const charts = result.charts;

            // 1. Sidebar Profile (Name and Position)
            document.getElementById('side_name').innerText = data.employee_name;
            document.getElementById('side_role').innerText = data.position;
            document.getElementById('welcome_name').innerText = data.employee_name;

            // 2. Metrics Update
            if (review) {
                document.getElementById('last_review_date').innerText = review.review_date;
                document.getElementById('mgr_rating').innerText = review.manager_rating.toFixed(1);
                document.getElementById('self_rating').innerText = review.self_rating.toFixed(1);
                
                // KPI Logic
                const kpiPercent = ((review.actual_kpi / review.target_kpi) * 100).toFixed(1);
                document.getElementById('kpi_percent').innerText = `${kpiPercent}%`;
                document.getElementById('kpi_details').innerText = `Actual: ${review.actual_kpi}% | Target: ${review.target_kpi}%`;

                // 3. Render Python Plotly Charts
                // Plotly.newPlot can take the JSON data directly
                Plotly.newPlot('satisfactionChart', charts.satisfaction_radar.data, charts.satisfaction_radar.layout, {responsive: true});
                Plotly.newPlot('ratingComparisonChart', charts.rating_bar.data, charts.rating_bar.layout, {responsive: true});
            }
        }
    } catch (err) {
        console.error("Dashboard error:", err);
    }
}
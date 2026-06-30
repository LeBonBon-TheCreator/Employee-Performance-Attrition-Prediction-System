document.addEventListener('DOMContentLoaded', () => {
    loadAllHistory();
});

async function loadAllHistory() {
    try {
        const response = await fetch('/api/all-risk-history');
        const result = await response.json();

        if (result.success) {
            renderHistoryTable(result.data);
        }
    } catch (error) {
        console.error("Error loading history:", error);
    }
}

function renderHistoryTable(data) {
    const tbody = document.getElementById('historyTableBody');
    tbody.innerHTML = '';

    data.forEach(entry => {
        const scorePercent = Math.round(entry.risk_score * 100);
        const riskClass = `badge-${entry.risk_level.toLowerCase()}`;
        const date = new Date(entry.calculated_at).toLocaleDateString('en-GB', {
            day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
        });

        tbody.innerHTML += `
            <tr>
                <td class="date-column">${date}</td>
                <td><strong>${entry.employee_id}</strong></td>
                <td>${entry.employee_name}</td>
                <td class="score-value">${scorePercent}%</td>
                <td>
                    <span class="badge-base badge-${entry.risk_level.toLowerCase()}">
                        ${entry.risk_level}
                    </span>
                </td>
                <td class="reason-text">${entry.primary_reason}</td>
            </tr>
        `;
    });
}

function filterHistory() {
    const input = document.getElementById("historySearch").value.toLowerCase();
    const table = document.getElementById("historyTableBody");
    const rows = table.getElementsByTagName("tr");

    for (let i = 0; i < rows.length; i++) {
        // Index 1 = ID, Index 2 = Name
        const idCol = rows[i].getElementsByTagName("td")[1];
        const nameCol = rows[i].getElementsByTagName("td")[2];
        
        if (idCol && nameCol) {
            const idValue = idCol.textContent || idCol.innerText;
            const nameValue = nameCol.textContent || nameCol.innerText;
            
            if (idValue.toLowerCase().includes(input) || 
                nameValue.toLowerCase().includes(input)) {
                rows[i].style.display = "";
            } else {
                rows[i].style.display = "none";
            }
        }
    }
}
document.addEventListener('DOMContentLoaded', () => {
    // Initial Load
    loadReviewTable();

    // Search and Filter Listeners
    document.getElementById('searchInput').addEventListener('input', applyFilters);
    document.getElementById('deptFilter').addEventListener('change', applyFilters);
    document.getElementById('sortType').addEventListener('change', applyFilters);
    document.getElementById('riskFilter').addEventListener('change', applyFilters);
});

let allEmployees = [];

async function loadReviewTable() {
    try {
        const res = await fetch('/api/get-employees');
        const data = await res.json();
        if (data.success) {
            allEmployees = data.data;
            renderTable(allEmployees);
        }
    } catch (err) {
        console.error("Error loading employees:", err);
    }
}

function renderTable(employees) {
    const tbody = document.getElementById('reviewTableBody');
    tbody.innerHTML = '';
    
    employees.forEach(emp => {
        // Use the level and score directly from your new table
        const level = emp.risk_level || 'Low';
        const displayScore = emp.risk_score ? Math.round(emp.risk_score * 100) : 0;
        const riskClass = `risk-${level.toLowerCase()}`;
        let displayDate = 'Pending';
        if (emp.latest_review_date) {
            const dateObj = new Date(emp.latest_review_date);
            displayDate = dateObj.toISOString().split('T')[0];
        }

        tbody.innerHTML += `
            <tr>
                <td>${emp.employee_id}</td>
                <td>${emp.employee_name}</td>
                <td>${emp.department}</td>
                <td>${emp.position}</td>
                <td>
                    <span class="risk-badge ${riskClass}">
                        ${level} (${displayScore}%)
                    </span>
                </td>
                <td>${displayDate}</td>
                <td>
                    <button class="btn-review" onclick="openReviewModal('${emp.employee_id}')">Start Review</button>
                </td>
            </tr>`;
    });
}

window.openReviewModal = async (empId) => {
    const modal = document.getElementById("reviewModal");
    
    try {
        const res = await fetch(`/api/get-employee/${empId}`);
        const result = await res.json();
        
        if (result.success) {
            const emp = result.data;
            // Set values in the modal
            document.getElementById("review_emp_id").value = emp.employee_id;
            document.getElementById("review_name_display").innerText = emp.employee_name;
            
            // Reset the form and slider outputs
            document.getElementById("performanceReviewForm").reset();
            document.querySelectorAll('#performanceReviewForm output').forEach(out => {
                out.value = 3; // Reset visual text of sliders to middle
            });
            
            // Show the modal
            modal.style.display = "flex"; 
        }
    } catch (err) {
        console.error("Failed to open modal:", err);
    }
};

window.closeReviewModal = () => {
    document.getElementById("reviewModal").style.display = "none";
};

// Handle Form Submission
document.getElementById("performanceReviewForm").onsubmit = async (e) => {
    e.preventDefault();
    
    // 1. Get the form data
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    data.employee_id = document.getElementById("review_emp_id").value;

    try {
        const response = await fetch('/api/update-performance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert("Performance review saved successfully! Attrition risk updated.");
            
            // 3. Close the modal
            closeReviewModal();
            
            // 4. Refresh the table to show the new risk levels
            await loadReviewTable();
            
        } else {
            alert("Error: " + result.message);
        }
    } catch (error) {
        console.error("Submission error:", error);
        alert("An error occurred while saving the review.");
    }
};

function applyFilters() {
    let filtered = [...allEmployees]; 
    
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const selectedDept = document.getElementById('deptFilter').value;
    const sortValue = document.getElementById('sortType').value;
    const riskFilter = document.getElementById('riskFilter').value;

    // Filter by Name or ID
    if (searchTerm) {
        filtered = filtered.filter(emp => 
            emp.employee_name.toLowerCase().includes(searchTerm) || 
            emp.employee_id.toLowerCase().includes(searchTerm)
        );
    }

    // Filter by Department
    if (selectedDept !== 'All') {
        filtered = filtered.filter(emp => emp.department === selectedDept);
    }

    // Filter by Risk Status
    if (riskFilter !== 'All') {
        filtered = filtered.filter(emp => emp.risk_level === riskFilter);
    }

    // Sort Logic
    filtered.sort((a, b) => {
        switch (sortValue) {
            case 'name_asc':
                return a.employee_name.localeCompare(b.employee_name);
            case 'name_desc':
                return b.employee_name.localeCompare(a.employee_name);
            case 'id_asc':
                return a.employee_id.localeCompare(b.employee_id);
            case 'id_desc':
                return b.employee_id.localeCompare(a.employee_id);
            default:
                return 0;
        }
    });

    // Update the table with the result
    renderTable(filtered);
}
async function loadFullProfile() {
    const res = await fetch('/api/get-full-profile');
    const result = await res.json();
    
    if (result.success) {
        const d = result.data;
        // Sidebar (inherited from previous logic)
        document.getElementById('side_name').innerText = d.employee_name;
        document.getElementById('side_role').innerText = d.position;

        // Identity
        document.getElementById('p_name').innerText = d.employee_name;
        document.getElementById('p_id').innerText = d.employee_id;
        document.getElementById('p_dob').innerText = d.dob;
        document.getElementById('p_gender').innerText = d.gender;
        document.getElementById('p_ethnicity').innerText = d.ethnicity;

        // Career
        document.getElementById('p_edu').innerText = `Level ${d.education}`;
        document.getElementById('p_field').innerText = d.education_field;
        document.getElementById('p_marital').innerText = d.marital_status;
        document.getElementById('p_hire').innerText = d.hire_date;

        // Job
        document.getElementById('p_dept').innerText = d.department;
        document.getElementById('p_pos').innerText = d.position;
        document.getElementById('p_role_start').innerText = d.role_start_date;
        document.getElementById('p_promo').innerText = d.last_promotion_date || 'N/A';
        document.getElementById('p_salary').innerText = `RM ${d.salary.toLocaleString()}`;

        // Logistics
        document.getElementById('p_travel').innerText = d.business_travel;
        document.getElementById('p_ot').innerText = d.over_time;
        document.getElementById('p_stock').innerText = d.stock_option_level;
        document.getElementById('p_dist').innerText = `${d.distance_from_home_km} KM`;
    }
}

document.addEventListener('DOMContentLoaded', loadFullProfile);
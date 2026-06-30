// 1. Declare variables GLOBALLY at the top
let editMode = false;
let addEmployeeModal, addEmployeeBtn, closeModal, addEmployeeForm;
let deptSelect, posSelect, managerSelect, empIdInput;
let allEmployees = []; 
const managerRoles = ["Engineering Manager", "Analytics Manager", "Manager", "HR Manager"];

document.addEventListener('DOMContentLoaded', () => {
    // 2. ASSIGN elements to those global variables (Do NOT use 'const' or 'let' here)
    addEmployeeModal = document.getElementById('addEmployeeModal');
    addEmployeeBtn = document.getElementById('addEmployeeBtn');
    closeModal = document.querySelector('.close-modal');
    addEmployeeForm = document.getElementById('addEmployeeForm');
    deptSelect = document.getElementById('deptSelect');
    posSelect = document.getElementById('posSelect');
    managerSelect = document.getElementById('managerSelect');
    empIdInput = document.getElementById('emp_id_input');

    loadEmployees();

    // Reset for "Add" mode
    addEmployeeBtn.addEventListener('click', () => {
        editMode = false;
        addEmployeeForm.reset();
        document.querySelector('.modal-content h3').innerText = "Add New Employee";
        document.querySelector('.btn-save').innerText = "Save Employee";
        addEmployeeModal.style.display = 'flex';
        fetchNextEmpId(); 
    });

    closeModal.addEventListener('click', () => {
        addEmployeeModal.style.display = 'none';
    });

    // Filtering logic for Positions
    deptSelect.addEventListener('change', function() {
        const selectedDept = this.value;
        const options = posSelect.querySelectorAll('option');
        posSelect.disabled = !selectedDept;
        options.forEach(opt => {
            const optDept = opt.getAttribute('data-dept');
            if(optDept) opt.style.display = (optDept === selectedDept) ? "block" : "none";
        });
        posSelect.value = ""; 
    });

    // Filtering logic for Managers
    posSelect.addEventListener('change', updateManagerList);

    // Form Submission (Handles both Add and Update)
    addEmployeeForm.onsubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData(addEmployeeForm);
        const data = Object.fromEntries(formData.entries());
        
        // Ensure manual fields are captured
        data.emp_id = empIdInput.value;
        data.manager_id = managerSelect.value;

        const endpoint = editMode ? '/api/update-employee' : '/api/add-employee';

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        if (result.success) {
            alert(editMode ? "Employee Updated!" : "Employee Added!");
            location.reload();
        } else {
            alert("Error: " + result.message);
        }
    };

    // Table Filter Listeners
    document.getElementById('searchInput').addEventListener('input', applyFilters);
    document.getElementById('deptFilter').addEventListener('change', applyFilters);
    document.getElementById('sortType').addEventListener('change', applyFilters);
});

// --- GLOBAL FUNCTIONS ---

async function loadEmployees() {
    const res = await fetch('/api/get-employees');
    const data = await res.json();
    if (data.success) {
        allEmployees = data.data;
        renderTable(allEmployees);
    }
}

function renderTable(data) {
    const tbody = document.getElementById('employeeTableBody');
    tbody.innerHTML = '';
    data.forEach(emp => {
        tbody.innerHTML += `
            <tr>
                <td>${emp.employee_id}</td>
                <td>${emp.employee_name}</td>
                <td>${emp.department}</td>
                <td>${emp.position}</td>
                <td>
                    <button class="btn-edit" onclick="editEmployee('${emp.employee_id}')">Edit</button>
                    <button class="btn-delete" onclick="deleteEmployee('${emp.employee_id}')">Delete</button>
                </td>
            </tr>`;
    });
}

async function updateManagerList() {
    const isManager = managerRoles.includes(posSelect.value);
    const currentEditingId = empIdInput.value; 

    if (isManager) {
        managerSelect.innerHTML = '<option value="">Top Level (No Manager)</option>';
        managerSelect.value = "";
        managerSelect.disabled = true;
    } else {
        managerSelect.disabled = false;
        const res = await fetch(`/api/get-managers-by-dept?department=${deptSelect.value}`);
        const data = await res.json();
        
        let html = '<option value="">Assign Manager (Optional)</option>';
        if (data.success) {
            data.managers.forEach(m => {
                // ONLY add to list if it's not the person themselves
                if (m.employee_id !== currentEditingId) {
                    html += `<option value="${m.employee_id}">${m.employee_name} (${m.employee_id})</option>`;
                }
            });
        }
        managerSelect.innerHTML = html;
    }
}

async function editEmployee(empId) {
    editMode = true;
    const res = await fetch(`/api/get-employee/${empId}`);
    const result = await res.json();

    if (result.success) {
        const emp = result.data;
        
        // Fill the fields
        empIdInput.value = emp.employee_id;
        addEmployeeForm.full_name.value = emp.employee_name;
        addEmployeeForm.email.value = emp.email || "";
        
        const dobField = document.getElementById('dob');
        if (emp.dob) {
            // ensures get ONLY YYYY-MM-DD 
        const dateMatch = emp.dob.match(/^\d{4}-\d{2}-\d{2}/);
        dobField.value = dateMatch ? dateMatch[0] : "";
    }
        addEmployeeForm.gender.value = emp.gender;
        addEmployeeForm.marital_status.value = emp.marital_status;
        addEmployeeForm.ethnicity.value = emp.ethnicity;
        addEmployeeForm.state.value = emp.state;
        addEmployeeForm.education.value = emp.education;
        addEmployeeForm.education_field.value = emp.education_field;
        addEmployeeForm.department.value = emp.department;

        // Trigger filters to show correct positions/managers
        deptSelect.dispatchEvent(new Event('change'));
        posSelect.value = emp.position;
        
        await updateManagerList();
        managerSelect.value = emp.manager_id || "";

        addEmployeeForm.salary.value = emp.salary;
        addEmployeeForm.distance_km.value = emp.distance_from_home_km;
        addEmployeeForm.business_travel.value = emp.business_travel;
        addEmployeeForm.over_time.value = emp.over_time;
        addEmployeeForm.stock_option_level.value = emp.stock_option_level;

        document.querySelector('.modal-content h3').innerText = "Edit Employee";
        document.querySelector('.btn-save').innerText = "Update Employee";
        addEmployeeModal.style.display = 'flex';
    }
}

async function deleteEmployee(empId) {
    if (!confirm(`Delete ${empId}?`)) return;
    const res = await fetch(`/api/delete-employee/${empId}`, { method: 'DELETE' });
    const result = await res.json();
    if (result.success) {
        alert(result.message);
        location.reload();
    } else {
        alert(result.message);
    }
}

async function fetchNextEmpId() {
    const res = await fetch('/api/get-next-employee-id');
    const data = await res.json();
    if (data.success) empIdInput.value = data.next_id;
}

function applyFilters() {
    let filtered = [...allEmployees];
    const search = document.getElementById('searchInput').value.toLowerCase();
    const dept = document.getElementById('deptFilter').value;
    const sort = document.getElementById('sortType').value;

    if (search) filtered = filtered.filter(e => e.employee_name.toLowerCase().includes(search) || e.employee_id.toLowerCase().includes(search));
    if (dept !== 'All') filtered = filtered.filter(e => e.department === dept);

    filtered.sort((a, b) => {
        if (sort === 'id_desc') return b.employee_id.localeCompare(a.employee_id);
        if (sort === 'id_asc') return a.employee_id.localeCompare(b.employee_id);
        if (sort === 'name_asc') return a.employee_name.localeCompare(b.employee_name);
        if (sort === 'name_desc') return b.employee_name.localeCompare(a.employee_name);
        return 0;
    });
    renderTable(filtered);
}

// Map globally
window.editEmployee = editEmployee;
window.deleteEmployee = deleteEmployee;
CREATE DATABASE worklytics_db;
USE worklytics_db;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'employee') NOT NULL,
    employee_id VARCHAR(20) UNIQUE NULL, -- Links to employees table
    OTP VARCHAR(6) NULL,
    OTPExpiry DATETIME NULL,
    INDEX (employee_id)
);

CREATE TABLE employees (
    employee_id VARCHAR(20) PRIMARY KEY,
    employee_name VARCHAR(100) NOT NULL,
    dob DATE NOT NULL,
    gender ENUM('Male', 'Female', 'Non-Binary', 'Prefer Not To Say') NOT NULL,
    ethnicity VARCHAR(50) NOT NULL,
    state VARCHAR(50) NOT NULL,
    marital_status ENUM('Single', 'Married', 'Divorced') NOT NULL,
    education INT DEFAULT 1, 
    education_field VARCHAR(50),
    hire_date DATE NOT NULL,
    -- Links back to users for account deletion sync
    FOREIGN KEY (employee_id) REFERENCES users(employee_id) ON DELETE CASCADE
);

-- 3. Workplace & Operational Details (Mutable/Assignment)
CREATE TABLE job_details (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id VARCHAR(20) UNIQUE NOT NULL,
    department VARCHAR(50) NOT NULL,
    position VARCHAR(50) NOT NULL,
    role_start_date DATE NOT NULL,
    last_promotion_date DATE,
    manager_id VARCHAR(20) NULL,
    manager_assign_date DATE NULL,
    salary INT NOT NULL,
    stock_option_level INT DEFAULT 0,
    distance_from_home_km INT DEFAULT 0,
    business_travel ENUM('No Travel', 'Some Travel', 'Frequently') DEFAULT 'No Travel',
    over_time ENUM('Yes', 'No') DEFAULT 'No',
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    FOREIGN KEY (manager_id) REFERENCES employees(employee_id) ON DELETE SET NULL
);

-- 4. Performance History
CREATE TABLE performance_reviews (
    review_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id VARCHAR(20) NOT NULL,
    review_date DATE NOT NULL,
    env_satisfaction INT DEFAULT 3,
    job_satisfaction INT DEFAULT 3,
    rel_satisfaction INT DEFAULT 3,
    self_rating INT DEFAULT 3,
    manager_rating INT DEFAULT 3,
    target_kpi FLOAT DEFAULT 100.0,
    actual_kpi FLOAT DEFAULT 100.0,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);

-- 5. Risk Assessments (ML Output)
CREATE TABLE risk_assessments (
    assessment_id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id VARCHAR(20),
    risk_score FLOAT,           
    risk_level VARCHAR(10),     
    primary_reason TEXT,        
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    -- Merged the Cascade delete here
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE
);


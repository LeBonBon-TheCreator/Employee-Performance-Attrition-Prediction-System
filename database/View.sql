CREATE OR REPLACE VIEW v_powerbi_hr_analytics AS
SELECT 
    -- 1. Identity & Demographics
    e.employee_id,
    e.employee_name,
    e.gender,
    e.ethnicity,
    e.state,
    e.marital_status,
    e.education,
    e.education_field,
    
    -- 2. Workplace Details
    j.department,
    j.position,
    CAST(j.salary AS SIGNED) AS monthly_income,
    CAST((j.salary * 12) AS SIGNED) AS annual_salary,
    j.over_time,
    CAST(j.distance_from_home_km AS DECIMAL(10,2)) AS distance_from_home_km,
    j.business_travel,
    
    -- 3. Tenure & Timing (CRITICAL FIXES HERE)
    e.hire_date,
    -- Explicitly cast Age as an Integer to stop DirectQuery Min/Max errors
    CAST(TIMESTAMPDIFF(YEAR, e.dob, CURDATE()) AS SIGNED) AS age,
    -- Rounding decimals helps the driver fold the query correctly
    ROUND(TIMESTAMPDIFF(MONTH, e.hire_date, CURDATE()) / 12.0, 2) AS years_at_company,
    ROUND(TIMESTAMPDIFF(MONTH, j.role_start_date, CURDATE()) / 12.0, 2) AS years_in_role,
    ROUND(TIMESTAMPDIFF(MONTH, j.last_promotion_date, CURDATE()) / 12.0, 2) AS years_since_last_promotion,
    
    -- 4. Latest Performance Review
    r.review_date,
    CAST(r.manager_rating AS SIGNED) AS manager_rating,
    CAST(r.self_rating AS SIGNED) AS self_rating,
    CAST((r.manager_rating - r.self_rating) AS SIGNED) AS perf_gap,
    CAST(r.actual_kpi AS DECIMAL(10,2)) AS actual_kpi,
    CAST(r.target_kpi AS DECIMAL(10,2)) AS target_kpi,
    ROUND(COALESCE((r.actual_kpi / NULLIF(r.target_kpi, 0)) * 100, 0), 2) AS kpi_achievement_pct,
    CAST(r.env_satisfaction AS SIGNED) AS env_satisfaction,
    CAST(r.job_satisfaction AS SIGNED) AS job_satisfaction,
    CAST(r.rel_satisfaction AS SIGNED) AS rel_satisfaction,
    ROUND((r.env_satisfaction + r.job_satisfaction + r.rel_satisfaction) / 3.0, 2) AS avg_satisfaction,
    
    -- 5. Latest ML Risk Assessment
    CAST(ra.risk_score AS DECIMAL(10,4)) AS risk_score,
    ra.risk_level,
    ra.primary_reason AS xai_reason,
    ra.calculated_at AS last_assessed_at

FROM employees e
JOIN job_details j ON e.employee_id = j.employee_id
LEFT JOIN (
    SELECT p1.* FROM performance_reviews p1
    JOIN (SELECT employee_id, MAX(review_date) as max_date FROM performance_reviews GROUP BY employee_id) p2
    ON p1.employee_id = p2.employee_id AND p1.review_date = p2.max_date
) r ON e.employee_id = r.employee_id
LEFT JOIN (
    SELECT ra1.* FROM risk_assessments ra1
    JOIN (SELECT employee_id, MAX(calculated_at) as max_date FROM risk_assessments GROUP BY employee_id) ra2
    ON ra1.employee_id = ra2.employee_id AND ra1.calculated_at = ra2.max_date
) ra ON e.employee_id = ra.employee_id;
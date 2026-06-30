from pydoc import text
from flask import Flask, request, jsonify, session, redirect, render_template
from flask_cors import CORS
from matplotlib import text
import pymysql
import pymysql.cursors
import pytz
import random
import string
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta, date
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import joblib
import plotly.graph_objects as go
import plotly.io as pio
import json
import os
import dill
pymysql.install_as_MySQLdb()

app = Flask(__name__, template_folder="templates")
app.secret_key = "worklytics_secret_key"
app.permanent_session_lifetime = timedelta(hours=2)

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'model')

# Load the Random Forest Model and the LIME Explainer
attrition_model = joblib.load(os.path.join(MODEL_DIR, 'attrition_rf_model.pkl'))
with open(os.path.join(MODEL_DIR, 'lime_explainer.pkl'), 'rb') as f:
    explainer = dill.load(f)

CORS(app)

def get_malaysia_time():
    """Returns the current time specifically for the Malaysia timezone (UTC+8)."""
    kl_tz = pytz.timezone('Asia/Kuala_Lumpur')
    return datetime.now(kl_tz)

def get_db_connection():
    conn = pymysql.connect(**db_config)
    with conn.cursor() as cursor:
        cursor.execute("SET time_zone = '+08:00'")
    return conn

# -----------------------------
# Database Configuration
# -----------------------------
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "$Hyang8964",
    "database": "worklytics_db"
}

# Admin Setup Route - Run this once to create the initial admin user, Only for a one-time setup
@app.route('/api/setup-admin')
def setup_admin():
    hashed_pw = generate_password_hash("shyang89", method='pbkdf2:sha256')
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO users (email, password, role) VALUES (%s, %s, %s)", 
                           ("shyang04@gmail.com", hashed_pw, "admin"))
        conn.commit()
        return "Admin Created!"
    except Exception as e:
        return str(e)
    finally:
        conn.close()

# =============================
# MACHINE LEARNING 
# =============================       
def calculate_age(birth_date):
    if not birth_date:
        return 35
    
    # Convert string birth_date to date object
    if isinstance(birth_date, str):
        birth_date = date.fromisoformat(birth_date)
        
    #  get a fresh date object for 'today'
    today = get_malaysia_time().date() 
    
    # Math (Date Object - Date Object)
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

def prepare_ml_features(emp_id, cursor):
    # Fetch raw data
    query = """
        SELECT e.*, j.*, r.*
        FROM employees e
        JOIN job_details j ON e.employee_id = j.employee_id
        LEFT JOIN performance_reviews r ON e.employee_id = r.employee_id
        WHERE e.employee_id = %s
        ORDER BY r.review_date DESC, r.review_id DESC
        LIMIT 1
    """

    now_kl = get_malaysia_time()
    today_date_obj = now_kl.date()

    def to_date_obj(val):
        if val is None: return None
        if isinstance(val, str):
            return datetime.strptime(val, '%Y-%m-%d').date()
        if isinstance(val, datetime):
            return val.date()
        return val

    cursor.execute(query, (emp_id,))
    data = cursor.fetchone()
    if not data: return None
    
    # Essential Dates
    # Convert all DB dates to objects
    h_date = to_date_obj(data.get('hire_date')) or today_date_obj
    role_date = to_date_obj(data.get('role_start_date')) or h_date
    promo_date = to_date_obj(data.get('last_promotion_date')) or h_date
    manager_date = to_date_obj(data.get('manager_assign_date')) or h_date
    review_date = to_date_obj(data.get('review_date')) or h_date

    years_in_company = (today_date_obj - h_date).days / 365.25
    tenure = (today_date_obj - review_date).days / 365.25
    years_in_role = (today_date_obj - role_date).days / 365.25
    years_since_promo = (today_date_obj - promo_date).days / 365.25
    years_with_manager = (today_date_obj - manager_date).days / 365.25

    # Satisfaction Averages
    avg_sat = (
        (data.get('env_satisfaction') or 3) + 
        (data.get('job_satisfaction') or 3) + 
        (data.get('rel_satisfaction') or 3)
    ) / 3
    
    # Performance Gap
    perf_gap = (data.get('manager_rating') or 3) - (data.get('self_rating') or 3)
    
    # Salary calculation
    annual_salary = (data.get('salary') or 0) * 12
    current_age = calculate_age(data.get('dob'))

    # Build the 55-column dictionary
    feat = {
        'Age': current_age,
        'DistanceFromHomeKM': data.get('distance_from_home_km', 0),
        'Education': data.get('education', 1), 
        'Salary': annual_salary,
        'StockOptionLevel': data.get('stock_option_level', 0),
        'YearsAtCompany': years_in_company,
        'YearsInMostRecentRole': years_in_role,
        'YearsSinceLastPromotion': years_since_promo,
        'YearsWithCurrManager': years_with_manager,
        'TenureAtReview': tenure,
        'AvgSatisfaction': avg_sat,
        'PerformanceGap': perf_gap,
        
        # Gender
        'Gender_Male': 1 if data.get('gender') == 'Male' else 0,
        'Gender_Non-Binary': 1 if data.get('gender') == 'Non-Binary' else 0,
        'Gender_Prefer Not To Say': 1 if data.get('gender') == 'Prefer Not To Say' else 0,
        
        # Travel & Dept 
        'BusinessTravel_No Travel': 1 if data.get('business_travel') == 'No Travel' else 0,
        'BusinessTravel_Some Travel': 1 if data.get('business_travel') == 'Some Travel' else 0,
        'Department_Sales': 1 if data.get('department') == 'Sales' else 0,
        'Department_Technology': 1 if data.get('department') == 'Technology' else 0,
        
        # Geography
        'State_IL': 1 if data.get('state') in ['Penang', 'Selangor'] else 0,
        'State_NY': 1 if data.get('state') == 'Kuala Lumpur' else 0,
        
        # Ethnicity
        'Ethnicity_Asian or Asian American': 1 if data.get('ethnicity') in ['Chinese', 'Malay', 'Indian'] else 0,
        'Ethnicity_Black or African American': 0,
        'Ethnicity_Mixed or multiple ethnic groups': 1 if data.get('ethnicity') == 'Mixed' else 0,
        'Ethnicity_Native Hawaiian': 0,
        'Ethnicity_White': 0,
        'Ethnicity_Other': 1 if data.get('ethnicity') == 'Others' else 0,

        
        # Education Field (Ensuring key names match your DB columns)
        'EducationField_Computer Science': 1 if data.get('education_field') == 'Computer Science' else 0,
        'EducationField_Economics': 1 if data.get('education_field') == 'Economics' else 0,
        'EducationField_Human Resources': 1 if data.get('education_field') == 'Human Resources' else 0,
        'EducationField_Information Systems': 1 if data.get('education_field') == 'Information Systems' else 0,
        'EducationField_Marketing': 1 if data.get('education_field') == 'Marketing' else 0,
        'EducationField_Other': 1 if data.get('education_field') == 'Other' else 0,
        'EducationField_Technical Degree': 1 if data.get('education_field') == 'Technical Degree' else 0,
        
        # Job Roles (Mapping 'position' to 'JobRole_...')
        'JobRole_Data Scientist': 1 if data.get('position') == 'Data Scientist' else 0,
        'JobRole_Engineering Manager': 1 if data.get('position') == 'Engineering Manager' else 0,
        'JobRole_HR Business Partner': 1 if data.get('position') == 'HR Business Partner' else 0,
        'JobRole_HR Executive': 1 if data.get('position') == 'HR Executive' else 0,
        'JobRole_HR Manager': 1 if data.get('position') == 'HR Manager' else 0,
        'JobRole_Machine Learning Engineer': 1 if data.get('position') == 'Machine Learning Engineer' else 0,
        'JobRole_Manager': 1 if data.get('position') == 'Manager' else 0,
        'JobRole_Recruiter': 1 if data.get('position') == 'Recruiter' else 0,
        'JobRole_Sales Executive': 1 if data.get('position') == 'Sales Executive' else 0,
        'JobRole_Sales Representative': 1 if data.get('position') == 'Sales Representative' else 0,
        'JobRole_Senior Software Engineer': 1 if data.get('position') == 'Senior Software Engineer' else 0,
        'JobRole_Software Engineer': 1 if data.get('position') == 'Software Engineer' else 0,
        
        # Marital & Overtime
        'MaritalStatus_Married': 1 if data.get('marital_status') == 'Married' else 0,
        'MaritalStatus_Single': 1 if data.get('marital_status') == 'Single' else 0,
        'OverTime_Yes': 1 if data.get('over_time') == 'Yes' else 0,
        
        # Age & Salary Bins
        'AgeGroup_30-39': 1 if 30 <= current_age <= 39 else 0,
        'AgeGroup_40-49': 1 if 40 <= current_age <= 49 else 0,
        'AgeGroup_50+': 1 if current_age >= 50 else 0,
        'SalaryTier_High': 1 if annual_salary > 120000 else 0,
        'SalaryTier_Low': 1 if annual_salary < 60000 else 0,
        'SalaryTier_Medium': 1 if 60000 <= annual_salary <= 120000 else 0
    }

    # 4. Final step: Order and convert to DataFrame
    ordered_cols = [
        'Age', 'DistanceFromHomeKM', 'Education', 'Salary', 'StockOptionLevel',
        'YearsAtCompany', 'YearsInMostRecentRole', 'YearsSinceLastPromotion',
        'YearsWithCurrManager', 'TenureAtReview', 'AvgSatisfaction', 'PerformanceGap',
        'Gender_Male', 'Gender_Non-Binary', 'Gender_Prefer Not To Say',
        'BusinessTravel_No Travel', 'BusinessTravel_Some Travel',
        'Department_Sales', 'Department_Technology', 'State_IL', 'State_NY',
        'Ethnicity_Asian or Asian American', 'Ethnicity_Black or African American',
        'Ethnicity_Mixed or multiple ethnic groups', 'Ethnicity_Native Hawaiian',
        'Ethnicity_Other', 'Ethnicity_White', 'EducationField_Computer Science',
        'EducationField_Economics', 'EducationField_Human Resources',
        'EducationField_Information Systems', 'EducationField_Marketing',
        'EducationField_Other', 'EducationField_Technical Degree',
        'JobRole_Data Scientist', 'JobRole_Engineering Manager',
        'JobRole_HR Business Partner', 'JobRole_HR Executive', 'JobRole_HR Manager',
        'JobRole_Machine Learning Engineer', 'JobRole_Manager', 'JobRole_Recruiter',
        'JobRole_Sales Executive', 'JobRole_Sales Representative',
        'JobRole_Senior Software Engineer', 'JobRole_Software Engineer',
        'MaritalStatus_Married', 'MaritalStatus_Single', 'OverTime_Yes',
        'AgeGroup_30-39', 'AgeGroup_40-49', 'AgeGroup_50+',
        'SalaryTier_High', 'SalaryTier_Low', 'SalaryTier_Medium'
    ]
    
    df = pd.DataFrame([feat])
    return df[ordered_cols]

def calculate_and_store_risk(emp_id, cursor):
    features_df = prepare_ml_features(emp_id, cursor) 
    
    if features_df is not None:
        prediction_proba = attrition_model.predict_proba(features_df)[0][1]
        risk_score = round(float(prediction_proba), 4)
        
        # 3. Determine Risk Level
        if risk_score > 0.7:
            risk_level = "High"
        elif risk_score > 0.4:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        # 4. Generate xAI Reason
        reason = generate_xai_reason(features_df)

        # 5. SAVE TO DATABASE
        current_time = get_malaysia_time()
        insert_sql = """
            INSERT INTO risk_assessments 
            (employee_id, risk_score, risk_level, primary_reason, calculated_at)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_sql, (
            emp_id, 
            risk_score, 
            risk_level, 
            reason,
            current_time
        ))

# xAI Reasoning - Using LIME to explain the prediction and extract top factors
def generate_xai_reason(features_df):
    # 1. Get the single row of data
    instance = features_df.iloc[0]
    
    # 2. Generate LIME explanation
    # Note: ensure 'attrition_model' and 'explainer' are loaded globally in app.py
    exp = explainer.explain_instance(
        data_row=instance.values, 
        predict_fn=attrition_model.predict_proba,
        num_features=10 
    )
    
    raw_output = exp.as_list()
    
    # --- DEBUG SECTION  ---
    print(f"\n--- [DEBUG] XAI Raw Output for Employee ---")
    for feature_condition, weight in raw_output:
        print(f"LIME condition: {feature_condition} | Weight: {weight:.4f}")
    # --------------------------------------------------------------------

    # User-friendly mapping (Keys should be substrings of your column names)
    xai_map = {
        # Performance & Tenure
        'TenureAtReview': "Review Period Tenure: Recent appointment or long-term stagnation in current review cycle.",
        'YearsSinceLastPromotion': "Career Stagnation: Lack of vertical movement over a prolonged period.",
        'YearsAtCompany': "Organizational Tenure: Analysis suggests a shift in long-term company loyalty.",
        'YearsInMostRecentRole': "Role Fatigue: Prolonged duration in the same position without rotation.",
        'YearsWithCurrManager': "Management Relationship: Tenure with current supervisor is a significant risk factor.",
        'PerformanceGap': "Performance Friction: Discrepancy identified between self-eval and manager ratings.",
        'AvgSatisfaction': "Engagement Levels: Average of subjective satisfaction across various work domains.",
        'OverTime': "Burnout Risk: High frequency of overtime affecting work-life balance.",

        #Compensation & Benefits
        'StockOptionLevel': "Equity Gap: Lack of long-term financial incentives or ownership.",
        'Salary': "Financial Competitiveness: Current compensation relative to industry or internal benchmarks.",
        
        #Demographics 
        'Age': "Demographic Factor: Potential alignment with specific career life-cycle stages.",
        'DistanceFromHome': "Commute Stress: Geographical distance impacting daily employee engagement.",
        'MaritalStatus_Single': "Demographic Stability: Single marital status historically correlates with higher mobility.",
        'Department_Sales': "Departmental Pressure: High-stress environment typical of Sales roles."
    }

    final_insights = []

    # 3. Process the LIME output
    for feature_text, weight in raw_output:
        if weight > 0:
            for key, msg in xai_map.items():
                # case-insensitive check to handle naming variations
                if key.lower() in feature_text.lower():
                    
                    # --- CRITICAL FILTERS ---
                    # Don't show Overtime if the value is 0 (No)
                    if 'OverTime' in key and instance.get('OverTime_Yes', 0) == 0:
                        continue

                    if key == 'TenureAtReview' and instance.get('TenureAtReview', 0) < 0.5:
                        continue

                    if msg not in final_insights:
                        final_insights.append(msg)
                    break # Move to next LIME feature once matched

    # 4. Final Output Formatting
    if not final_insights:
        # If model is high risk but we filtered everything, provide a generic insight
        return "Multiple interacting factors: The risk is driven by a combination of minor organizational and tenure-based variables."

    # Return top 3 unique insights separated by line breaks for HTML
    return "<br>".join([m for m in final_insights[:3]])

@app.route('/api/predict-risk/<emp_id>')
def predict_risk(emp_id):
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # Prepare the 55 columns
            features_df = prepare_ml_features(emp_id, cursor)
            
            if features_df is None:
                return jsonify({"success": False, "message": "Employee not found"})

            # Get Prediction Probability
            # [0] is stay, [1] is leave
            risk_proba = attrition_model.predict_proba(features_df)[0][1] 
            
            # Save risk to DB or just return it
            return jsonify({
                "success": True,
                "risk_score": round(risk_proba * 100, 2),
                "risk_level": "High" if risk_proba > 0.7 else "Medium" if risk_proba > 0.3 else "Low"
            })
    finally:
        conn.close()

# =============================
# PAGE ROUTES 
# =============================
@app.route('/')
def home():
    return redirect('/login')

@app.route('/login')
def login_page():
    if 'user_id' in session:
        role = session.get('role', '').lower()
        if role == 'admin':
            return redirect('/admin-dashboard')
        elif role == 'employee':
            return redirect('/employee-dashboard')
    return render_template('authentication/login.html')

@app.route('/forgot-password')
def forgot_password_page():
    return render_template('authentication/forgot_password.html')

@app.route('/otp-verification')
def otp_page():
    return render_template('authentication/otp_verification.html')

@app.route('/reset-password')
def reset_password_page():
    return render_template('authentication/reset_password.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role', '').lower() != 'admin':
        return "Unauthorized", 403

    return render_template('admin/dashboard.html')

@app.route('/employee-dashboard')
def employee_dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role', '').lower() != 'employee':
        return "Unauthorized", 403

    return render_template('employee/emp_dashboard.html')

@app.route('/employee-info')
def employee_info():
    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role', '').lower() != 'employee':
        return "Unauthorized", 403

    return render_template('employee/personal_info.html')

@app.route('/change-password')
def change_password():
    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role', '').lower() != 'employee':
        return "Unauthorized", 403

    return render_template('employee/change_password.html')

@app.route('/employee-management')
def employee_management():
    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role', '').lower() != 'admin':
        return "Unauthorized", 403

    return render_template('admin/emp_management.html')

@app.route('/employee-review')
def employee_review():
    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role', '').lower() != 'admin':
        return "Unauthorized", 403

    return render_template('admin/emp_review.html')

@app.route('/review-history')
def performance_tracking():
    if 'user_id' not in session:
        return redirect('/login')

    if session.get('role', '').lower() != 'admin':
        return "Unauthorized", 403

    return render_template('admin/review_history.html')

# =============================
# AUTHENTICATION APIs
# =============================
# Login API checks email and uses check_password_hash for verification
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
                SELECT u.*, e.employee_id 
                FROM users u 
                LEFT JOIN employees e ON u.employee_id = e.employee_id 
                WHERE u.email = %s
            """
            cursor.execute(sql, (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                session.permanent = True
                session['user_id'] = user['id']
                session['employee_id'] = user['employee_id']
                session['role'] = user['role']
                
                return jsonify({
                    "success": True, 
                    "role": user['role'],
                    "employee_id": user['employee_id']
                })
            else:
                return jsonify({"success": False, "message": "Invalid email or password"}), 401
    finally:
        conn.close()

# Get the logged-in employee's profile using the employee_id from the session
@app.route('/api/employee/profile')
def get_my_profile():
    if 'employee_id' not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # Fetch personal profile + link to email from users table
            sql = """
                SELECT e.*, u.email 
                FROM employees e 
                JOIN users u ON e.employee_id = u.employee_id 
                WHERE e.employee_id = %s
            """
            cursor.execute(sql, (session['employee_id'],))
            profile = cursor.fetchone()
            
            if not profile:
                return jsonify({"success": False, "message": "Profile not found"}), 404
                
            return jsonify({"success": True, "data": profile})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

# Logout API clears the session
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True})

# Check session API to verify if user is logged in and return their role
@app.route('/api/check-session', methods=['GET'])
def check_session():
    if 'user_id' in session:
        return jsonify({"logged_in": True, "role": session.get('role')})
    return jsonify({"logged_in": False})

# =============================
# FORGOT PASSWORD APIs
# =============================
@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.json
        email = data.get('email')

        if not email:
            return jsonify({"success": False, "message": "Email required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT id FROM users WHERE Email=%s", (email,))
        user = cursor.fetchone()

        if not user:
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "User not found"}), 404

        otp = ''.join(random.choices(string.digits, k=6))
        now = datetime.now() 
        expiry_time = now + timedelta(minutes=10)

        cursor.execute(
            "UPDATE users SET OTP=%s, OTPExpiry=%s WHERE Email=%s",
            (otp, expiry_time, email)
        )

        conn.commit()
        cursor.close()
        conn.close()

        msg = MIMEText(f"Your Worklytics OTP code is: {otp}\nValid for 10 minutes.")
        msg['Subject'] = "Worklytics Password Reset OTP"
        msg['From'] = "chipfish64@gmail.com"
        msg['To'] = email

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login("chipfish64@gmail.com", "uwld owak scig tzfc")
            server.send_message(msg)

        return jsonify({"success": True})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.json
        email = data.get('email')
        otp_input = data.get('otp')

        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT OTP, OTPExpiry FROM users WHERE Email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            return jsonify({"success": False}), 404

        if not user['OTP'] or datetime.now() > user['OTPExpiry']:
            return jsonify({"success": False, "message": "OTP expired"}), 400

        if str(otp_input) == str(user['OTP']):
            return jsonify({"success": True})

        return jsonify({"success": False, "message": "Invalid OTP"}), 400

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.json
        email = data.get('email')
        new_password = data.get('new_password')

        if not email or not new_password:
            return jsonify({"success": False, "message": "Missing email or password"}), 400

        # Hash the password before saving to the database
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # Store the hashed version, not the plain text
                sql = "UPDATE users SET password=%s, otp=NULL, otpexpiry=NULL WHERE email=%s"
                cursor.execute(sql, (hashed_password, email))
            conn.commit()
        finally:
            conn.close()

        return jsonify({"success": True, "message": "Password reset successfully!"})

    except Exception as e:
        print(f"Reset Password Error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# =============================
# EMPLOYEE MANAGEMENT APIs
# =============================
# 1. Standard Employee ID (E-XXX)
@app.route('/api/get-next-employee-id', methods=['GET'])
def get_next_id():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT MAX(CAST(SUBSTRING(employee_id, 3) AS UNSIGNED)) FROM employees"
            cursor.execute(sql)
            result = cursor.fetchone()
            max_id = result[0] if result[0] is not None else 100
            return jsonify({"success": True, "next_id": f"E-{max_id + 1}"})
    finally:
        conn.close()

# Fetch managers filtered by department
@app.route('/api/get-managers-by-dept', methods=['GET'])
def get_managers_by_dept():
    dept = request.args.get('department')
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # We look for people in the SAME department who hold Manager roles
            sql = """
                SELECT e.employee_id, e.employee_name 
                FROM employees e
                JOIN job_details j ON e.employee_id = j.employee_id
                WHERE j.department = %s 
                AND j.position IN ('Engineering Manager', 'Analytics Manager', 'Manager', 'HR Manager')
            """
            cursor.execute(sql, (dept,))
            return jsonify({"success": True, "managers": cursor.fetchall()})
    finally:
        conn.close()

@app.route('/api/add-employee', methods=['POST'])
def add_employee():
    data = request.json
    today_kl = get_malaysia_time().date() 
    today_str = today_kl.strftime('%Y-%m-%d')
    
    default_password = 'Worklytics123!'
    hashed_password = generate_password_hash(default_password, method='pbkdf2:sha256')

    # Manager Logic
    manager_id = data.get('manager_id')
    if not manager_id or manager_id == "" or str(manager_id).lower() == 'none':
        manager_id = None
        manager_date = None
    else:
        manager_date = today_str 

    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 1. Table: users
            cursor.execute("""
                INSERT INTO users (email, password, role, employee_id) 
                VALUES (%s, %s, %s, %s)
            """, (data['email'], hashed_password, 'employee', data['emp_id']))

            # 2. Table: employees
            cursor.execute("""
                INSERT INTO employees (
                    employee_id, employee_name, dob, gender, marital_status, 
                    ethnicity, state, education, education_field, hire_date
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['emp_id'], data['full_name'], data['dob'], data['gender'], 
                data['marital_status'], data['ethnicity'], data['state'], 
                data['education'], data['education_field'], today_str
            ))

            # 3. Table: job_details
            cursor.execute("""
                INSERT INTO job_details (
                    employee_id, department, position, salary, distance_from_home_km, 
                    business_travel, over_time, stock_option_level, 
                    role_start_date, manager_id, manager_assign_date
                ) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['emp_id'], data['department'], data['position'], 
                data['salary'], data['distance_km'], data['business_travel'], 
                data['over_time'], data.get('stock_option_level', 0),
                today_str, manager_id, manager_date
            ))
            # calculate_and_store_risk(data['emp_id'], cursor)
        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        conn.rollback()
        print(f"Add Employee Error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/get-employees', methods=['GET'])
def get_employees():
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # This query gets the latest risk assessment for each employee
            sql = """
                SELECT 
                e.employee_id, e.employee_name, 
                MAX(r.review_date) AS latest_review_date,
                j.department, j.position, 
                ra.risk_score, ra.risk_level
            FROM employees e
            JOIN job_details j ON e.employee_id = j.employee_id
            LEFT JOIN performance_reviews r ON e.employee_id = r.employee_id
            LEFT JOIN (
                SELECT employee_id, risk_score, risk_level
                FROM risk_assessments
                WHERE (employee_id, calculated_at) IN (
                    SELECT employee_id, MAX(calculated_at)
                    FROM risk_assessments
                    GROUP BY employee_id
                )
            ) ra ON e.employee_id = ra.employee_id
            GROUP BY 
                e.employee_id, e.employee_name, 
                j.department, j.position, 
                ra.risk_score, ra.risk_level;
            """
            cursor.execute(sql)
            employees = cursor.fetchall()
            return jsonify({"success": True, "data": employees})
    finally:
        conn.close()

@app.route('/api/delete-employee/<emp_id>', methods=['DELETE'])
def delete_employee(emp_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 1. Check if this person is a manager for anyone else
            # Note: We now check job_details because manager_id moved there
            cursor.execute("SELECT COUNT(*) FROM job_details WHERE manager_id = %s", (emp_id,))
            result = cursor.fetchone()
            subordinate_count = result[0] if result else 0

            # 2. If they have a team, deny the deletion to prevent orphaned reporting lines
            if subordinate_count > 0:
                return jsonify({
                    "success": False, 
                    "message": f"Cannot delete. This person is currently managing {subordinate_count} employee(s). Please reassign their team in the system first."
                }), 400

            # 3. Execution of Deletion
            cursor.execute("DELETE FROM users WHERE employee_id = %s", (emp_id,))

        conn.commit()
        return jsonify({"success": True, "message": "Employee and all associated records deleted successfully!"})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()
    
@app.route('/api/get-employee/<emp_id>', methods=['GET'])
def get_employee_details(emp_id):
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            sql = """
                SELECT 
                    e.*, 
                    u.email, 
                    j.department, 
                    j.position, 
                    j.salary, 
                    j.distance_from_home_km, 
                    j.business_travel, 
                    j.over_time, 
                    j.stock_option_level,
                    j.manager_id, 
                    j.role_start_date, 
                    j.last_promotion_date,
                    j.manager_assign_date
                FROM employees e
                JOIN job_details j ON e.employee_id = j.employee_id
                JOIN users u ON e.employee_id = u.employee_id
                WHERE e.employee_id = %s
            """
            cursor.execute(sql, (emp_id,))
            employee = cursor.fetchone()

            if not employee:
                return jsonify({"success": False, "message": "Employee not found"}), 404

            for key, value in employee.items():
                if isinstance(value, (date, datetime)):
                    employee[key] = value.strftime('%Y-%m-%d')
            
            return jsonify({"success": True, "data": employee})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/update-employee', methods=['POST'])
def update_employee():
    data = request.json
    emp_id = data['emp_id']
    today_str = get_malaysia_time().date().strftime('%Y-%m-%d')
    
    # Clean Manager ID
    new_mgr_id = data.get('manager_id')
    if not new_mgr_id or str(new_mgr_id).lower() in ['', 'none', 'null']:
        new_mgr_id = None

    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 1. Get current dates to preserve them if no change occurs
            cursor.execute("SELECT position, manager_id, role_start_date, last_promotion_date, manager_assign_date FROM job_details WHERE employee_id = %s", (emp_id,))
            current = cursor.fetchone()

            # 2. Update EMPLOYEES Table
            cursor.execute("""
                UPDATE employees SET 
                employee_name=%s, dob=%s, gender=%s, marital_status=%s, 
                ethnicity=%s, state=%s, education=%s, education_field=%s
                WHERE employee_id=%s
            """, (data['full_name'], data.get('dob'), data['gender'], data['marital_status'], 
                  data['ethnicity'], data['state'], data['education'], data['education_field'], emp_id))

            # 3. Handle Date Logic (Calculated in Python, passed as safe params)
            role_d, promo_d, mgr_d = current['role_start_date'], current['last_promotion_date'], current['manager_assign_date']
            
            if current['position'] != data['position']:
                role_d = today_str
                if data['position'] in ["Engineering Manager", "Analytics Manager", "Manager", "HR Manager"]:
                    promo_d = today_str
            if str(current['manager_id']) != str(new_mgr_id):
                mgr_d = today_str if new_mgr_id else None

            # 4. Update JOB_DETAILS (FIX FOR ERROR 1241)
            cursor.execute("""
                UPDATE job_details SET 
                department=%s, position=%s, salary=%s, distance_from_home_km=%s, 
                business_travel=%s, over_time=%s, stock_option_level=%s,
                manager_id=%s, role_start_date=%s, last_promotion_date=%s, manager_assign_date=%s
                WHERE employee_id=%s
            """, (data['department'], data['position'], data['salary'], data['distance_km'], 
                  data['business_travel'], data['over_time'], data.get('stock_option_level', 0), 
                  new_mgr_id, role_d, promo_d, mgr_d, emp_id))

            cursor.execute("UPDATE users SET email=%s WHERE employee_id=%s", (data['email'], emp_id))
            calculate_and_store_risk(emp_id, cursor)

        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        conn.rollback()
        print(f"Update Error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

# =============================
# REVIEW EMPLOYEES APIs
# =============================
@app.route('/api/update-performance', methods=['POST'])
def update_performance():
    data = request.json
    today_kl = get_malaysia_time().date() 
    today = today_kl.strftime('%Y-%m-%d')
    emp_id = data['employee_id']
    
    conn = pymysql.connect(**db_config, cursorclass=pymysql.cursors.DictCursor)
    try:
        with conn.cursor() as cursor:
            # 1. Save the Review
            sql = """
                INSERT INTO performance_reviews (
                    employee_id, review_date, env_satisfaction, 
                    job_satisfaction, rel_satisfaction, self_rating, 
                    manager_rating, target_kpi, actual_kpi
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                emp_id, today, data['env_satisfaction'],
                data['job_satisfaction'], data['rel_satisfaction'],
                data['self_rating'], data['manager_rating'],
                data['target_kpi'], data['actual_kpi']
            ))
            
            # 2. TRIGGER THE ML MODEL (The Bridge)
            # We call the function we designed earlier to calculate risk immediately
            calculate_and_store_risk(emp_id, cursor)

        conn.commit()
        return jsonify({"success": True})
    except Exception as e:
        conn.rollback()
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

# =============================
# REVIEW HISTORY API
# =============================
@app.route('/api/all-risk-history', methods=['GET'])
def get_all_risk_history():
    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # We JOIN with employees to get the name for the history table
            sql = """
                SELECT ra.*, e.employee_name 
                FROM risk_assessments ra
                JOIN employees e ON ra.employee_id = e.employee_id
                ORDER BY ra.calculated_at DESC
            """
            cursor.execute(sql)
            history = cursor.fetchall()
            for row in history:
                if row.get('calculated_at'):
                    row['calculated_at'] = row['calculated_at'].strftime('%d %b %Y, %H:%M')
                    
            return jsonify({"success": True, "data": history})
    finally:
        conn.close()

# =============================
# Employee Dashboard
# =============================
@app.route('/api/get-my-data', methods=['GET'])
def get_my_data():
    emp_id = session.get('employee_id')
    if not emp_id:
        return jsonify({"success": False, "message": "No session found"}), 401

    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # 1. Profile Info
            cursor.execute("""
                SELECT e.employee_name, j.position, j.department, e.hire_date, u.email
                FROM employees e 
                JOIN job_details j ON e.employee_id = j.employee_id
                JOIN users u ON e.employee_id = u.employee_id
                WHERE e.employee_id = %s
            """, (emp_id,))
            profile = cursor.fetchone()

            # 2. Latest Performance Review
            cursor.execute("""
                SELECT * FROM performance_reviews 
                WHERE employee_id = %s 
                ORDER BY review_date DESC LIMIT 1
            """, (emp_id,))
            review = cursor.fetchone()

            if not profile:
                return jsonify({"success": False, "message": "Profile not found"}), 404

            # --- GENERATE PLOTLY CHARTS IN PYTHON ---
            charts = {}
            if review:
                # A. Radar Chart for Satisfactions
                categories = ['Environment', 'Job Role', 'Relationships', 'Environment']
                values = [
                    review['env_satisfaction'], 
                    review['job_satisfaction'], 
                    review['rel_satisfaction'],
                    review['env_satisfaction'] 
                ]
                
                fig_radar = go.Figure(data=go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    line=dict(color='#4e73df')
                ))
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
                    showlegend=False,
                    autosize=True,
                    margin=dict(l=30, r=30, t=50, b=30),
                    height=350
                )
                charts['satisfaction_radar'] = json.loads(pio.to_json(fig_radar))

                # B. Bar Chart for Ratings Comparison
                fig_bar = go.Figure(data=[
                    go.Bar(name='Self', x=['Self Rating'], y=[review['self_rating']], marker_color='#6c757d'),
                    go.Bar(name='Manager', x=['Manager Rating'], y=[review['manager_rating']], marker_color='#4e73df')
                ])
                fig_bar.update_layout(
                    yaxis=dict(range=[0, 5]),
                    autosize=True,
                    margin=dict(l=30, r=30, t=30, b=50),
                    height=350,
                    showlegend=False
                )
                charts['rating_bar'] = json.loads(pio.to_json(fig_bar))

            # Format dates
            if profile['hire_date']:
                profile['hire_date'] = profile['hire_date'].strftime('%Y-%m-%d')
            if review and review['review_date']:
                review['review_date'] = review['review_date'].strftime('%Y-%m-%d')

            return jsonify({
                "success": True,
                "data": profile,
                "review": review,
                "charts": charts
            })
    finally:
        conn.close()

@app.route('/api/get-full-profile', methods=['GET'])
def get_full_profile():
    emp_id = session.get('employee_id')
    if not emp_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # Joining employees and job_details to get every field
            sql = """
                SELECT e.*, j.* FROM employees e
                JOIN job_details j ON e.employee_id = j.employee_id
                WHERE e.employee_id = %s
            """
            cursor.execute(sql, (emp_id,))
            full_data = cursor.fetchone()

            if not full_data:
                return jsonify({"success": False, "message": "Data not found"}), 404

            # Format all date objects for JSON
            date_fields = ['dob', 'hire_date', 'role_start_date', 
                           'last_promotion_date', 'manager_assign_date']
            for field in date_fields:
                if full_data.get(field):
                    full_data[field] = full_data[field].strftime('%d %b %Y')

            return jsonify({"success": True, "data": full_data})
    finally:
        conn.close()
          
@app.route('/api/change-password', methods=['POST'])
def api_change_password():
    emp_id = session.get('employee_id')
    data = request.json
    
    curr_pwd = data.get('current_password')
    new_pwd = data.get('new_password')
    conf_pwd = data.get('confirm_password')

    if new_pwd != conf_pwd:
        return jsonify({"success": False, "message": "Passwords do not match."})

    conn = get_db_connection()
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # Get current hashed password from users table
            cursor.execute("SELECT password FROM users WHERE employee_id = %s", (emp_id,))
            user = cursor.fetchone()

            if not user or not check_password_hash(user['password'], curr_pwd):
                return jsonify({"success": False, "message": "Incorrect current password."})

            # Hash and Update
            hashed_pwd = generate_password_hash(new_pwd)
            cursor.execute("UPDATE users SET password = %s WHERE employee_id = %s", (hashed_pwd, emp_id))
            conn.commit()
            
            return jsonify({"success": True, "message": "Password updated successfully!"})
    finally:
        conn.close()

# =============================
# Notification APIs
# =============================
@app.route('/api/risk-stats')
def get_risk_stats():
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            # SQL query to count high risk employees from your table
            sql = """
                SELECT COUNT(*) as high_risk_count 
                FROM risk_assessments r1
                WHERE r1.assessment_id = (
                    SELECT MAX(assessment_id) 
                    FROM risk_assessments r2 
                    WHERE r2.employee_id = r1.employee_id
                ) AND r1.risk_level = 'High'
            """
            cursor.execute(sql)
            result = cursor.fetchone()
            
            return jsonify({
                'high_risk_count': result['high_risk_count'] if result else 0
            })
    except Exception as e:
        print(f"Error fetching risk stats: {e}")
        return jsonify({'high_risk_count': 0})
    finally:
        if conn:
            conn.close()

# =============================
# RUN APP
# =============================
if __name__ == '__main__':
    app.run(debug=True)
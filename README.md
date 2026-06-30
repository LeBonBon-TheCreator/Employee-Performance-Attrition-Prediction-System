# Worklytics: Machine Learning–Driven HR Decision Support System

## 📝 Project Overview

**Worklytics** is an end-to-end predictive analytics and decision-support platform designed to help HR managers evaluate employee performance and proactively mitigate attrition. By bridging the gap between raw workforce data and actionable policy, Worklytics transforms traditional HR management into a data-driven science.

Following the industry-standard **CRISP-DM** methodology, this system integrates machine learning, explainable AI (xAI), and interactive data visualization to provide deep insights into human capital management.

---

## 🚀 Key Features

* **Predictive Attrition Modeling:** Employs a `Random Forest Classifier` to accurately forecast employee attrition risk based on KPIs, satisfaction metrics, and tenure data.
* **Explainable AI (xAI) Integration:** Utilizes the **LIME** framework to deconstruct "black-box" model outputs, providing transparent, feature-level reasoning for every risk score.
* **Proactive Alerting Engine:** Features a synchronized audio-visual notification module that flags high-priority risks instantly without causing alert fatigue.
* **Interactive Dashboards:** Leverages **Power BI** to present complex data relationships through an executive-ready visual interface.
* **Optimized Backend Architecture:** Built on a robust `Flask` and `MySQL` foundation, utilizing advanced SQL subqueries to prevent data redundancy and ensure real-time accuracy.

---

## 🛠️ Technical Stack

### **Data Science & Modeling**

* **Python** (Pandas, NumPy, Scikit-Learn)
* **LIME** (Local Interpretable Model-agnostic Explanations)
* **Random Forest Classifier**

### **Web & Database**

* **Flask** (Python Web Framework)
* **MySQL** (Database Management)
* **HTML/CSS/JavaScript** (Frontend Dashboard)

### **Analytics & Visualization**

* **Power BI** (Data Modeling, DAX, Interactive Reporting)

---

## 📂 Project Structure

```text
worklytics/
├── app.py              # Main Flask application logic
├── models/             # Pre-trained Random Forest model & LIME explainer
├── static/             # CSS, JavaScript, and audio assets
├── templates/          # HTML files for the web interface
├── data/               # Data cleaning scripts and datasets
└── README.md           # Project documentation

```

---

## 💡 Key Learnings & Challenges

* **The Explainability Barrier:** Overcame the "black box" nature of machine learning by mapping model weights to human-understandable insights via LIME.
* **Browser Security Constraints:** Navigated modern browser autoplay restrictions by engineering a "User-Interacted Audio Trigger" for critical alerts.
* **Tool Mastery:** Successfully self-taught Power BI and DAX under project timelines, transitioning from flat-file analysis to professional Star Schema data modeling.

---

## 👤 About the Author

Developed by a **Business Analytics** student at **INTI International University**. Passionate about the intersection of human resource management, machine learning, and transparent, ethical AI deployment.

---

## 🤝 Acknowledgements

* **Ms. Sarasvathi A/P Nagalingham** – Project Supervisor, for invaluable technical guidance and mentorship throughout the development lifecycle.

---

## 📊 Status

* **Project State:** Completed (Final Year Project)
* **Methodology:** CRISP-DM

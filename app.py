from flask import Flask, render_template, request, redirect, url_for
from disease_recommendation import get_recommendation
import sqlite3
from datetime import datetime
import pandas as pd
import joblib
import json
import os


app = Flask(__name__)

# ==========================================
# Create Database
# ==========================================

def create_database():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients(

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        age INTEGER,
        gender INTEGER,
        disease TEXT,
        date TEXT

    )
    """)

    conn.commit()
    conn.close()

create_database()

# ==========================================
# Load Machine Learning Model
# ==========================================

model = joblib.load("models/random_forest_model.pkl")
label_encoder = joblib.load("models/disease_label_encoder.pkl")

# ==========================================
# Dashboard
# ==========================================

@app.route("/")
def dashboard():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    # Total Patients
    cursor.execute("SELECT COUNT(*) FROM patients")
    total = cursor.fetchone()[0]

    # Most Common Disease
    cursor.execute("""
        SELECT disease, COUNT(*)
        FROM patients
        GROUP BY disease
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """)

    result = cursor.fetchone()

    if result:
        disease = result[0]
    else:
        disease = "No Data"

    # Recent Patients
    cursor.execute("""
        SELECT *
        FROM patients
        ORDER BY id DESC
        LIMIT 10
    """)

    patients = cursor.fetchall()

    # Disease Chart Data
    cursor.execute("""
        SELECT disease, COUNT(*)
        FROM patients
        GROUP BY disease
    """)

    chart = cursor.fetchall()

    disease_names = [row[0] for row in chart]
    disease_counts = [row[1] for row in chart]

    print("Disease Names :", disease_names)
    print("Disease Counts:", disease_counts)

    conn.close()

    return render_template(

        "dashboard.html",

        total=total,

        disease=disease,

        patients=patients,

        disease_names=json.dumps(disease_names),

        disease_counts=json.dumps(disease_counts)

    )

# ==========================================
# Prediction Page
# ==========================================

@app.route("/predict-page")
def prediction_page():

    return render_template("index.html")

# ==========================================
# Disease Prediction
# ==========================================

@app.route("/predict", methods=["POST"])
def predict():

    # Patient Details
    name = request.form["name"]
    email = request.form["email"]

    fever = int(request.form["fever"])
    cough = int(request.form["cough"])
    fatigue = int(request.form["fatigue"])
    difficulty_breathing = int(request.form["difficulty_breathing"])
    age = int(request.form["age"])
    gender = int(request.form["gender"])
    blood_pressure = int(request.form["blood_pressure"])
    cholesterol_level = int(request.form["cholesterol_level"])

    # Feature Scaling
    age_scaled = age / 100
    bp_scaled = blood_pressure / 200
    chol_scaled = cholesterol_level / 300
    risk_level = 1

    patient = pd.DataFrame([{

        "fever": fever,
        "cough": cough,
        "fatigue": fatigue,
        "difficulty_breathing": difficulty_breathing,
        "age": age,
        "gender": gender,
        "blood_pressure": blood_pressure,
        "cholesterol_level": cholesterol_level,
        "age_scaled": age_scaled,
        "bp_scaled": bp_scaled,
        "chol_scaled": chol_scaled,
        "risk_level": risk_level

    }])

    # Prediction
    prediction = model.predict(patient)
    disease = label_encoder.inverse_transform(prediction)[0]

    print("Predicted Disease :", disease)

    # Save Patient Record
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""

        INSERT INTO patients
        (
            name,
            email,
            age,
            gender,
            disease,
            date
        )

        VALUES
        (
            ?,?,?,?,?,?
        )

    """,

    (

        name,
        email,
        age,
        gender,
        disease,
        datetime.now().strftime("%d-%m-%Y %H:%M")

    ))

    conn.commit()
    conn.close()

    # Recommendation
    result = get_recommendation(disease)

    return render_template(

        "result.html",

        disease=disease,
        medicine=result["Medicine"],
        diet=result["Diet"],
        exercise=result["Exercise"],
        water=result["Water"],
        precautions=result["Precautions"]

    )


# ==========================================
# Patient History
# ==========================================

@app.route("/history")
def history():

    search = request.args.get("search")

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if search:

        cursor.execute("""

            SELECT *
            FROM patients

            WHERE

            name LIKE ?
            OR disease LIKE ?

            ORDER BY id DESC

        """,

        (

            "%" + search + "%",
            "%" + search + "%"

        ))

    else:

        cursor.execute("""

            SELECT *
            FROM patients
            ORDER BY id DESC

        """)

    patients = cursor.fetchall()

    conn.close()

    return render_template(

        "history.html",

        patients=patients,

        search=search

    )

if __name__ == "__main__":
    import os
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )
    
# ==========================================
# Delete Patient
# ==========================================

@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(

        "DELETE FROM patients WHERE id=?",

        (id,)

    )

    conn.commit()
    conn.close()

    return redirect(url_for("history"))


# ==========================================
# Export Patient History
# ==========================================

@app.route("/export")
def export():

    conn = sqlite3.connect("database.db")

    df = pd.read_sql_query(

        "SELECT * FROM patients",

        conn

    )

    conn.close()

    df.to_csv(

        "static/patient_history.csv",

        index=False

    )

    return redirect("/static/patient_history.csv")


# ==========================================
# About Page
# ==========================================

@app.route("/about")
def about():

    return render_template("about.html")


# ==========================================
# Contact Page
# ==========================================

@app.route("/contact")
def contact():

    return render_template("contact.html")


# ==========================================
# 404 Error
# ==========================================

@app.errorhandler(404)
def page_not_found(error):

    return "<h2>404 - Page Not Found</h2>", 404


# ==========================================
# Run Application
# ==========================================

if __name__ == "__main__":

    app.run(

        debug=True,

        host="0.0.0.0",

        port=5000

    )
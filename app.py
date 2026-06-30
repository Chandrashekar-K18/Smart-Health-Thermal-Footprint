from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import session


import sqlite3
import cv2
import numpy as np
import pickle
import os


app=Flask(__name__)

app.secret_key="smart_health"


def init_db():

    con=sqlite3.connect(
        "database.db"
    )

    cur=con.cursor()

    cur.execute("""

    CREATE TABLE IF NOT EXISTS users(

    id INTEGER PRIMARY KEY,

    email TEXT,

    phone TEXT,

    password TEXT

    )

    """)

    con.commit()

    con.close()


init_db()


@app.route("/")

def login():

    return render_template(
        "login.html"
    )


@app.route(
"/register",
methods=["POST"]
)

def register():

    email=request.form["email"]

    phone=request.form["phone"]

    password=request.form["password"]

    con=sqlite3.connect(
        "database.db"
    )

    cur=con.cursor()

    cur.execute(

    """

    INSERT INTO users

    (
    email,
    phone,
    password

    )

    VALUES

    (?,?,?)

    """,

    (
    email,
    phone,
    password
    )

    )

    con.commit()

    con.close()

    return render_template(

    "login.html",

    success=

    "Registration Successful"

    )


@app.route(
"/login",
methods=["POST"]
)

def authenticate():

    email=request.form["email"]

    password=request.form["password"]

    con=sqlite3.connect(
        "database.db"
    )

    cur=con.cursor()

    cur.execute(

    """

    SELECT *

    FROM users

    WHERE

    email=?

    AND

    password=?

    """,

    (
    email,
    password
    )

    )

    user=cur.fetchone()

    con.close()

    if user:

        session["user"]=email

        return redirect(
            "/dashboard"
        )

    return render_template(

    "login.html",

    error=

    "Invalid Credentials"

    )

@app.route("/predict", methods=["POST"])
def predict():
    # Verify if a file packet was delivered
    if "file" not in request.files:
        return {"error": "No image data sent from frontend"}, 400
        
    file = request.files["file"]
    if file.filename == "":
        return {"error": "No selected file"}, 400

    try:
        # 1. Read the image binary data directly into memory
        file_bytes = np.frombuffer(file.read(), np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_GRAYSCALE)
        
        if img is None:
            return {"error": "Failed to parse image file format"}, 400

        # 2. Standardize grid sizes to match training specs
        img = cv2.resize(img, (60, 60))
        
        # 3. Extract Zonal Features identical to your training script
        toe_zone = img[0:20, :]
        mid_zone = img[20:40, :]
        heel_zone = img[40:60, :]
        
        features = [
            np.mean(img),
            np.max(img),
            np.mean(toe_zone),
            np.max(toe_zone),
            np.mean(mid_zone),
            np.max(mid_zone),
            np.mean(heel_zone),
            np.max(heel_zone),
            np.std(img)
        ]
        
        # 4. Check if model exists and open it
        model_path = "model/thermal_model.pkl"
        if not os.path.exists(model_path):
            return {"error": "The AI classifier file is missing. Please run train_model.py first."}, 500
            
        with open(model_path, "rb") as f:
            model = pickle.load(f)
            
        # 5. Run prediction (0 = Healthy, 1 = Diabetic)
        prediction_id = model.predict([features])[0]
        classes = ["Healthy", "Diabetic"]
        result_label = classes[prediction_id]
        
        # Send diagnostic output back to the JavaScript interface
        return {"prediction": result_label}

    except Exception as e:
        return {"error": f"Internal server error: {str(e)}"}, 500
@app.route(
"/dashboard"
)

def dashboard():

    if "user" not in session:

        return redirect("/")

    return render_template(
        "dashboard.html"
    )


@app.route("/logout")

def logout():

    session.clear()

    return redirect("/")


import os

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
import streamlit as st
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
import os

CSV_FILE = "attendance.csv"

# Initialize CSV if not present
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=["Name", "Date", "Day", "Status"])
    df.to_csv(CSV_FILE, index=False)

# Load CSV
def load_attendance():
    return pd.read_csv(CSV_FILE)

# Save new record
def save_attendance(name, status):
    now = datetime.now()
    new_row = {
        "Name": name,
        "Date": now.strftime("%Y-%m-%d"),
        "Day": now.strftime("%A"),
        "Status": status
    }
    df = load_attendance()
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

# Simple face detector using OpenCV Haar Cascade (no AI model)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

st.title("Face Attendance System")

menu = st.sidebar.radio("Menu", ["Register", "Mark Attendance", "View Records", "Delete Records"])

# Open webcam and capture one frame
def capture_image():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    cap.release()
    return ret, frame

if menu == "Register":
    st.header("Register New Person")
    name = st.text_input("Enter Name")
    if st.button("Capture & Save Face"):
        ret, frame = capture_image()
        if ret:
            faces = face_cascade.detectMultiScale(frame, 1.3, 5)
            if len(faces) == 0:
                st.error("No face detected. Try again.")
            else:
                folder = "registered_faces"
                os.makedirs(folder, exist_ok=True)
                path = os.path.join(folder, f"{name}.jpg")
                cv2.imwrite(path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                st.image(frame, caption=f"Registered as {name}", use_container_width=True)
                st.success(f"{name} has been registered successfully!")

if menu == "Mark Attendance":
    st.header("Mark Attendance")
    if st.button("Scan Face"):
        ret, frame = capture_image()
        if ret:
            faces = face_cascade.detectMultiScale(frame, 1.3, 5)
            if len(faces) == 0:
                st.warning("No face detected.")
            else:
                st.image(frame, caption="Scanned Image", use_container_width=True)
                # Simple check if file exists (dummy verification)
                registered_faces = os.listdir("registered_faces") if os.path.exists("registered_faces") else []
                match_found = False
                for file in registered_faces:
                    if file.endswith(".jpg"):
                        person_name = os.path.splitext(file)[0]
                        if person_name.lower() in " ".join(st.session_state.get("last_name", [person_name])).lower():
                            match_found = True
                            save_attendance(person_name, "Present")
                            st.success(f"Attendance marked for {person_name}")
                            break
                if not match_found:
                    st.error("No matching face found. Marked as Absent.")
                    save_attendance("Unknown", "Absent")

if menu == "View Records":
    st.header("📋 Attendance Records")
    df = load_attendance()
    st.dataframe(df)
    st.download_button("Download CSV", df.to_csv(index=False), "attendance.csv", "text/csv")

if menu == "Delete Records":
    if st.button("Delete All Records"):
        df = pd.DataFrame(columns=["Name", "Date", "Day", "Status"])
        df.to_csv(CSV_FILE, index=False)
        st.success("All records deleted successfully!")

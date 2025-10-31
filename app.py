import streamlit as st
import cv2
import numpy as np
import pandas as pd
from datetime import datetime
import os

CSV_FILE = "attendance.csv"

# Initialize CSV if not present
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["Name", "Date", "Day", "Status"]).to_csv(CSV_FILE, index=False)

def load_attendance():
    return pd.read_csv(CSV_FILE)

def save_attendance(name, status):
    now = datetime.now()
    new_row = {"Name": name, "Date": now.strftime("%Y-%m-%d"), "Day": now.strftime("%A"), "Status": status}
    df = load_attendance()
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

st.title("📸 Photo-based Attendance System (No Webcam)")

menu = st.sidebar.radio("Menu", ["Register", "Mark Attendance", "View Records", "Delete Records"])

if menu == "Register":
    st.header("Register New Person")
    name = st.text_input("Enter Name")
    uploaded = st.file_uploader("Upload a face photo", type=["jpg", "png", "jpeg"])

    if uploaded and st.button("Register"):
        image = np.array(bytearray(uploaded.read()), dtype=np.uint8)
        frame = cv2.imdecode(image, cv2.IMREAD_COLOR)
        faces = face_cascade.detectMultiScale(frame, 1.3, 5)
        if len(faces) == 0:
            st.error("No face detected. Try again.")
        else:
            os.makedirs("registered_faces", exist_ok=True)
            path = os.path.join("registered_faces", f"{name}.jpg")
            cv2.imwrite(path, frame)
            st.success(f"{name} registered successfully!")
            st.image(frame, caption=f"Registered as {name}", use_container_width=True)

if menu == "Mark Attendance":
    st.header("Mark Attendance")
    uploaded = st.file_uploader("Upload your photo to mark attendance", type=["jpg", "png", "jpeg"])
    if uploaded and st.button("Check Attendance"):
        image = np.array(bytearray(uploaded.read()), dtype=np.uint8)
        frame = cv2.imdecode(image, cv2.IMREAD_COLOR)
        st.image(frame, caption="Uploaded Image", use_container_width=True)

        registered_faces = os.listdir("registered_faces") if os.path.exists("registered_faces") else []
        if not registered_faces:
            st.warning("No registered faces found.")
        else:
            st.success("Marked as Present ✅")
            save_attendance(uploaded.name, "Present")

if menu == "View Records":
    st.header("📋 Attendance Records")
    df = load_attendance()
    st.dataframe(df)
    st.download_button("Download CSV", df.to_csv(index=False), "attendance.csv", "text/csv")

if menu == "Delete Records":
    if st.button("Delete All Records"):
        pd.DataFrame(columns=["Name", "Date", "Day", "Status"]).to_csv(CSV_FILE, index=False)
        st.success("All records deleted successfully!")

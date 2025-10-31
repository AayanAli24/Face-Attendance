import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image

# Paths
CSV_FILE = "attendance.csv"
REGISTER_DIR = "registered_faces"

# Setup
os.makedirs(REGISTER_DIR, exist_ok=True)
if not os.path.exists(CSV_FILE):
    pd.DataFrame(columns=["Name", "Date", "Day", "Status"]).to_csv(CSV_FILE, index=False)


# ---------------- Helper Functions ----------------
def load_attendance():
    return pd.read_csv(CSV_FILE)

def save_attendance(name, status):
    now = datetime.now()
    new_row = {
        "Name": name,
        "Date": now.strftime("%Y-%m-%d"),
        "Day": now.strftime("%A"),
        "Status": status,
    }
    df = load_attendance()
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)


# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="📸 Simple Attendance System", layout="wide")
st.title("📸 Simple Attendance System (No Face Recognition)")

menu = st.sidebar.radio("Navigation", ["Register", "Mark Attendance", "View Records", "Delete Records"])

# ---------------- Register ----------------
if menu == "Register":
    st.header("🧍 Register a New Person")
    name = st.text_input("Enter your name:")
    img_file = st.camera_input("Capture your photo")

    if img_file and name:
        img = Image.open(img_file)
        save_path = os.path.join(REGISTER_DIR, f"{name}.jpg")
        img.save(save_path)
        st.success(f"{name} registered successfully!")
        st.image(img, caption=f"Registered Image for {name}", use_container_width=True)


# ---------------- Mark Attendance ----------------
elif menu == "Mark Attendance":
    st.header("✅ Mark Attendance")

    registered_faces = [f for f in os.listdir(REGISTER_DIR) if f.endswith(".jpg")]

    if not registered_faces:
        st.warning("⚠️ No registered people found. Please register first.")
    else:
        selected_name = st.selectbox("Select your name:", [os.path.splitext(f)[0] for f in registered_faces])
        img_file = st.camera_input("Capture your photo to mark attendance")

        if img_file:
            captured_img = Image.open(img_file)
            st.image(captured_img, caption="Captured Image", use_container_width=True)

            # Here you could compare images manually if needed
            if selected_name + ".jpg" in registered_faces:
                save_attendance(selected_name, "Present")
                st.success(f"✅ Attendance marked for {selected_name}")
            else:
                st.error("🚫 Name not recognized. Please register first.")


# ---------------- View Records ----------------
elif menu == "View Records":
    st.header("📋 Attendance Records")
    df = load_attendance()
    st.dataframe(df, use_container_width=True)
    st.download_button("📥 Download CSV", df.to_csv(index=False).encode("utf-8"), "attendance.csv", "text/csv")

# ---------------- Delete Records ----------------
elif menu == "Delete Records":
    st.header("🗑️ Delete All Records")
    if st.button("Delete All Attendance Records"):
        pd.DataFrame(columns=["Name", "Date", "Day", "Status"]).to_csv(CSV_FILE, index=False)
        st.success("✅ All attendance records deleted successfully!")

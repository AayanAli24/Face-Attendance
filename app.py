import streamlit as st
import pandas as pd
import os
from datetime import datetime
from PIL import Image

# CSV File Path
CSV_FILE = "attendance.csv"
REGISTER_DIR = "registered_faces"

# Initialize CSV file
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=["Name", "Date", "Day", "Status"])
    df.to_csv(CSV_FILE, index=False)

# Create directory for registered faces
os.makedirs(REGISTER_DIR, exist_ok=True)


# -------------------- Helper Functions --------------------
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


# -------------------- Streamlit UI --------------------
st.set_page_config(page_title="📸 Attendance System", layout="wide")

st.title("📸 Image-Based Attendance System (No OpenCV)")

menu = st.sidebar.radio("Navigation", ["Register", "Mark Attendance", "View Records", "Delete Records"])

# -------------------- Register --------------------
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

# -------------------- Mark Attendance --------------------
elif menu == "Mark Attendance":
    st.header("✅ Mark Attendance")
    registered_faces = os.listdir(REGISTER_DIR)

    if not registered_faces:
        st.warning("No registered faces found. Please register first.")
    else:
        name = st.selectbox("Select your name", [os.path.splitext(n)[0] for n in registered_faces])
        img_file = st.camera_input("Capture your image to mark attendance")

        if img_file and name:
            # (Simplified — no face recognition, just assumes correct person)
            save_attendance(name, "Present")
            st.success(f"Attendance marked for {name} as Present ✅")
            st.image(img_file, caption=f"Attendance Image for {name}", use_container_width=True)

# -------------------- View Records --------------------
elif menu == "View Records":
    st.header("📋 Attendance Records")
    df = load_attendance()
    st.dataframe(df, use_container_width=True)
    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv_data, "attendance.csv", "text/csv")

# -------------------- Delete Records --------------------
elif menu == "Delete Records":
    st.header("🗑️ Delete All Records")
    if st.button("Delete All Attendance Records"):
        pd.DataFrame(columns=["Name", "Date", "Day", "Status"]).to_csv(CSV_FILE, index=False)
        st.success("✅ All attendance records deleted successfully!")

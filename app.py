from flask import Flask, render_template, Response, request, redirect, url_for
import cv2
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

# CSV file for attendance
CSV_FILE = "attendance.csv"

# Initialize webcam
camera = cv2.VideoCapture(0)

# Ensure CSV file exists
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=["Name", "Date", "Time"])
    df.to_csv(CSV_FILE, index=False)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Convert frame to JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/mark', methods=['POST'])
def mark_attendance():
    name = request.form['name']
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    df = pd.read_csv(CSV_FILE)
    df.loc[len(df)] = [name, date, time]
    df.to_csv(CSV_FILE, index=False)

    return redirect(url_for('index'))

@app.route('/records')
def view_records():
    df = pd.read_csv(CSV_FILE)
    return df.to_html(classes="table table-striped", index=False)

if __name__ == '__main__':
    app.run(debug=True)

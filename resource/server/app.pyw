from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_session import Session
import os
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CoInitialize
from PIL import ImageGrab
from io import BytesIO
import base64
import subprocess
import threading
import pystray
from pystray import MenuItem, Icon
from PIL import Image

app = Flask(__name__)

# Session configuration
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Variable LOGIN
LOGIN = True

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            return redirect(url_for('index'))
    return render_template('login.html')

# Main page
@app.route('/')
def index():
    if LOGIN and not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

# Action routes
@app.route('/action/<command>')
def action(command):
    if command == 'shutdown':
        os.system('shutdown /s /t 1')
    elif command == 'restart':
        os.system('shutdown /r /t 1')
    elif command == 'logoff':
        os.system('shutdown /l')
    elif command == 'lock':
        os.system('rundll32.exe user32.dll,LockWorkStation')
    return redirect(url_for('index'))

# Set volume via scrollbar
@app.route('/set_volume', methods=['POST'])
def set_volume():
    CoInitialize()  # Initialize COM for this thread

    volume_value = float(request.form['volume'])  # Get volume value from frontend

    # Get volume control interface
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))

    volume.SetMasterVolumeLevelScalar(volume_value, None)  # Set volume level
    return ('', 204)  # Empty response, success

# Capture screenshot
@app.route('/screenshot')
def screenshot():
    screenshot = ImageGrab.grab()  # Take a screenshot

    # Convert to base64 image
    buffered = BytesIO()
    screenshot.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return jsonify({'image': img_str})  # Return image in base64

# Execute command
@app.route('/run_command', methods=['POST'])
def run_command():
    command = request.form['command']
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout + result.stderr  # Capture output
    except Exception as e:
        output = str(e)

    return jsonify({'output': output})  # Return output

# Function to create the tray icon
def create_tray_icon():
    # Define an icon
    icon_image = Image.open(os.path.join(os.getcwd(),".." , "icon", "hey.png"))
    menu = (MenuItem("Quit", quit_app),)
    icon = Icon("FlaskApp", icon_image, "Flask App", menu)
    icon.run()

def quit_app(icon, item):
    icon.stop()
    os._exit(0)

if __name__ == '__main__':
    threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000}, daemon=True).start()
    subprocess.Popen(['start', 'chrome', 'http://localhost:5000'], shell=True)
    create_tray_icon()
    

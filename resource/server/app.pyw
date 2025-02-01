from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_session import Session
import os
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL, CoInitialize
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from PIL import ImageGrab, Image
from io import BytesIO
import base64
import subprocess
import threading
import webbrowser
from pystray import MenuItem, Icon

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret_key')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Enable login verification
LOGIN_REQUIRED = False

# List of allowed commands for the /run_command endpoint
ALLOWED_COMMANDS = ['dir', 'whoami']

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password': # HEREEEE To change the username and password
            session['logged_in'] = True
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("Incorrect username or password", "error")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash("You have been logged out", "info")
    return redirect(url_for('login'))

@app.route('/')
def index():
    if LOGIN_REQUIRED and not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

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

@app.route('/set_volume', methods=['POST'])
def set_volume():
    try:
        CoInitialize()  # Initialize COM for this thread
        volume_value = float(request.form['volume'])
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMasterVolumeLevelScalar(volume_value, None)
        return ('', 204)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/screenshot')
def screenshot():
    try:
        shot = ImageGrab.grab()
        buffered = BytesIO()
        shot.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return jsonify({'image': img_str})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/run_command', methods=['POST'])
def run_command():
    command = request.form['command']
    # Restrict execution to allowed commands
    if not any(command.strip().startswith(allowed) for allowed in ALLOWED_COMMANDS):
        return jsonify({'output': 'Command not allowed'}), 403
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stdout + result.stderr
    except Exception as e:
        output = str(e)
    return jsonify({'output': output})

def quit_app(icon, item):
    icon.stop()
    os._exit(0)

def create_tray_icon():
    # Define the path of the icon (located in the "icon" folder at the root)
    icon_path = os.path.join(os.getcwd(), "..", "icon", "hey.png")
    if not os.path.exists(icon_path):
        # If no icon is found, create a default white image
        image = Image.new('RGB', (64, 64), color='white')
    else:
        image = Image.open(icon_path)
    menu = (MenuItem("Quit", quit_app),)
    icon = Icon("FlaskApp", image, "Flask App", menu)
    icon.run()

if __name__ == '__main__':
    # Start the Flask app in a background thread
    threading.Thread(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000}, daemon=True).start()
    # Open the default browser to the application's address
    webbrowser.open('http://localhost:5000')
    create_tray_icon()

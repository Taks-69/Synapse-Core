import os
import subprocess
import time
from datetime import datetime, timedelta
from pystyle import Colorate, Colors, Write

def check_last_run():
    last_run_file = 'last_run.txt'

    if not os.path.exists(last_run_file):
        with open(last_run_file, 'w') as f:
            f.write(datetime.now().isoformat())
        return True

    with open(last_run_file, 'r') as f:
        last_run_date = datetime.fromisoformat(f.read().strip())

    if datetime.now() - last_run_date > timedelta(days=2):
        return True 

    return False 

def update_last_run():
    with open('last_run.txt', 'w') as f:
        f.write(datetime.now().isoformat())

def main():
    title = Colorate.Vertical(Colors.red_to_black, """
                 _______                                               ______
                |     __|.--.--..-----..---.-..-----..-----..-----.  |      |.-----..----..-----.
                |__     ||  |  ||     ||  _  ||  _  ||__ --||  -__|  |   ---||  _  ||   _||  -__|
                |_______||___  ||__|__||___._||   __||_____||_____|  |______||_____||__|  |_____|
                         |_____|              |__|
    """)

    print(title)

    print(Colorate.Horizontal(Colors.green_to_cyan, "╔═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╗"))
    print(Colorate.Horizontal(Colors.green_to_cyan, "╠══╣https://guns.lol/takeshi╠═══╣https://guns.lol/takeshi╠═══╣https://guns.lol/takeshi╠═══╣https://guns.lol/takeshi╠══╣"))
    print(Colorate.Horizontal(Colors.green_to_cyan, "╚═════════════════════════════════════════════════════════════════════════════════════════════════════════════════════╝"))

    if check_last_run():
        print("Launching the site: https://guns.lol/Takeshi")
        subprocess.Popen(['start', 'chrome', 'https://guns.lol/Takeshi'], shell=True)

    update_last_run()

    # Installing modules
    Write.Print("Do you want to install all the necessary modules via 'pip install -r requirements.txt'? (y/n) ", Colors.yellow, interval=0.01)
    install_modules = input()
    if install_modules.lower() == 'y':
        subprocess.run(['pip', 'install', '-r', 'requirements.txt'])

    # Running the application
    Write.Print("Do you want 'app.pyw' located in 'resource\\server\\app.pyw' to be launched automatically in the background every time the computer starts? (y/n) ", Colors.yellow, interval=0.01)
    run_app = input()
    if run_app.lower() == 'y':
        shortcut_path = os.path.join(os.environ['USERPROFILE'], r'AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\app.pyw.lnk')
        target = os.path.join(os.getcwd(), 'resource', 'server', 'app.pyw')
        
        # Create a shortcut
        if not os.path.exists(shortcut_path):
            subprocess.run(['powershell', '-command', f"$s=(New-Object -COMObject WScript.Shell).CreateShortcut('{shortcut_path}'); $s.TargetPath='{target}'; $s.Save()"])
            print("Shortcut created to launch 'app.pyw' at startup.")
        else:
            print("Shortcut already exists.")

    Write.Print("Do you want to configure the server to run on the default port 5000? (y/n) ", Colors.yellow, interval=0.01)
    port = input()
    if port.lower() == 'y':
        new_port = '5000'
    else:
        Write.Print("Enter the port you want the server to run on: ", Colors.yellow, interval=0.01)
        new_port = input()

    # Modify app.pyw to use the specified port
    app_file_path = os.path.join(os.getcwd(), 'resource', 'server', 'app.pyw')
    with open(app_file_path, 'r') as file:
        content = file.readlines()

	# Update the port line for the Flask app run
    for i, line in enumerate(content):
        if 'threading.Thread(target=app.run' in line:
            content[i] = f"    threading.Thread(target=app.run, kwargs={{'host': '0.0.0.0', 'port': {new_port}}}, daemon=True).start()\n"  # Ajoute une tabulation ici
            break

	# Update the port line for subprocess.Popen
    for i, line in enumerate(content):
        if 'subprocess.Popen([' in line and 'chrome' in line:
            content[i] = f"    subprocess.Popen(['start', 'chrome', 'http://localhost:{new_port}'], shell=True)\n"
            break

    with open(app_file_path, 'w') as file:
        file.writelines(content)

    print(f"The application will now run on port {new_port}.")

    # start app
    Write.Print("Do you want to launch the application now? (y/n) ", Colors.yellow, interval=0.01)
    launch_app = input()
    if launch_app.lower() == 'y':
        app_file_path = os.path.join(os.getcwd(), 'resource', 'server', 'app.pyw')  # Chemin complet
        subprocess.Popen(['python', app_file_path], cwd=os.path.dirname(app_file_path))  # Exécuter dans le répertoire
        print("Application launched.")
    else:
        os.system("pause")

if __name__ == '__main__':
    main()

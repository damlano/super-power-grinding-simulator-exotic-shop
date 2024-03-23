from PIL import ImageGrab, Image
from pywinauto import Application
from pydirectinput import click
import time
import win32gui, win32process
import requests
from io import BytesIO
import numpy as np
import json

# Load the config.json file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

discord_webhook = config['discord_webhook']
delay_per_cycle = config["delay"]
referance_image_variable = config["reference_image"]

def get_window_pid(title):
    hwnd = win32gui.FindWindow(None, title)
    if hwnd:
        threadid, pid = win32process.GetWindowThreadProcessId(hwnd)
        return pid
    else:
        return None

roblox_pid = get_window_pid('Roblox')

def change_to_roblox():
    app = Application().connect(process=roblox_pid, timeout=5)
    roblox_window = app.top_window()
    roblox_window.set_focus()

def take_screenshot(delay):
    time.sleep(delay)
    screenshot = ImageGrab.grab()
    resized_screenshot = screenshot.resize((1600, 900), Image.LANCZOS)
    crop_box = (630, 110, 860, 130)
    discord_box = (630, 110, 987,203)
    cropped_screenshot = resized_screenshot.crop(crop_box)
    discord_screenshot = resized_screenshot.crop(discord_box)
    return cropped_screenshot, discord_screenshot

def calculate_mse(imageA, imageB):
    if imageA.size != imageB.size:
        imageB = imageB.resize(imageA.size)
    err = np.sum((np.array(imageA) - np.array(imageB)) ** 2)
    err /= float(imageA.size[0] * imageA.size[1])
    return err

def check_screenshot(cropped_screenshot):
    reference_image = Image.open(referance_image_variable)

    mse_value = calculate_mse(reference_image, cropped_screenshot)
    mse_threshold = 100

    if mse_value < mse_threshold:
        return True
    else:
        print('Image is not similair to reference.')
        return False

def send_to_discord(cropped_screenshot):
    byte_io = BytesIO()
    cropped_screenshot.save(byte_io, 'PNG')
    byte_io.seek(0)

    files = {
        'file': ('screenshot.png', byte_io, 'image/png'),
        'payload_json': (None, '{"content": "Here\'s the screenshot:"}')
    }

    response = requests.post(discord_webhook, files=files)
    
    if response.status_code == 204:
        print("Screenshot sent successfully.")
    elif response.status_code == 200:
        print("Likely sent!")
    else:
        print(f"Failed to send screenshot. Status code: {response.status_code}")


while __name__ == "__main__":
    time.sleep(delay_per_cycle)
    change_to_roblox()
    cropped_screenshot, discord_screenshot = take_screenshot(1)
    if check_screenshot(cropped_screenshot) == True:
        click(980, 110)
        send_to_discord(discord_screenshot)

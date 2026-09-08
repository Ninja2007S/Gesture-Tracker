import subprocess
import sys
import webbrowser
from datetime import datetime

import pyautogui

pyautogui.FAILSAFE = False


def action_open_browser():
    print("[ACTION] Opening browser -> https://www.instagram.com/x_sathija_balachandra_x/?hl=en")
    webbrowser.open("https://www.instagram.com/x_sathija_balachandra_x/?hl=en")


def action_take_screenshot():
    filename = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    img = pyautogui.screenshot()
    img.save(filename)
    print(f"[ACTION] Screenshot saved as {filename}")


def action_volume_up():
    print("[ACTION] Volume up")
    for _ in range(3):
        pyautogui.press("volumeup")


def action_volume_down():
    print("[ACTION] Volume down")
    for _ in range(3):
        pyautogui.press("volumedown")


def action_play_pause_media():
    print("[ACTION] Play/Pause media")
    pyautogui.press("playpause")


def action_next_slide():
    print("[ACTION] Next slide (Right arrow)")
    pyautogui.press("right")


def action_prev_slide():
    print("[ACTION] Previous slide (Left arrow)")
    pyautogui.press("left")


def action_say_hello():
    print("[ACTION] 👋 Hello! Gesture recognized.")


def action_lock_screen():
    print("[ACTION] Locking screen...")
    if sys.platform.startswith("win"):
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
    elif sys.platform == "darwin":
        subprocess.run(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"])
    else:
        subprocess.run(["xdg-screensaver", "lock"])


# ---- Edit this to program your own gesture -> action behavior ----
GESTURE_ACTIONS = {
    "open_palm": action_play_pause_media,
    "fist": action_say_hello,
    "peace": action_take_screenshot,
    "pointing": action_next_slide,
    "thumbs_up": action_volume_up,
    "call_me": action_volume_down,
    "rock_on": action_open_browser,
    "ok_sign": action_prev_slide,
}
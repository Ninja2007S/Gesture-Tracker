# Hand Gesture Control (OpenCV + MediaPipe)

Track your hand with a webcam, classify the pose into a named gesture, and
trigger any Python function you want — media control, screenshots, tab
switching, opening a specific site, launching an app, etc. Built with
MediaPipe's HandLandmarker (Tasks API) + OpenCV.

## Demo features included

- **Static gestures** (hold a shape ~0.6s to fire): fist, open palm,
  pointing, peace, thumbs up, rock-on, call-me, OK sign.
- **Swipe gesture**: hold an open palm and move it quickly left/right to
  switch browser tabs (`Ctrl+Tab` / `Ctrl+Shift+Tab`) — separate from the
  static-hold detection so a slow open-palm hold still fires its own action.
- Fully editable gesture → action mapping in one file, no need to touch the
  detection code to change behavior.

## Project files

| File                  | Purpose                                                        |
|------------------------|-----------------------------------------------------------------|
| `gesture_detector.py`  | MediaPipe HandLandmarker wrapper + turns landmarks into a gesture name |
| `gesture_actions.py`   | **Edit this** — maps each gesture name to a function to run    |
| `main.py`              | Camera loop, hold-to-trigger debounce, swipe detection, HUD    |
| `requirements.txt`     | Python dependencies                                             |

## Requirements

- **Python 3.9–3.12.** MediaPipe does not currently publish wheels for
  Python 3.13 or 3.14 — `pip install mediapipe` will fail on those versions.
  If your system's default Python is newer, install 3.11 or 3.12 alongside
  it and point the virtual environment at that version specifically (see
  Step 3 below). You don't need to uninstall or change your system default.
- VS Code with the Python extension (Microsoft).
- A webcam.

## Step 1 — Open the project in VS Code

`File > Open Folder...` → select this project folder.

## Step 2 — Confirm you have a compatible Python installed

```powershell
py --list
```

You need a `3.11` or `3.12` entry. If you don't have one, download it from
https://www.python.org/downloads/ (check "Add python.exe to PATH" during
install) — it can coexist with any other Python version on your machine.

## Step 3 — Create and activate a virtual environment

```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
```

If activation is blocked by execution policy:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

Your prompt should now start with `(venv)`. Confirm the version:
```powershell
python --version
```

## Step 4 — Install dependencies

```powershell
pip install -r requirements.txt
```

## Step 5 — Run it

```powershell
python main.py
```

First run downloads a small (~10MB) hand-landmark model automatically —
normal, one-time only. A window opens showing your webcam feed with the
hand skeleton and current gesture name overlaid.

- Hold a gesture steady for ~0.6s → its mapped action fires (watch the
  progress bar).
- Open palm + fast horizontal swipe → switch tabs.
- **`d`** — toggle skeleton overlay.
- **`q`** — quit.

## Programming your own gestures → actions

Open `gesture_actions.py`. Write a plain function, then point a gesture at
it in `GESTURE_ACTIONS`:

```python
def action_open_youtube():
    webbrowser.open("https://www.youtube.com")

GESTURE_ACTIONS["peace"] = action_open_youtube
```

To add a brand-new *shape* (not just a new action), add a finger-pattern
check inside `classify()` in `gesture_detector.py`, then use that new
gesture name as a key in `GESTURE_ACTIONS`.

## Demo script suggestions

- **Peace sign** → opens a URL — good visual "wow" moment.
- **Open palm swipe** → tab switching — great for a browser-based demo.
- **Pointing** → advance a slide deck (put it in presentation mode first).
- **Thumbs up / call-me** → volume up/down — intuitive for an audience.

## Troubleshooting

- **`mediapipe` fails to install / metadata-generation-failed on numpy:**
  you're likely on Python 3.13+. See Requirements above — use 3.11/3.12.
- **Black window / camera not found:** change `CAMERA_INDEX` in `main.py`,
  or check OS camera privacy settings.
- **Volume/media keys don't work:** those OS media keys are most reliable
  on Windows; on macOS/Linux swap in OS-specific commands (e.g. `osascript`
  on macOS, `amixer` on Linux).
- **Gestures fire too often / not enough:** tune `HOLD_TIME_SECONDS` and
  `COOLDOWN_SECONDS` in `main.py`. For swipes, tune `SWIPE_MIN_DISPLACEMENT`
  and `SWIPE_MAX_DURATION`.

## License

MIT — do whatever you like with it.

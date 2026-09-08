import time
import cv2

from gesture_detector import HandGestureDetector
from gesture_actions import GESTURE_ACTIONS

HOLD_TIME_SECONDS = 0.6
COOLDOWN_SECONDS = 1.2
CAMERA_INDEX = 0


def main():
    detector = HandGestureDetector(max_hands=1)
    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        print("ERROR: could not open the webcam. Check CAMERA_INDEX or camera permissions.")
        return

    show_landmarks = True
    current_gesture = "none"
    gesture_start_time = None
    last_fired_time = 0.0
    prev_frame_time = time.time()

    print("Gesture control running. Press 'q' in the video window to quit.")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Failed to read from camera.")
            break

        frame = cv2.flip(frame, 1)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = detector.process(frame_rgb)

        gesture_this_frame = "none"

        if result.hand_landmarks:
            landmarks = result.hand_landmarks[0]
            handedness_label = result.handedness[0][0].category_name

            if show_landmarks:
                detector.draw_landmarks(frame, landmarks)

            gesture_this_frame = detector.classify(landmarks, handedness_label)

        now = time.time()
        if gesture_this_frame != current_gesture:
            current_gesture = gesture_this_frame
            gesture_start_time = now

        held_long_enough = gesture_start_time is not None and (now - gesture_start_time) >= HOLD_TIME_SECONDS
        cooldown_passed = (now - last_fired_time) >= COOLDOWN_SECONDS

        if held_long_enough and cooldown_passed and current_gesture in GESTURE_ACTIONS:
            GESTURE_ACTIONS[current_gesture]()
            last_fired_time = now
            gesture_start_time = now

        fps = 1.0 / max(now - prev_frame_time, 1e-6)
        prev_frame_time = now

        cv2.putText(frame, f"Gesture: {current_gesture}", (15, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        cv2.putText(frame, f"FPS: {fps:.0f}", (15, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "q: quit   d: toggle landmarks", (15, frame.shape[0] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

        if gesture_start_time is not None and current_gesture in GESTURE_ACTIONS:
            progress = min((now - gesture_start_time) / HOLD_TIME_SECONDS, 1.0)
            bar_w = int(200 * progress)
            cv2.rectangle(frame, (15, 85), (215, 100), (60, 60, 60), -1)
            cv2.rectangle(frame, (15, 85), (15 + bar_w, 100), (0, 255, 0), -1)

        cv2.imshow("Hand Gesture Control", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("d"):
            show_landmarks = not show_landmarks

    cap.release()
    cv2.destroyAllWindows()
    detector.close()


if __name__ == "__main__":
    main()
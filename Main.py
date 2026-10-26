import cv2
from hand_tracker import HandTracker
from virtual_mouse import VirtualMouse
from virtual_keyboard import VirtualKeyboard

CAM_WIDTH, CAM_HEIGHT = 960, 720


def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAM_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_HEIGHT)

    tracker = HandTracker(max_hands=1)
    mouse = VirtualMouse(CAM_WIDTH, CAM_HEIGHT)
    keyboard = VirtualKeyboard()

    mode = "mouse"  # or "keyboard"

    prev_time = 0

    while True:
        success, frame = cap.read()
        if not success:
            print("Failed to grab frame from webcam.")
            break

        frame = cv2.flip(frame, 1)  # mirror for natural interaction
        frame = tracker.find_hands(frame, draw=True)
        landmarks = tracker.get_landmark_positions(frame)

        index_tip = tracker.get_fingertip(landmarks, "index")
        thumb_tip = tracker.get_fingertip(landmarks, "thumb")

        if mode == "mouse":
            mouse.move(index_tip)
            clicked = mouse.check_click(thumb_tip, index_tip)
            if clicked:
                cv2.putText(frame, "CLICK", (500, 50), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 255, 0), 3)

        elif mode == "keyboard":
            frame = keyboard.draw(frame, hover_point=index_tip)
            pressed_key = keyboard.check_press(thumb_tip, index_tip)
            if pressed_key:
                cv2.putText(frame, f"Pressed: {pressed_key.text}", (500, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Mode banner
        cv2.putText(frame, f"MODE: {mode.upper()}  (m=mouse, k=keyboard, q=quit)",
                    (10, frame.shape[0] - 15), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 255, 255), 2)

        cv2.imshow("Virtual Mouse & Keyboard", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("m"):
            mode = "mouse"
        elif key == ord("k"):
            mode = "keyboard"

    tracker.close()
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
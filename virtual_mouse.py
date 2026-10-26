import pyautogui
import numpy as np
import time

pyautogui.FAILSAFE = False  # disable corner-abort safety if it annoys you


class VirtualMouse:
    def __init__(self, cam_width, cam_height, smoothening=5, click_threshold=35):
        self.screen_w, self.screen_h = pyautogui.size()
        self.cam_w, self.cam_h = cam_width, cam_height
        self.smoothening = smoothening
        self.click_threshold = click_threshold

        self.prev_x, self.prev_y = 0, 0
        self.curr_x, self.curr_y = 0, 0

        self.last_click_time = 0
        self.click_cooldown = 0.4  # seconds, avoids double clicks

        # Region of the camera frame mapped to full screen
        # (keeps hand near center of frame for full screen reach)
        self.frame_margin = 100

    def move(self, index_tip):
        """index_tip: (x, y) pixel coords from webcam frame."""
        if index_tip is None:
            return

        x, y = index_tip

        # Map from camera frame range -> screen range
        screen_x = np.interp(
            x, (self.frame_margin, self.cam_w - self.frame_margin), (0, self.screen_w)
        )
        screen_y = np.interp(
            y, (self.frame_margin, self.cam_h - self.frame_margin), (0, self.screen_h)
        )

        # Smoothing
        self.curr_x = self.prev_x + (screen_x - self.prev_x) / self.smoothening
        self.curr_y = self.prev_y + (screen_y - self.prev_y) / self.smoothening

        pyautogui.moveTo(self.curr_x, self.curr_y)
        self.prev_x, self.prev_y = self.curr_x, self.curr_y

    def check_click(self, thumb_tip, index_tip):
        """Trigger a click if thumb and index fingertip are close enough."""
        from hand_tracker import HandTracker  # local import to reuse distance()

        dist = HandTracker.distance(thumb_tip, index_tip)
        now = time.time()

        if dist < self.click_threshold and (now - self.last_click_time) > self.click_cooldown:
            pyautogui.click()
            self.last_click_time = now
            return True
        return False
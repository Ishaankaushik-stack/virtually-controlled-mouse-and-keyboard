import cv2
import pyautogui
import time

KEY_LAYOUT = [
    list("QWERTYUIOP"),
    list("ASDFGHJKL"),
    list("ZXCVBNM"),
    ["SPACE", "BACK"],
]

KEY_W, KEY_H = 55, 55
KEY_GAP = 8
START_X, START_Y = 30, 30


class Key:
    def __init__(self, x, y, w, h, text):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.text = text

    def contains(self, point):
        if point is None:
            return False
        px, py = point
        return self.x <= px <= self.x + self.w and self.y <= py <= self.y + self.h

    def draw(self, frame, highlight=False):
        color = (0, 200, 0) if highlight else (60, 60, 60)
        cv2.rectangle(frame, (self.x, self.y), (self.x + self.w, self.y + self.h), color, cv2.FILLED)
        cv2.rectangle(frame, (self.x, self.y), (self.x + self.w, self.y + self.h), (255, 255, 255), 1)
        font_scale = 0.55 if len(self.text) == 1 else 0.4
        text_size = cv2.getTextSize(self.text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 2)[0]
        tx = self.x + (self.w - text_size[0]) // 2
        ty = self.y + (self.h + text_size[1]) // 2
        cv2.putText(frame, self.text, (tx, ty), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 2)


class VirtualKeyboard:
    def __init__(self, press_threshold=35, press_cooldown=0.6):
        self.keys = []
        self.press_threshold = press_threshold
        self.press_cooldown = press_cooldown
        self.last_press_time = 0
        self.typed_text = ""
        self._build_layout()

    def _build_layout(self):
        for row_idx, row in enumerate(KEY_LAYOUT):
            x = START_X
            y = START_Y + row_idx * (KEY_H + KEY_GAP)
            for key_text in row:
                w = KEY_W * 3 if key_text == "SPACE" else (KEY_W + 20 if key_text == "BACK" else KEY_W)
                self.keys.append(Key(x, y, w, KEY_H, key_text))
                x += w + KEY_GAP

    def draw(self, frame, hover_point=None):
        for key in self.keys:
            highlight = key.contains(hover_point)
            key.draw(frame, highlight=highlight)
        # Show typed text bar
        cv2.rectangle(frame, (START_X, 320), (START_X + 500, 370), (50, 50, 50), cv2.FILLED)
        cv2.putText(frame, self.typed_text[-30:], (START_X + 10, 355),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        return frame

    def check_press(self, thumb_tip, index_tip):
        """If pinch happens over a key, simulate typing that character."""
        from hand_tracker import HandTracker

        dist = HandTracker.distance(thumb_tip, index_tip)
        now = time.time()

        if dist < self.press_threshold and (now - self.last_press_time) > self.press_cooldown:
            for key in self.keys:
                if key.contains(index_tip):
                    self._type_key(key.text)
                    self.last_press_time = now
                    return key
        return None

    def _type_key(self, key_text):
        if key_text == "SPACE":
            pyautogui.press("space")
            self.typed_text += " "
        elif key_text == "BACK":
            pyautogui.press("backspace")
            self.typed_text = self.typed_text[:-1]
        else:
            pyautogui.press(key_text.lower())
            self.typed_text += key_text.lower
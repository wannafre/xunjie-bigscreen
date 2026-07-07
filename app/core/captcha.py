import base64
import io
import json
import logging
import os
import random
import threading
import time
from typing import Dict, Optional, Tuple, Union
from Crypto.Cipher import AES
from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)

# ==========================================
# 1. AES Decryption Utility (AJ-Captcha ECB Mode)
# ==========================================

def decrypt_point_json(encrypted_text: str, key: str) -> dict:
    """
    Decrypts the AES-128 ECB encrypted pointJson sent by AJ-Captcha frontend.
    """
    try:
        key_bytes = key.encode('utf-8')
        encrypted_bytes = base64.b64decode(encrypted_text)
        cipher = AES.new(key_bytes, AES.MODE_ECB)
        decrypted_bytes = cipher.decrypt(encrypted_bytes)
        
        # Remove PKCS7 padding
        padding_len = decrypted_bytes[-1]
        if 1 <= padding_len <= 16:
            # Check padding validity
            if all(b == padding_len for b in decrypted_bytes[-padding_len:]):
                decrypted_bytes = decrypted_bytes[:-padding_len]
                
        decrypted_text = decrypted_bytes.decode('utf-8')
        return json.loads(decrypted_text)
    except Exception as e:
        logger.error(f"Failed to decrypt pointJson: {e}")
        return {}


# ==========================================
# 2. Captcha Image Generation Utility
# ==========================================

def generate_captcha_images() -> Tuple[str, str, int]:
    """
    Generates a dynamic background image (310x155) with random gradients and shapes,
    and a cropped jigsaw puzzle block (47x155) with transparent background.
    Returns: (bg_base64, jigsaw_base64, target_x)
    """
    bg_width = 310
    bg_height = 155
    block_size = 47
    
    # Generate background image with random color gradient
    bg = Image.new("RGB", (bg_width, bg_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(bg)
    
    color1 = (random.randint(40, 140), random.randint(40, 140), random.randint(140, 240))
    color2 = (random.randint(140, 240), random.randint(40, 140), random.randint(40, 140))
    for x in range(bg_width):
        r = int(color1[0] + (color2[0] - color1[0]) * x / bg_width)
        g = int(color1[1] + (color2[1] - color1[1]) * x / bg_width)
        b = int(color1[2] + (color2[2] - color1[2]) * x / bg_width)
        draw.line([(x, 0), (x, bg_height)], fill=(r, g, b))
        
    # Draw noise lines and shapes for anti-ocr protection
    for _ in range(8):
        shape = random.choice(["line", "circle", "rectangle"])
        col = (random.randint(50, 220), random.randint(50, 220), random.randint(50, 220))
        if shape == "line":
            draw.line([(random.randint(0, bg_width), random.randint(0, bg_height)),
                       (random.randint(0, bg_width), random.randint(0, bg_height))], fill=col, width=random.randint(1, 3))
        elif shape == "circle":
            r_size = random.randint(12, 28)
            cx, cy = random.randint(30, bg_width - 30), random.randint(20, bg_height - 20)
            draw.ellipse([cx - r_size, cy - r_size, cx + r_size, cy + r_size], fill=col)
        else:
            x1, y1 = random.randint(20, bg_width - 60), random.randint(20, bg_height - 60)
            x2, y2 = x1 + random.randint(15, 35), y1 + random.randint(15, 35)
            draw.rectangle([x1, y1, x2, y2], fill=col)

    # Random target position for jigsaw puzzle block
    target_x = random.randint(block_size + 20, bg_width - block_size - 20)
    target_y = random.randint(15, bg_height - block_size - 15)

    # Crop jigsaw block from background
    block_img = bg.crop((target_x, target_y, target_x + block_size, target_y + block_size))
    
    # Create transparent jigsaw canvas
    jigsaw_canvas = Image.new("RGBA", (block_size, bg_height), (0, 0, 0, 0))
    
    # Build jigsaw puzzle shape mask
    mask = Image.new("L", (block_size, block_size), 0)
    mask_draw = ImageDraw.Draw(mask)
    # Draw square block body
    mask_draw.rectangle([4, 4, block_size - 5, block_size - 5], fill=255)
    # Right side protruding circle notch
    mask_draw.ellipse([block_size - 9, 18, block_size, 27], fill=255)
    # Left side cutout circle
    mask_draw.ellipse([0, 18, 9, 27], fill=0)
    
    # Paste puzzle piece
    block_rgba = block_img.convert("RGBA")
    jigsaw_piece = Image.new("RGBA", (block_size, block_size), (0, 0, 0, 0))
    jigsaw_piece.paste(block_rgba, (0, 0), mask=mask)
    jigsaw_canvas.paste(jigsaw_piece, (0, target_y))

    # Darken slot area on background
    slot_overlay = Image.new("RGBA", (block_size, block_size), (0, 0, 0, 160))
    bg_rgba = bg.convert("RGBA")
    bg_rgba.paste(slot_overlay, (target_x, target_y), mask=mask)

    # Convert to base64
    bg_io = io.BytesIO()
    bg_rgba.convert("RGB").save(bg_io, format="JPEG")
    bg_base64 = base64.b64encode(bg_io.getvalue()).decode("utf-8")

    jigsaw_io = io.BytesIO()
    jigsaw_canvas.save(jigsaw_io, format="PNG")
    jigsaw_base64 = base64.b64encode(jigsaw_io.getvalue()).decode("utf-8")

    return bg_base64, jigsaw_base64, target_x


# ==========================================
# 3. Captcha Manager Class (Thread-safe Cache)
# ==========================================

class CaptchaManager:
    def __init__(self):
        self._lock = threading.Lock()
        # token -> {"target_x": int, "secret_key": str, "verified": bool, "expires_at": float}
        self._tokens: Dict[str, dict] = {}
        # key (username or IP) -> {"fail_count": int, "last_attempt_at": float}
        self._fails: Dict[str, dict] = {}
        # IP -> list of timestamps
        self._ip_requests: Dict[str, list] = {}

    def clean_expired(self):
        now = time.time()
        with self._lock:
            # Clean expired verification tokens
            expired_tokens = [t for t, d in self._tokens.items() if d["expires_at"] < now]
            for t in expired_tokens:
                del self._tokens[t]
            # Clean old failure history (older than 30 mins)
            expired_fails = [k for k, d in self._fails.items() if now - d["last_attempt_at"] > 1800]
            for k in expired_fails:
                del self._fails[k]
            # Clean old IP rate tracks
            for ip in list(self._ip_requests.keys()):
                self._ip_requests[ip] = [t for t in self._ip_requests[ip] if now - t < 60]
                if not self._ip_requests[ip]:
                    del self._ip_requests[ip]

    def create_token(self, token: str, target_x: int, secret_key: str, ttl: int = 300):
        self.clean_expired()
        now = time.time()
        with self._lock:
            self._tokens[token] = {
                "target_x": target_x,
                "secret_key": secret_key,
                "verified": False,
                "expires_at": now + ttl
            }

    def get_token_data(self, token: str) -> Optional[dict]:
        self.clean_expired()
        with self._lock:
            return self._tokens.get(token)

    def verify_token(self, token: str) -> bool:
        with self._lock:
            if token in self._tokens:
                self._tokens[token]["verified"] = True
                return True
            return False

    def consume_token(self, token: str) -> bool:
        self.clean_expired()
        with self._lock:
            data = self._tokens.get(token)
            if data and data["verified"]:
                # Prevent replay attacks
                del self._tokens[token]
                return True
            return False

    def get_fail_count(self, key: str) -> int:
        self.clean_expired()
        with self._lock:
            return self._fails.get(key, {}).get("fail_count", 0)

    def record_fail(self, key: str):
        now = time.time()
        with self._lock:
            if key not in self._fails:
                self._fails[key] = {"fail_count": 0, "last_attempt_at": now}
            self._fails[key]["fail_count"] += 1
            self._fails[key]["last_attempt_at"] = now

    def reset_fail(self, key: str):
        with self._lock:
            if key in self._fails:
                del self._fails[key]

    def record_ip_request(self, ip: str) -> int:
        now = time.time()
        with self._lock:
            if ip not in self._ip_requests:
                self._ip_requests[ip] = []
            self._ip_requests[ip].append(now)
            # Retain only timestamps from the last 10 seconds
            self._ip_requests[ip] = [t for t in self._ip_requests[ip] if now - t < 10]
            return len(self._ip_requests[ip])

    def get_ip_request_rate(self, ip: str, period: int = 10) -> int:
        now = time.time()
        with self._lock:
            timestamps = self._ip_requests.get(ip, [])
            recent = [t for t in timestamps if now - t < period]
            return len(recent)

captcha_manager = CaptchaManager()

def verify_captcha_verification(captcha_verification: str) -> bool:
    """
    Parses and consumes the verification token from captchaVerification.
    Standard formats:
    1. 'token'
    2. 'token---pointJsonEncrypted'
    """
    if not captcha_verification:
        return False
    if "---" in captcha_verification:
        parts = captcha_verification.split("---")
        token = parts[0]
    else:
        token = captcha_verification
    return captcha_manager.consume_token(token)

# Ganti ke 1 kalau pakai webcam USB eksternal
CAMERA_INDEX = 0
FRAME_WIDTH = 960
FRAME_HEIGHT = 540

USE_TELEGRAM = False
TELEGRAM_BOT_TOKEN = "ISI_TOKEN"
TELEGRAM_CHAT_ID = "ISI_CHAT_ID"
ALERT_COOLDOWN_SECONDS = 10

# Produk Uji: AHH (Kuning), Beng-Beng (Merah), Oreo (Biru)
INITIAL_INVENTORY = {
    "AHH (Kuning)": {
        "stock": 0,
        "max_capacity": 6,
        "min_threshold": 2,
        "price": 1500,
        "roi": (60, 140, 250, 260),
        "theme_color": (0, 230, 240),    # Kuning cerah
        # HSV Kuning AHH Nabati (Hue 20 - 38, Saturation pekat)
        "hsv_ranges": [
            ((20, 110, 80), (38, 255, 255))
        ],
        "min_contour_area": 3000,
    },
    "Beng-Beng (Merah)": {
        "stock": 0,
        "max_capacity": 6,
        "min_threshold": 2,
        "price": 2500,
        "roi": (355, 140, 250, 260),
        "theme_color": (0, 0, 255),      # Merah
        # Saturasi dinaikkan ke >= 135 agar kulit tangan manusia (S: 50-110) 100% diabaikan
        "hsv_ranges": [
            ((0, 135, 70), (9, 255, 255)),
            ((168, 135, 70), (180, 255, 255))
        ],
        "min_contour_area": 3000,
    },
    "Oreo (Biru)": {
        "stock": 0,
        "max_capacity": 6,
        "min_threshold": 2,
        "price": 2000,
        "roi": (650, 140, 250, 260),
        "theme_color": (255, 140, 0),    # Biru khas Oreo
        # HSV Biru Oreo Original (Hue 98 - 130, Saturation pekat)
        "hsv_ranges": [
            ((98, 110, 60), (130, 255, 255))
        ],
        "min_contour_area": 3000,
    },
}

BLUR_KERNEL = (5, 5)
DEBOUNCE_FRAMES = 3

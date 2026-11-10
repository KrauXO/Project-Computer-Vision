# Ganti ke 1 kalau pakai webcam USB eksternal
CAMERA_INDEX = 0
FRAME_WIDTH = 960
FRAME_HEIGHT = 540

USE_TELEGRAM = False
TELEGRAM_BOT_TOKEN = "ISI_TOKEN"
TELEGRAM_CHAT_ID = "ISI_CHAT_ID"
ALERT_COOLDOWN_SECONDS = 10

# Produk Uji: AHH (Kuning), Choco Pie (Merah Marun), Oreo (Biru)
INITIAL_INVENTORY = {
    "AHH (Kuning)": {
        "stock": 0,
        "max_capacity": 6,
        "min_threshold": 2,
        "price": 1500,
        "roi": (60, 140, 250, 260),
        "theme_color": (0, 230, 240),
        "hsv_ranges": [
            ((20, 100, 80), (38, 255, 255))
        ],
        "min_contour_area": 1600,
    },
    "Choco Pie (Merah)": {
        "stock": 0,
        "max_capacity": 6,
        "min_threshold": 2,
        "price": 3000,
        "roi": (355, 140, 250, 260),
        "theme_color": (0, 0, 255),
        # HSV Merah Marun Lotte Choco Pie:
        # Hue 0-7 & 170-180 (membuang rona kulit tangan di Hue 10-22)
        # Saturation 85-255 & Value 45-255 (menangkap merah marun pekat)
        "hsv_ranges": [
            ((0, 85, 45), (7, 255, 255)),
            ((170, 85, 45), (180, 255, 255))
        ],
        "min_contour_area": 1600,
    },
    "Oreo (Biru)": {
        "stock": 0,
        "max_capacity": 6,
        "min_threshold": 2,
        "price": 2000,
        "roi": (650, 140, 250, 260),
        "theme_color": (255, 140, 0),
        "hsv_ranges": [
            ((98, 90, 50), (130, 255, 255))
        ],
        "min_contour_area": 1600,
    },
}

BLUR_KERNEL = (5, 5)
DEBOUNCE_FRAMES = 3

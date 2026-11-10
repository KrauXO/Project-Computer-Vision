# Ganti ke 1 kalau pakai webcam USB eksternal
CAMERA_INDEX = 0
FRAME_WIDTH = 960
FRAME_HEIGHT = 540

# Ubah ke True dan isi token kalau mau notif ke Telegram beneran
USE_TELEGRAM = False
TELEGRAM_BOT_TOKEN = "ISI_TOKEN"
TELEGRAM_CHAT_ID = "ISI_CHAT_ID"
ALERT_COOLDOWN_SECONDS = 10

# Format ROI: (x, y, w, h)
INITIAL_INVENTORY = {
    "Pilus (Hijau)": {
        "stock": 0,
        "max_capacity": 6,
        "min_threshold": 2,
        "price": 2000,
        "roi": (60, 140, 250, 260),
        "theme_color": (0, 220, 0),
        "hsv_ranges": [
            ((35, 60, 40), (85, 255, 255))
        ],
        "min_contour_area": 1200,
    },
    "Beng-Beng (Merah)": {
        "stock": 0,
        "max_capacity": 6,
        "min_threshold": 2,
        "price": 2500,
        "roi": (355, 140, 250, 260),
        "theme_color": (0, 0, 255),
        # Merah di HSV split di 0-10 sama 165-180
        "hsv_ranges": [
            ((0, 75, 40), (10, 255, 255)),
            ((165, 75, 40), (180, 255, 255))
        ],
        "min_contour_area": 1200,
    },
    "Slai O'Lai (Biru)": {
        "stock": 0,
        "max_capacity": 6,
        "min_threshold": 2,
        "price": 3000,
        "roi": (650, 140, 250, 260),
        "theme_color": (255, 140, 0),
        "hsv_ranges": [
            ((95, 70, 40), (130, 255, 255))
        ],
        "min_contour_area": 1200,
    },
}

BLUR_KERNEL = (5, 5)
DEBOUNCE_FRAMES = 3  # Butuh 3 frame stabil biar angka stok gak kedip-kedip

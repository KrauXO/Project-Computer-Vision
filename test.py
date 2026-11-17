import cv2
from collections import deque
from statistics import mode
from ultralytics import YOLO

# Load model hasil training lokal yang baru saja jadi
model = YOLO("runs/detect/model_sekre/weights/best.pt")

# Ambil daftar nama kelas yang dilatih
CLASSES = model.names.values()
MIN_STOCK = 1
HISTORY_LEN = 10  # Smoothing agar angka stabil di layar

history = {cls: deque(maxlen=HISTORY_LEN) for cls in CLASSES}

# Buka kamera (0 untuk webcam laptop, atau 1 jika pakai kamera eksternal/HP)
cap = cv2.VideoCapture(0)

print("[INFO] Memulai Smart Inventory. Tekan 'q' untuk keluar.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Prediksi frame dengan model kustom
    results = model.predict(frame, conf=0.85, iou=0.60, verbose=False)
    
    current_counts = {cls: 0 for cls in CLASSES}
    for box in results[0].boxes:
        cls_idx = int(box.cls[0])
        cls_name = model.names[cls_idx]
        current_counts[cls_name] += 1

    # Gambar hasil deteksi di frame
    annotated_frame = results[0].plot()

    # Tampilkan teks jumlah stok di pojok kiri atas
    y_pos = 35
    for cls in CLASSES:
        history[cls].append(current_counts[cls])
        stable_qty = mode(history[cls])

        color = (0, 255, 0)
        text = f"{cls.upper()}: {stable_qty} pcs"

        if stable_qty <= MIN_STOCK:
            color = (0, 0, 255)  # Merah jika menipis
            text += " [STOK MENIPIS!]"

        cv2.putText(annotated_frame, text, (20, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        y_pos += 30

    cv2.imshow("Smart Inventory Sekre HMIF - Live Demo", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
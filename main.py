import time
from datetime import datetime
import cv2
import config
from detector import SnackVisionDetector
from notifier import InventoryNotifier


WINDOW_NAME = "Smart Inventory Kamera Sekre HMIF"


def draw_hud(frame, debug_vis, inventory_state, notifier, fps):
    h, w, _ = frame.shape
    now_str = datetime.now().strftime("%H:%M:%S")

    # Header
    cv2.rectangle(frame, (0, 0), (w, 65), (20, 22, 28), -1)
    cv2.putText(frame, "SMART INVENTORY SEKRE HMIF", (20, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.68, (0, 240, 190), 2)
    cv2.putText(frame, f"AHH (Kuning) | Beng-Beng (Merah) | Oreo (Biru) | FPS: {fps:.1f} | [Q] Keluar",
                (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (190, 200, 210), 1)

    total_items = 0
    total_valuation = 0
    any_low_stock = False
    blink = int(time.time() * 3) % 2 == 0

    # Gambar kotak produk (ROI)
    for name, data in inventory_state.items():
        x, y, rw, rh = data["roi"]
        stock = data["stock"]
        min_t = data["min_threshold"]
        max_cap = data["max_capacity"]
        price = data["price"]
        theme_color = data["theme_color"]

        total_items += stock
        total_valuation += stock * price
        is_low = stock < min_t
        if is_low:
            any_low_stock = True

        if stock == 0:
            border_color = (0, 0, 255) if blink else (0, 50, 180)
            status_txt = "KOSONG (0 PCS)"
        elif is_low:
            border_color = (0, 70, 255) if blink else (0, 120, 255)
            status_txt = f"LOW STOCK ({stock} PCS)"
        else:
            border_color = theme_color
            status_txt = f"AMAN ({stock} PCS)"

        cv2.rectangle(frame, (x, y), (x + rw, y + rh), border_color, 2)
        cv2.rectangle(frame, (x, y - 32), (x + rw, y), border_color, -1)
        cv2.putText(frame, f"{name}: {stock}/{max_cap} pcs", (x + 8, y - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.52, (255, 255, 255), 2)
        cv2.putText(frame, status_txt, (x + 10, y + rh - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.50, border_color, 2)

    # Panel bawah (Valuasi & Log Alert)
    panel_h = 110
    footer_y = h - panel_h
    cv2.rectangle(frame, (0, footer_y), (w, h), (18, 20, 26), -1)
    cv2.line(frame, (0, footer_y), (w, footer_y), (40, 45, 55), 2)

    status_summary = "PERLU RESTOCK!" if any_low_stock else "STOK AMAN"
    summary_color = (0, 80, 255) if any_low_stock else (0, 230, 110)

    cv2.putText(frame, f"TOTAL: {total_items} pcs | VALUASI: Rp {total_valuation:,} | STATUS: {status_summary}",
                (20, footer_y + 26), cv2.FONT_HERSHEY_SIMPLEX, 0.52, summary_color, 2)

    for i, log_msg in enumerate(notifier.logs[-2:]):
        cv2.putText(frame, log_msg, (20, footer_y + 54 + i * 22),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 210, 220), 1)

    # Mini HSV mask di pojok kanan bawah
    if debug_vis is not None:
        pip_w, pip_h = 160, 90
        pip_res = cv2.resize(debug_vis, (pip_w, pip_h))
        px = w - pip_w - 15
        py = footer_y + (panel_h - pip_h) // 2
        frame[py:py+pip_h, px:px+pip_w] = pip_res
        cv2.rectangle(frame, (px, py), (px + pip_w, py + pip_h), (0, 220, 255), 1)
        cv2.putText(frame, "HSV MASK", (px + 6, py + 14),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 255, 255), 1)


def main():
    cap = cv2.VideoCapture(config.CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

    if not cap.isOpened():
        print(f"[ERROR] Kamera #{config.CAMERA_INDEX} gak kebuka.")
        return

    detector = SnackVisionDetector()
    notifier = InventoryNotifier()
    inventory_state = {k: v.copy() for k, v in config.INITIAL_INVENTORY.items()}

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, config.FRAME_WIDTH, config.FRAME_HEIGHT)

    prev_time = time.time()
    fps = 30.0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[WARN] Gagal baca frame.")
            break

        frame = cv2.resize(frame, (config.FRAME_WIDTH, config.FRAME_HEIGHT))

        annotated_frame, debug_vis = detector.process_frame(frame, inventory_state)
        notifier.check_and_notify(inventory_state)

        curr_time = time.time()
        fps = 0.85 * fps + 0.15 * (1.0 / max(curr_time - prev_time, 1e-4))
        prev_time = curr_time

        draw_hud(annotated_frame, debug_vis, inventory_state, notifier, fps)
        cv2.imshow(WINDOW_NAME, annotated_frame)

        key = cv2.waitKey(20) & 0xFF
        if key in (ord('q'), 27):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

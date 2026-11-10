import cv2
import numpy as np
import config


class SnackVisionDetector:
    def __init__(self):
        self._morph_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        self._candidate_counts = {name: 0 for name in config.INITIAL_INVENTORY}
        self._stability_counter = {name: 0 for name in config.INITIAL_INVENTORY}

    def process_frame(self, frame_bgr, inventory_state):
        annotated = frame_bgr.copy()
        blurred = cv2.GaussianBlur(frame_bgr, config.BLUR_KERNEL, 0)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

        debug_mask_combined = np.zeros((config.FRAME_HEIGHT, config.FRAME_WIDTH), dtype=np.uint8)

        for name, data in inventory_state.items():
            x, y, w, h = data["roi"]
            min_area = data["min_contour_area"]
            max_cap = data["max_capacity"]

            roi_hsv = hsv[y:y+h, x:x+w]

            # Filter warna sesuai rentang HSV di config
            roi_mask = np.zeros((h, w), dtype=np.uint8)
            for (lower, upper) in data["hsv_ranges"]:
                lower_np = np.array(lower, dtype=np.uint8)
                upper_np = np.array(upper, dtype=np.uint8)
                sub_mask = cv2.inRange(roi_hsv, lower_np, upper_np)
                roi_mask = cv2.bitwise_or(roi_mask, sub_mask)

            # Bersihin noise bintik kecil
            roi_mask = cv2.morphologyEx(roi_mask, cv2.MORPH_OPEN, self._morph_kernel)
            roi_mask = cv2.morphologyEx(roi_mask, cv2.MORPH_CLOSE, self._morph_kernel)
            debug_mask_combined[y:y+h, x:x+w] = roi_mask

            contours, _ = cv2.findContours(roi_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            detected_items_in_roi = 0

            for cnt in contours:
                area = cv2.contourArea(cnt)
                if area < min_area:
                    continue

                bx, by, bw, bh = cv2.boundingRect(cnt)
                sub_blob = roi_mask[by:by+bh, bx:bx+bw]

                # Distance transform buat cari titik pusat (tetap 1 barang meski dekat kamera, dan bisa misah kalau dempet)
                dist_transform = cv2.distanceTransform(sub_blob, cv2.DIST_L2, 5)
                max_val = np.max(dist_transform)
                if max_val <= 0:
                    continue

                # Ambil puncak kedalaman > 45%
                _, peak_mask = cv2.threshold(dist_transform, 0.45 * max_val, 255, cv2.THRESH_BINARY)
                peak_mask = np.uint8(peak_mask)

                peak_contours, _ = cv2.findContours(peak_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                valid_peaks = []
                for pc in peak_contours:
                    if cv2.contourArea(pc) >= 80:
                        M = cv2.moments(pc)
                        if M["m00"] > 0:
                            pcx = int(M["m10"] / M["m00"])
                            pcy = int(M["m01"] / M["m00"])
                            valid_peaks.append((pcx, pcy))

                num_items = max(1, len(valid_peaks))
                detected_items_in_roi += num_items

                abs_x, abs_y = x + bx, y + by
                box_color = (0, 255, 255) if num_items == 1 else (0, 165, 255)
                cv2.rectangle(annotated, (abs_x, abs_y), (abs_x + bw, abs_y + bh), box_color, 2)

                if valid_peaks:
                    for p_idx, (pcx, pcy) in enumerate(valid_peaks):
                        global_cx = abs_x + pcx
                        global_cy = abs_y + pcy
                        cv2.circle(annotated, (global_cx, global_cy), 6, (0, 0, 255), -1)
                        cv2.putText(annotated, f"#{p_idx + 1}", (global_cx - 8, global_cy - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 255, 0), 2)
                else:
                    cx, cy = abs_x + bw // 2, abs_y + bh // 2
                    cv2.circle(annotated, (cx, cy), 6, (0, 0, 255), -1)

                label = f"{num_items} PCS" if num_items > 1 else "1 PCS"
                cv2.putText(annotated, f"{label} ({int(area)}px)", (abs_x, abs_y - 8),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.44, box_color, 2)

            final_stock = min(detected_items_in_roi, max_cap)
            self._update_stock_debounced(name, final_stock, data)

        debug_vis = cv2.cvtColor(debug_mask_combined, cv2.COLOR_GRAY2BGR)
        return annotated, debug_vis

    def _update_stock_debounced(self, name, new_count, item_data):
        # Nahan angka stok selama beberapa frame biar stabil waktu tangan orang ngambil barang
        if self._candidate_counts[name] == new_count:
            self._stability_counter[name] += 1
        else:
            self._candidate_counts[name] = new_count
            self._stability_counter[name] = 1

        if self._stability_counter[name] >= config.DEBOUNCE_FRAMES:
            item_data["stock"] = new_count

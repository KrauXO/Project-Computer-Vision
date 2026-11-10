import csv
import os
import time
import threading
import urllib.request
import urllib.parse
from datetime import datetime
import config


class InventoryNotifier:
    def __init__(self, csv_filename="inventory_log.csv"):
        self.logs = [
            f"[{datetime.now().strftime('%H:%M:%S')}] Sistem aktif & memantau etalase.",
        ]
        self.last_alert_time = {name: 0.0 for name in config.INITIAL_INVENTORY}
        self.csv_filename = csv_filename
        self._init_csv()

    def _init_csv(self):
        if not os.path.exists(self.csv_filename):
            try:
                with open(self.csv_filename, mode="w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Timestamp", "Event", "Item", "Stock", "Min_Threshold", "Price", "Notes"])
            except Exception as e:
                print(f"[WARN] Gagal bikin CSV log: {e}")

    def add_log(self, tag, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] [{tag}] {message}"
        print(entry)
        self.logs.append(entry)
        if len(self.logs) > 5:
            self.logs.pop(0)

    def record_csv(self, event_type, item_name, stock, min_thresh, price, notes=""):
        try:
            with open(self.csv_filename, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    event_type,
                    item_name,
                    stock,
                    min_thresh,
                    price,
                    notes,
                ])
        except Exception:
            pass

    def check_and_notify(self, inventory_state, force=False):
        now = time.time()
        for name, data in inventory_state.items():
            stock = data["stock"]
            min_t = data["min_threshold"]
            price = data["price"]

            if stock < min_t:
                cooldown_elapsed = (now - self.last_alert_time.get(name, 0.0)) > config.ALERT_COOLDOWN_SECONDS
                if cooldown_elapsed or force:
                    self.last_alert_time[name] = now
                    status = "HABIS (0 pcs)" if stock == 0 else f"Sisa {stock} pcs"
                    msg = f"Stok {name} {status} (Batas min: {min_t} pcs). Segera restock!"
                    self.add_log("ALERT", msg)
                    self.record_csv("LOW_STOCK", name, stock, min_t, price, status)
                    self._send_telegram_async(name, stock, min_t, price)

    def _send_telegram_async(self, item_name, stock, min_t, price):
        # Kirim di background thread biar webcam gak ngelag
        if not config.USE_TELEGRAM or "ISI_" in config.TELEGRAM_BOT_TOKEN:
            return

        def _worker():
            try:
                text = (
                    f"🚨 *PERINGATAN STOK SEKRE HMIF*\n"
                    f"━━━━━━━━━━━━━━━━━━━\n"
                    f"📦 *Produk:* {item_name}\n"
                    f"📉 *Sisa:* {stock} pcs (Min: {min_t})\n"
                    f"💰 *Harga:* Rp {price:,}\n"
                    f"🕒 *Waktu:* {datetime.now().strftime('%H:%M:%S')}\n\n"
                    f"⚠️ Tolong tim Ekobis segera restock."
                )
                url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
                payload = urllib.parse.urlencode({
                    "chat_id": config.TELEGRAM_CHAT_ID,
                    "text": text,
                    "parse_mode": "Markdown",
                }).encode("utf-8")
                req = urllib.request.Request(url, data=payload, method="POST")
                with urllib.request.urlopen(req, timeout=4) as resp:
                    if resp.status == 200:
                        self.add_log("TELE", f"Notif Telegram {item_name} terkirim.")
            except Exception as e:
                self.add_log("WARN", f"Gagal kirim Telegram: {e}")

        threading.Thread(target=_worker, daemon=True).start()

# Smart Inventory Kamera Sekre HMIF UNDIP

Prototipe sistem pemantauan stok jajanan etalase di Sekretariat HMIF UNDIP berbasis **Computer Vision (OpenCV)** secara *real-time*. Proyek ini dirancang untuk mendeteksi ketersediaan fisik snack di atas meja/etalase tanpa input manual, memantau nilai aset kas, serta memicu peringatan restock otomatis saat barang menipis.

---

## Latar Belakang & Masalah

Etalase jajanan di sekre sering kali kehabisan stok tanpa terpantau secara langsung, dan pencatatan manual memerlukan waktu rekap dari pengurus divisi Ekonomi & Bisnis (Ekobis). Sistem ini memanfaatkan kamera/webcam sebagai sensor otomatis untuk:

- Menghitung sisa fisik produk di masing-masing partisi rak secara kontinu.
- Mengetahui valuasi barang yang masih tersedia di etalase (`total_stok x harga_satuan`).
- Memberi notifikasi instan ketika stok berada di bawah batas minimum (*threshold*).

---

## Pendekatan Teknis (Visi Komputer)

Sistem menggunakan alur pemrosesan citra klasik (*classical computer vision*) yang ringan dan berjalan stabil di laptop tanpa memerlukan training model deep learning:

1. **Region of Interest (ROI) Partitioning**  
   Area tangkapan kamera dibagi menjadi 3 zona produk:
   - **Zona Kiri:** AHH Nabati (Kemasan Kuning Keju)
   - **Zona Tengah:** Lotte Choco Pie (Kemasan Merah Marun)
   - **Zona Kanan:** Oreo Original (Kemasan Biru)

2. **Segmentasi Warna HSV (`cv2.cvtColor` + `cv2.inRange`)**  
   Warna kemasan diisolasi pada ruang warna HSV untuk memisahkan komponen warna (*Hue*) dari intensitas pencahayaan (*Value*). Khusus zona tengah Choco Pie, rentang Hue dikunci di $0 - 7$ dan $170 - 180$ dengan saturasi tinggi ($S \ge 85$), sehingga rona kulit tangan manusia (Hue $10 - 22$) otomatis tereliminasi dan tangan tidak salah terhitung sebagai barang.

3. **Pembersihan Morfologi (`MORPH_OPEN` & `MORPH_CLOSE`)**  
   Menutup celah grafis teks/logo pada kemasan dan menghilangkan derau bintik kecil pada latar belakang.

4. **Pemisahan Objek Dempet (Euclidean Distance Transform)**  
   Alih-alih menebak jumlah barang dari luas area (yang rentan keliru saat barang ditaruh dekat kamera), sistem menggunakan `cv2.distanceTransform` untuk mendeteksi puncak kedalaman geometris (*local peaks / center of mass*):
   - Objek tunggal (meskipun tampak besar di kamera) tetap terhitung **1 barang** karena hanya memiliki 1 puncak.
   - Dua snack yang ditaruh menempel/dempet terdeteksi sebagai **2 barang** karena memiliki 2 puncak kedalaman terpisah.

5. **Temporal Debounce Filter**  
   Perubahan angka stok divalidasi selama beberapa frame berturut-turut untuk mencegah *flicker* ketika tangan pembeli sedang bergerak di depan kamera.

---

## Struktur File

```text
Viskom/
├── config.py         # Konfigurasi ROI, rentang HSV, batas threshold, dan harga
├── detector.py       # Pipeline visi komputer (HSV, morfologi, distance transform)
├── notifier.py       # Logika bisnis, audit CSV, alert cooldown, dan Telegram bot
├── main.py           # Program utama (loop kamera, dashboard HUD, event handling)
├── run.bat           # Shortcut sekali klik untuk menjalankan program
├── requirements.txt  # Dependensi Python (opencv-python, numpy)
└── inventory_log.csv # Log pencatatan transaksi & histori stok otomatis
```

---

## Cara Menjalankan

### 1. Persiapan Dependensi

Pastikan dependensi telah terpasang di environment Python:

```bash
pip install -r requirements.txt
```

### 2. Menjalankan Program

Pilih salah satu cara berikut:

- **Cara 1 (Langsung):** Dobel klik file `run.bat`
- **Cara 2 (Terminal):**
  ```bash
  python main.py
  ```

Tekan **`Q`** atau tombol **`ESC`** pada jendela aplikasi untuk keluar.

---

## Integrasi Telegram (Opsional)

Untuk mengaktifkan pengiriman notifikasi otomatis ke grup Telegram tim Ekobis:

1. Buka file `config.py`.
2. Ubah `USE_TELEGRAM = True`.
3. Masukkan `TELEGRAM_BOT_TOKEN` dan `TELEGRAM_CHAT_ID`.
4. Pengiriman pesan berjalan di thread latar belakang (*non-blocking*) sehingga tidak membebani performa streaming kamera.

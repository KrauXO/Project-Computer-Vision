from ultralytics import YOLO

if __name__ == '__main__':
    # Load model dasar
    model = YOLO("yolo11n.pt")

    # Mulai training menggunakan GPU (device=0)
    model.train(
        data="C:\\Users\\enams\\Documents\\Kuliah Saburo\\Semester 5\\Viskom\\data.yaml",
        epochs=60,
        imgsz=640,
        batch=16,
        device=0,
        patience=15,
        name="model_sekre"
    )
import serial
import time
import cv2
from ultralytics import YOLO
import numpy as np

# YOLOv8 model
model = YOLO('parklast.pt')

# Set up serial communication (COM port)
arduino = serial.Serial('COM3', 9600, timeout=1)

# Dosya yolu
dosya_yolu = 'carpark4.mp4'  # Video dosyası için

# Dosya türünü kontrol et
if dosya_yolu.endswith('.mp4'):
    kaynak = cv2.VideoCapture(dosya_yolu)
elif dosya_yolu.endswith('.jpg'):
    kaynak = cv2.imread(dosya_yolu)
else:
    raise ValueError('Desteklenmeyen dosya formatı')

# Son servo hareketinden bu yana geçen süreyi takip etmek için bir zaman damgası
son_servo_hareketi = 0
# Servo motorun son konumunda bekleyeceği süre (saniye cinsinden)
bekleme_suresi = 10

# Function to send data to Arduino
def send_to_arduino(data):
    arduino.write(data.encode())

# Class names and colors (assuming class 0 is Nesne1 and class 1 is Nesne2)
class_names = ['dolu', 'bos']
colors = [(255, 0, 0), (0, 255, 0)]  # Yeşil ve Mavi

# Nesne1 detection flag
bos_detected = False

threshold = 0.06

# Video için döngü
while True:
    # Video veya resimden görüntüyü oku
    if isinstance(kaynak, cv2.VideoCapture):
        ret, frame = kaynak.read()
        if not ret:
            print("Video dosyasından görüntü alınamıyor.")
            break
    else:
        frame = kaynak.copy()

    # Perform object detection
    results = model.predict(frame, imgsz=800, conf=threshold)  # Doğrudan NumPy dizisini kullan

    # Geçerli zamanı al
    simdiki_zaman = int(round(time.time()))

    # Reset Nesne1 detection flag
    bos_detected = False

    # Process results (e.g., check for a specific class)
    for result in results:
        if result.boxes is not None:
            for box in result.boxes:
                # Box nesnesinden koordinatları ve sınıf bilgisini çıkar
                xmin, ymin, xmax, ymax = box.xyxy[0].numpy()  # Koordinatları al
                conf = box.conf[0].numpy()  # Güven skorunu al
                cls = box.cls[0].numpy()  # Sınıf etiketini al
                label = f"{class_names[int(cls)]}"  # Sınıf adı etiketi
                conf_label = f"{conf:.2f}"  # Güven skoru etiketi

                # Sınıfa göre renk seç
                color = colors[int(cls)]

                # Dikdörtgeni çiz
                cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), color, 1)
                # Sınıf adını yaz
                cv2.putText(frame, label, (int(xmin + (xmax - xmin) / 2 - len(label) * 3), int(ymin - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 1), 2)
                # Güven skorunu yaz
                cv2.putText(frame, conf_label, (int(xmin + (xmax - xmin) / 2 - len(conf_label) * 3), int(ymax + 20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.1, (255, 255, 1), 1)

                if cls == 0:  # Assuming class 0 is Nesne1
                    bos_detected = True
                    # Eğer son servo hareketinden itibaren belirli bir süre geçtiyse, servo motoru hareket ettir
                    if (simdiki_zaman - son_servo_hareketi) > bekleme_suresi:
                        send_to_arduino('detected')
                        son_servo_hareketi = simdiki_zaman

    # Nesne1 detection message
    if bos_detected:
        cv2.putText(frame, "bos alan tespit edildi", (int(frame.shape[1] / 2 - 100), int(frame.shape[0] - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    else:
        cv2.putText(frame, "alan tespit edilmedi", (int(frame.shape[1] / 2 - 100), int(frame.shape[0] - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # Görüntüyü göster
    cv2.imshow('YOLOv8 Object Detection', frame)

    # Eğer video dosyası ise ve 'q' tuşuna basılırsa döngüden çık
    if isinstance(kaynak, cv2.VideoCapture) and cv2.waitKey(1) == ord('q'):
        break

# Close the serial connection and release the resources
arduino.close()
if isinstance(kaynak, cv2.VideoCapture):
    kaynak.release()
cv2.destroyAllWindows()

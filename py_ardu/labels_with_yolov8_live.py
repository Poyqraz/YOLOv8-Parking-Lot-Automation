import serial
import time
import cv2
from ultralytics import YOLO
from PIL import Image
import numpy as np

# YOLOv8 model
model = YOLO('park.pt')

# Set up serial communication (COM port)
arduino = serial.Serial('COM3', 9600, timeout=1)

# Webcam'i aç
webcam = cv2.VideoCapture(1)  # varsayılan kamerayı temsil eder

# Son servo hareketinden bu yana geçen süreyi takip etmek için bir zaman damgası
son_servo_hareketi = 0
# Servo motorun son konumunda bekleyeceği süre (saniye cinsinden)
bekleme_suresi = 10

# Function to send data to Arduino
def send_to_arduino(data):
    arduino.write(data.encode())

# Class names and colors (assuming class 0 is Nesne1 and class 1 is Nesne2)
class_names = ['space_empty', 'space_occupied']
colors = [(0, 255, 0), (255, 0, 0)]  # Yeşil ve Mavi

# Nesne1 detection flag
space_empty_detected = False

while True:
    # Webcam'den görüntüyü oku
    ret, frame = webcam.read()
    if not ret:
        print("Kamera görüntüsü alınamıyor.")
        break

    # Görüntüyü PIL Image'e dönüştür
    image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # Perform object detection
    results = model.predict(image)

    # Geçerli zamanı al
    simdiki_zaman = int(round(time.time()))

    # Reset Nesne1 detection flag
    space_empty_detected = False

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
                cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), color, 2)
                # Sınıf adını yaz
                cv2.putText(frame, label, (int(xmin + (xmax - xmin)/2 - len(label) * 3), int(ymin - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 1), 2)
                # Güven skorunu yaz
                cv2.putText(frame, conf_label, (int(xmin + (xmax - xmin)/2 - len(conf_label) * 3), int(ymax + 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 1), 2)

                if cls == 0:  # Assuming class 0 is Nesne1
                    space_empty_detected = True
                    # Eğer son servo hareketinden itibaren belirli bir süre geçtiyse, servo motoru hareket ettir
                    if (simdiki_zaman - son_servo_hareketi) > bekleme_suresi:
                        send_to_arduino('detected')
                        son_servo_hareketi = simdiki_zaman

        # Nesne1 detection message
        if space_empty_detected:
            cv2.putText(frame, "alan tespit edildi", (int(frame.shape[1] / 2 - 100), int(frame.shape[0] - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "alan tespit edilmedi", (int(frame.shape[1] / 2 - 100), int(frame.shape[0] - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Görüntüyü göster
        cv2.imshow('YOLOv8 Object Detection', frame)

        if cv2.waitKey(1) == ord('q'):
            break

    # Close the serial connection and release the webcam
arduino.close()
webcam.release()
cv2.destroyAllWindows()
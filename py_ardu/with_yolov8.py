import serial
import time
import cv2
from ultralytics import YOLO
from PIL import Image
import numpy as np

# YOLOv8 model
model = YOLO('custom.pt')

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

    # Process results (e.g., check for a specific class)
    for result in results:
        if result.boxes is not None:
            for box in result.boxes:
                # Box nesnesinden koordinatları ve sınıf bilgisini çıkar
                xmin, ymin, xmax, ymax = box.xyxy[0].numpy()  # Koordinatları al
                conf = box.conf[0].numpy()  # Güven skorunu al
                cls = box.cls[0].numpy()  # Sınıf etiketini al
                if cls == 0:  # Assuming class 0 is the object of interest

                    # Eğer son servo hareketinden itibaren belirli bir süre geçtiyse, servo motoru hareket ettir
                    if (simdiki_zaman - son_servo_hareketi) > bekleme_suresi:
                        send_to_arduino('detected')
                        son_servo_hareketi = simdiki_zaman
                else:
                    send_to_arduino('not_detected')

    # Görüntüyü göster
    cv2.imshow('YOLOv8 Object Detection', np.array(image))

    if cv2.waitKey(1) == ord('q'):
        break

# Close the serial connection and release the webcam
arduino.close()
webcam.release()
cv2.destroyAllWindows()

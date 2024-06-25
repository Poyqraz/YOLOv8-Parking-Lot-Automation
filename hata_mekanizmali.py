import serial
import time
import cv2
from ultralytics import YOLO
import numpy as np

# YOLOv8 model
model = YOLO('parklast.pt')

# Set up serial communication (COM port)
arduino = serial.Serial('COM4', 9600, timeout=1)

# Dosya yolu
dosya_yolu = 'carpark.mp4'

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
colors = [(178, 34, 34), (0, 255, 0)]  # Yeşil ve Mavi

# Nesne1 detection flag
bos_detected = False

threshold = 0.08  # Güven eşiği

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

    # Initialize the counter for "bos" objects
    bos_counter = 0

    def get_prefix(counter):
        if 0 <= counter < 20:
            return 'A'
        elif 20 <= counter < 40:
            return 'B'
        elif 40 <= counter < 60:
            return 'C'
        else:
            return 'D'  # 60'dan büyük değerler için varsayılan


    def check_collision(box1, box2):
        x1_min, y1_min, x1_max, y1_max, _ = box1  # Ignore the class value
        x2_min, y2_min, x2_max, y2_max, _ = box2  # Ignore the class value

        # Check if all corners of box1 are inside box2 or vice versa
        box1_in_box2 = x1_min >= x2_min and y1_min >= y2_min and x1_max <= x2_max and y1_max <= y2_max
        box2_in_box1 = x2_min >= x1_min and y2_min >= y1_min and x2_max <= x1_max and y2_max <= y1_max

        return box1_in_box2 or box2_in_box1


    # Process results (e.g., check for a specific class)
    boxes = []
    collision_boxes = []
    for result in results:
        if result.boxes is not None:
            for box in result.boxes:
                # Box nesnesinden koordinatları ve sınıf bilgisini çıkar
                xmin, ymin, xmax, ymax = box.xyxy[0].numpy()  # Koordinatları al
                cls = box.cls[0].numpy()  # Sınıf bilgisini al
                boxes.append((xmin, ymin, xmax, ymax, cls))  # Sınıf bilgisini de ekleyin

    # Check for collisions
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if check_collision(boxes[i], boxes[j]):
                # Draw a red rectangle around the collision area
                x_min = min(boxes[i][0], boxes[j][0])
                y_min = min(boxes[i][1], boxes[j][1])
                x_max = max(boxes[i][2], boxes[j][2])
                y_max = max(boxes[i][3], boxes[j][3])
                cv2.rectangle(frame, (int(x_min), int(y_min)), (int(x_max), int(y_max)), (238, 232, 170), 2)

                # Calculate the center of the collision box
                center_x = int((x_min + x_max) / 2)
                center_y = int((y_min + y_max) / 2)

                # Write the name "H" below the collision box
                cv2.putText(frame, "H", (center_x, center_y + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (238, 232, 170), 2)

                # Add the collision box to the list of collision boxes
                collision_boxes.append((x_min, y_min, x_max, y_max, boxes[i][4]))


    # Modify the check_collision function
    def check_collision(box1, box2):
        x1_min, y1_min, x1_max, y1_max, _ = box1  # Ignore the class value
        x2_min, y2_min, x2_max, y2_max, _ = box2  # Ignore the class value

        # Check if all corners of box1 are inside box2 or vice versa
        box1_in_box2 = x1_min >= x2_min and y1_min >= y2_min and x1_max <= x2_max and y1_max <= y2_max
        box2_in_box1 = x2_min >= x1_min and y2_min >= y1_min and x2_max <= x1_max and y2_max <= y1_max

        return box1_in_box2 or box2_in_box1


    # Modify the check_collision function
    def check_collision(box1, box2):
        x1_min, y1_min, x1_max, y1_max, _ = box1  # Ignore the class value
        x2_min, y2_min, x2_max, y2_max, _ = box2  # Ignore the class value

        # Check if all corners of box1 are inside box2 or vice versa
        box1_in_box2 = x1_min >= x2_min and y1_min >= y2_min and x1_max <= x2_max and y1_max <= y2_max
        box2_in_box1 = x2_min >= x1_min and y2_min >= y1_min and x2_max <= x1_max and y2_max <= y1_max

        return box1_in_box2 or box2_in_box1


    # Draw the detection boxes that are not inside or below a collision box
    for box in boxes:
        xmin, ymin, xmax, ymax, cls = box
        if not any(check_collision(box, collision_box) for collision_box in collision_boxes):
            # Sınıfa göre renk seç
            color = colors[int(cls)]  # Renk bilgisini al

            # Get the class name
            label = class_names[int(cls)]

            # Dikdörtgeni çiz
            cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), color, 1)

            # Sınıf adını yaz
            cv2.putText(frame, label, (int(xmin + (xmax - xmin) / 2 - len(label) * 3), int(ymin - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.41, (255, 255, 1), 1)

            if cls == 1:  # Assuming class 0 is "bos"
                bos_detected = True
                # Eğer son servo hareketinden itibaren belirli bir süre geçtiyse, servo motoru hareket ettir
                if (simdiki_zaman - son_servo_hareketi) > bekleme_suresi:
                    send_to_arduino('detected')
                    son_servo_hareketi = simdiki_zaman

                # Increase the counter for "bos" objects and assign a unique name
                bos_counter += 1
                prefix = get_prefix(bos_counter)
                bos_name = f"{prefix}{bos_counter}"

                # Write the unique name below the detection box
                cv2.putText(frame, bos_name, (int(xmin), int(ymax + 20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.38, (255, 255, 1), 1)

    # Nesne1 detection message
    if bos_detected:
        cv2.putText(frame, "Bos park alani tespit edildi", (int(frame.shape[1] / 2 - 100), int(frame.shape[0] - 40)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "A2 konumuna park ediniz", (int(frame.shape[1] / 2 - 100), int(frame.shape[0] - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    else:
        cv2.putText(frame, "Bos park alanı yoktur", (int(frame.shape[1] / 2 - 100), int(frame.shape[0] - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # Görüntüyü göster
    cv2.imshow('YOLOv8 Otopark Uygulaması', frame)

    # Eğer video dosyası ise ve 'q' tuşuna basılırsa döngüden çık
    if isinstance(kaynak, cv2.VideoCapture):
        if cv2.waitKey(1) == ord('q'):
            break
    else:
        cv2.waitKey(0)
        break

# Close the serial connection and release the resources
arduino.close()
if isinstance(kaynak, cv2.VideoCapture):
    kaynak.release()
cv2.destroyAllWindows()
import tkinter as tk
from tkinter import filedialog
import serial
import time
import cv2
from ultralytics import YOLO
import numpy as np

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

        # Set up serial communication (COM port)
        self.arduino = serial.Serial('COM4', 9600, timeout=1)
        # Son servo hareketinden bu yana geçen süreyi takip etmek için bir zaman damgası
        self.son_servo_hareketi = 0
        # Servo motorun son konumunda bekleyeceği süre (saniye cinsinden)
        self.bekleme_suresi = 10

    def create_widgets(self):
        self.load_model_button = tk.Button(self)
        self.load_model_button["text"] = "Model Yükle"
        self.load_model_button["command"] = self.load_model
        self.load_model_button.pack(side="top")

        self.load_video_button = tk.Button(self)
        self.load_video_button["text"] = "Video Yükle"
        self.load_video_button["command"] = self.load_video
        self.load_video_button.pack(side="top")

        self.start_button = tk.Button(self)
        self.start_button["text"] = "İşlemi Başlat"
        self.start_button["command"] = self.start_processing
        self.start_button.pack(side="top")

    def load_model(self):
        filename = filedialog.askopenfilename()
        self.model = YOLO(filename)

    def load_video(self):
        self.video_path = filedialog.askopenfilename()

    def send_to_arduino(self, message):
        self.arduino.write(message.encode())

    def start_processing(self):
        # Set up the class names and colors
        class_names = ['Dolu', 'bos']
        colors = [(255, 0, 0), (0, 255, 0)]  # Yeşil ve Mavi

        # Nesne1 detection flag
        bos_detected = False

        threshold = 0.06  # Güven eşiği

        # Video için döngü
        kaynak = cv2.VideoCapture(self.video_path) if self.video_path.endswith('.mp4') else cv2.imread(self.video_path)
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
            results = self.model.predict(frame, imgsz=800, conf=threshold)  # Doğrudan NumPy dizisini kullan

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

                        if cls == 0:  # Assuming class 0 is Nesne1
                            bos_detected = True
                            # Eğer son servo hareketinden itibaren belirli bir süre geçtiyse, servo motoru hareket ettir
                            if (simdiki_zaman - self.son_servo_hareketi) > self.bekleme_suresi:
                                self.send_to_arduino('detected')
                                self.son_servo_hareketi = simdiki_zaman

                    # Nesne1 detection message
                    if bos_detected:
                        cv2.putText(frame, "bos alan tespit edildi",
                                    (int(frame.shape[1] / 2 - 100), int(frame.shape[0] - 10)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    else:
                        cv2.putText(frame, "bos alan tespit edilmedi",
                                    (int(frame.shape[1] / 2 - 100), int(frame.shape[0] - 10)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)  # Kırmızı renk

                    # Görüntüyü göster
                    cv2.imshow('YOLOv8 Object Detection.Exe', frame)

                    # Eğer video dosyası ise ve 'q' tuşuna basılırsa döngüden çık
                    if isinstance(kaynak, cv2.VideoCapture):
                        if cv2.waitKey(1) == ord('q'):
                            break
                    else:
                        cv2.waitKey(0)
                        break

                # Close the serial connection and release the resources
                self.arduino.close()
                if isinstance(kaynak, cv2.VideoCapture):
                    kaynak.release()
                cv2.destroyAllWindows()

root = tk.Tk()
app = Application(master=root)
app.mainloop()

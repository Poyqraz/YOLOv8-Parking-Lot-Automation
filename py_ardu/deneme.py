import cv2
import serial
import time

ac = cv2.CascadeClassifier("plaka30.xml")
webcam = cv2.VideoCapture(1)

ardu = serial.Serial('com3', 9600)

# Son servo hareketinden bu yana geçen süreyi takip etmek için bir zaman damgası
son_servo_hareketi = 0
# Servo motorun son konumunda bekleyeceği süre (milisaniye cinsinden)
bekleme_suresi = 10000

while True:
    kontrol, cerceve = webcam.read()
    if not kontrol:
        print("Kamera görüntüsü alınamıyor.")
        break

    gri = cv2.cvtColor(cerceve, cv2.COLOR_BGRA2GRAY)
    sonuc = ac.detectMultiScale(gri, 1.1, 4)

    # Geçerli zamanı al
    simdiki_zaman = int(round(time.time() * 1000))

    for (x, y, genislik, yukseklik) in sonuc:
        cv2.putText(cerceve, "Plaka", (x - 5, y - 10), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
        cv2.rectangle(cerceve, (x, y), (x + genislik, y + yukseklik), (0, 0, 255), 4)

        # Eğer son servo hareketinden itibaren belirli bir süre geçtiyse, servo motoru hareket ettir
        if (simdiki_zaman - son_servo_hareketi) > bekleme_suresi:
            ardu.write(b'e')
            son_servo_hareketi = simdiki_zaman

    # Servo motorun son konumunda beklemesi gerekiyorsa, komut gönderme
    if (simdiki_zaman - son_servo_hareketi) <= bekleme_suresi:
        # Servo motorun son konumunda beklemesi için burada ekstra bir işlem yapmaya gerek yok
        pass

    if cv2.waitKey(10) == 27:
        break

    cv2.imshow("Plaka Tanıyıcı", cerceve)

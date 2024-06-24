import cv2
import serial

# İki kamera için CascadeClassifier nesneleri
ac1 = cv2.CascadeClassifier("mantar.xml")
ac2 = cv2.CascadeClassifier("mantar.xml")

# İki kamera için VideoCapture nesneleri
webcam1 = cv2.VideoCapture(1)  #  varsayılan kamera
webcam2 = cv2.VideoCapture(2)  #  ikinci kamera

# Arduino için seri bağlantı
##ardu = serial.Serial('com3', 9600)

while True:
    # Her iki kameradan da görüntüyü yakalama
    kontrol1, cerceve1 = webcam1.read()
    kontrol2, cerceve2 = webcam2.read()

    # Her iki görüntü için griye çevirme ve nesne tespiti
    if kontrol1 and kontrol2:
        gri1 = cv2.cvtColor(cerceve1, cv2.COLOR_BGR2GRAY)
        gri2 = cv2.cvtColor(cerceve2, cv2.COLOR_BGR2GRAY)
        sonuc1 = ac1.detectMultiScale(gri1, 1.1, 4)
        sonuc2 = ac2.detectMultiScale(gri2, 1.1, 4)
        ##ardu.write(b'a')  # Her iki kamera için de aynı komut gönderilmesi

        # İlk kamera için nesne tespiti ve işaretleme
        for (x, y, genislik, yukseklik) in sonuc1:
            cv2.putText(cerceve1, "Tespit Olumlu", (x-5, y-10), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
            cv2.rectangle(cerceve1, (x, y), (x+genislik, y+yukseklik), (0, 0, 255), 4)

        # İkinci kamera için nesne tespiti ve işaretleme
        for (x, y, genislik, yukseklik) in sonuc2:
            cv2.putText(cerceve2, "Tespit Olumlu", (x-5, y-10), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 3)
            cv2.rectangle(cerceve2, (x, y), (x+genislik, y+yukseklik), (0, 0, 255), 4)
            ##ardu.write(b'e')  # Nesne tespit edildiğinde Arduino'ya sinyal gönder

        # Görüntüleri göster
        cv2.imshow("Kamera 1", cerceve1)
        cv2.imshow("Kamera 2", cerceve2)

    # 'ESC' tuşuna basıldığında döngüden çık
    if cv2.waitKey(10) & 0xFF == 27:
        break

# Her şeyi serbest bırak
webcam1.release()
webcam2.release()
cv2.destroyAllWindows()

import cv2
import serial

ac=cv2.CascadeClassifier("plaka30.xml")
webcam=cv2.VideoCapture(3)

ardu=serial.Serial('com3',9600)

while True:
    kontrol,cerceve=webcam.read()
    gri=cv2.cvtColor(cerceve,cv2.COLOR_BGRA2GRAY)
    sonuc=ac.detectMultiScale(gri,1.1,4)
    ardu.write(b'a')

    for (x,y,genislik,yukseklik) in sonuc:
        cv2.putText(cerceve, "Plaka", (x-5,y-10), cv2.FONT_HERSHEY_COMPLEX,1 ,(0,0,255),3 )
        cv2.rectangle(cerceve,(x,y), (x+genislik,y+yukseklik), (0,0,255),4 )
        ardu.write(b'e')
    if cv2.waitKey(10)==27:
        break
    cv2.imshow("ac",cerceve)
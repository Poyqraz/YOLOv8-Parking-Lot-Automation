import cv2
webcam=cv2.VideoCapture(1)
sayac=1
while sayac<=120:
    kontrol,cerceve=webcam.read()
    gri=cv2.cvtColor(cerceve,cv2.COLOR_BGR2GRAY)
    if cv2.waitKey(10)==27:
        break

    cv2.imshow("Webcam",gri)
    cv2.imwrite("n"+str(sayac)+".jpg",gri)
    cv2.waitKey(0)
    sayac+=1
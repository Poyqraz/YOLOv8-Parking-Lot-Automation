import serial

ardu=serial.Serial('com3', 9600)
while True:
    islem=input("A=yak, E=sondur:")
    if (islem=="a"):
        ardu.write(b'a')
    elif (islem=="e"):
        ardu.write(b'e')
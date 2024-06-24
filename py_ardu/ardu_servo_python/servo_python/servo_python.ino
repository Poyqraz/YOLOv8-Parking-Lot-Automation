#include <Servo.h>

char python;
Servo myServo;
bool objectDetected = false;  // Nesne tespit edildi mi?

void setup() {
  Serial.begin(9600);
  myServo.attach(2);
}

void loop() {
  if (Serial.available() > 0) {
    python = Serial.read();
    if (python == 'a') {
      objectDetected = true;  // Nesne tespit edildi
      myServo.write(90);  // Servo motoru 90 dereceye döndür
    } else if (python == 'e') {
      myServo.write(180);
      objectDetected = false;  // Nesne tespit edilmedi
    }
  }
}


char python;
void setup() {

Serial.begin(9600);

pinMode(2,OUTPUT);


}

void loop() {
  
  if(Serial.available()>0) {
    python=Serial.read();
    if (python=='a') {
      digitalWrite(2, HIGH);
    }

    else if (python=='e'){

      digitalWrite(2, LOW);
    }

  } 

}

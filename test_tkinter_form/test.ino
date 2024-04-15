#include <Servo.h>

Servo servo;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  servo.attach(3);
  servo.write(0);
}

void loop() {
  // put your main code here, to run repeatedly:
  if(Serial.available()){
    int num = Serial.parseInt();
    Serial.println(num);
    servo.write(num);
    delay(3000);
    }
}
#include <Arduino.h>
#include <HardwareSerial.h>

char ack_phrase[] = "\x06" "\x30" "\x35" "\x30" "\x0D" "\x0A";//<ACK>050\r\n
char eol = '\x0A';

HardwareSerial SerialPort2(2); //UART 2 - RX:16, TX:17
  
void setup() {
  Serial.begin(115200);
  delay(100);
  Serial.println("setup()");
  SerialPort2.begin(300,SERIAL_7E1,16,17);
}

void loop() {
  Serial.println("loop");
  
  SerialPort2.print("/?!\r\n"); //sent wake up signal, mt174 should send identifier afterwards
  delay(200);
  bool found_id = false;
  
  if (SerialPort2.available())
  {
    while (!found_id)
    {
      String data = SerialPort2.readStringUntil(eol);
      Serial.println("received: " + data);
  
      if (data.startsWith("/ISk5MT174-0001")) //identifier
      {
        Serial.println("got identifier");
        delay(100);
        
        Serial.println("sending ACK");
        SerialPort2.print(ack_phrase); // ack
        Serial.println("updating baud rate");
        SerialPort2.flush();
        SerialPort2.end();
        found_id = true;
        delay(200);
      }
    }
   }
  
  //communication with new baud rate
  SerialPort2.begin(9600,SERIAL_7E1,16,17);
  while (true)
  {
    if (SerialPort2.available())
    {
      String data = SerialPort2.readStringUntil(eol);
      Serial.println("received: " + data);
   }
  }
}
int i = 0;
String sensors[] = { "T", "P" }; // thermistor, pressure sensor

void setup()
{
  Serial.begin(115200);
//  Serial.write("[Arduino] Setting up serial...");
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
//  Serial.print("[Arduino] Serial Configured!");
  randomSeed(analogRead(0));
}


void loop()
{
  long randomSensor = random(2);
  Serial.print(sensors[randomSensor]);
  Serial.println(i);
  i++;
  long randNumber = 500 + random(501);
  delay(randNumber);  
}

//char dataString[50] = {0};
//int a = 0; 
//
//void setup() {
//Serial.begin(115200);              //Starting serial communication
//}
//
//
//void loop() {
//  a++;                          // a value increase every loop
//  sprintf(dataString,"%02X",a); // convert a value to hexa 
//  Serial.println(dataString);   // send the data
//  delay(1000);                  // give the loop some break
//}

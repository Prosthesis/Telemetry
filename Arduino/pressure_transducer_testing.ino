// which analog pin to connect
#define PRESSUREPIN A0 
// how many samples to take and average, more takes longer 
// but is more 'smooth'
#define NUMSAMPLES 5

void setup(void) 
{
  Serial.begin(115200);
}

void loop(void) 
{
  uint8_t i;
  float average = 0;
  
  // take N samples in a row, with a slight delay
  for (i=0; i< NUMSAMPLES; i++) 
  {
    average += analogRead(PRESSUREPIN);
    delay(10);
  }
 
  average /= NUMSAMPLES;
  
  // read pressure sensor
  // convert to psi based off of observed behavior with sensor
  // and bicycle pump
  float pressure1 = (average - 114) * 10; 
  Serial.print("P:");
  Serial.println(pressure1);
  
 
  delay(1000);
}

//00psi = 114-115
//20psi = 116-117
//40psi = 118-119
//60psi = 119-120
//65psi = 119-121
//80psi = 122
//85psi = 122-123
//105psi= 124-125


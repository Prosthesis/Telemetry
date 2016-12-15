// which analog pin to connect
#define PRESSUREPIN A0 
// which analog pin to connect
#define THERMISTORPIN A0    
// how many samples to take and average, more takes longer 
// but is more 'smooth'
#define NUMSAMPLES 5
#define THERMISTORNOMINAL 10000 // 10,000 ohms; resistance @ room temp C (we assume 25 is the room temp) 
#define TEMPERATURENOMINAL 25 // almost always 25 C
// The beta coefficient of the thermistor (usually 3000-4000)
#define BCOEFFICIENT 3984 // taken from data sheet for part
#define SERIESRESISTOR 10000 // the value of the fixed resistor

void setup(void) 
{
  Serial.begin(115200);
}


float readTemp(int pin)
{
  uint8_t i;
  float average = 0;
 
  // take N samples in a row, with a slight delay
  for (i=0; i< NUMSAMPLES; i++) 
  {
    average += analogRead(pin);
    delay(10);
  }
  
  average /= NUMSAMPLES;
 
  // convert the value to resistance
  average = 1023 / average - 1;
  average = SERIESRESISTOR / average;

 
  float steinhart = 0;
  steinhart = average / THERMISTORNOMINAL;     // (R/Ro)
  steinhart = log(steinhart);                  // ln(R/Ro)
  steinhart /= BCOEFFICIENT;                   // 1/B * ln(R/Ro)
  steinhart += 1.0 / (TEMPERATURENOMINAL + 273.15); // + (1/To)
  steinhart = 1.0 / steinhart;                 // Invert
  steinhart -= 273.15;                         // convert to C
 
  /*
  Serial.print("Temperature "); 
  Serial.print(steinhart);
  Serial.println(" *C");
  */
  return steinhart;
}

float readPressure(int pin)
{
  uint8_t i;
  float average = 0;
  
  // take N samples in a row, with a slight delay
  for (i=0; i< NUMSAMPLES; i++) 
  {
    average += analogRead(pin);
    delay(10);
  }
   
   average /= NUMSAMPLES;
   // convert to psi based off of observed behavior with sensor
  // and bicycle pump
   return (average - 114) * 10;
}

void loop(void) 
{
  float thermistor1 = readTemp(THERMISTORPIN);
  Serial.print("T:");
  Serial.println(thermistor1);
  
  float pressure1 = readPressure(PRESSUREPIN);
  Serial.print("P:");
  Serial.println(pressure1);
  
 
  delay(1000);
}


unsigned long highTime;    //integer for storing high time
unsigned long lowTime;     //integer for storing low time
float avg_p;    // integer for storing period
float freq;      //storing frequency
int itr = 10;

void setup()
{
    pinMode(11,INPUT);  //Setting pin as input
    Serial.begin(9600);
    
}

void loop()
{
    avg_p = 0;
    for (int i=0; i < itr; i++){
      highTime=pulseIn(11,HIGH,250000);  //read high time
      lowTime=pulseIn(11,LOW,250000);    //read low time
      /*
      Serial.print("H:");
      Serial.print(highTime);
      Serial.print("  L:");
      Serial.print(lowTime);
      Serial.print("\n");
      */
      avg_p += highTime;
      avg_p += lowTime; // Period = Ton + Toff
    }
    avg_p /= itr;
    
    if (avg_p == 0 || avg_p > 59880){ //if no signal received or if frequency too low
      Serial.println(0); // flowrate is 0
    }
    else{
      freq = 1000000/avg_p;       //getting frequency with totalTime is in Micro seconds
      freq /= 16.7; //freq stores flow rate
      if (freq > 1000){
        Serial.println(0);
      }
      else{
        Serial.println(freq);
      }
    }
}

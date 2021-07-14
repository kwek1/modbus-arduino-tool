float sml = 0;
float big = 0;
float avg = 0;
int itr = 600; //average values across itr samples
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(A0, INPUT); //smaller flowmeter
  pinMode(A1, INPUT); //larger flowmeter
}

void loop() {
  // put your main code here, to run repeatedly:
  sml = analogRead(A0) * 0.049;
  avg = 0;
  for (int i = 0; i < itr; i++){
    if (sml < 50){
      sml = analogRead(A0) * 0.049;
      avg += sml;
    }
    else{
      big = analogRead(A1) * 0.98;
      avg += analogRead(A1);
    }
  }
  Serial.println(avg/itr);
  //delay(1000);
}

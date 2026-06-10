const float R_REF = 330.0;
const float V_CC = 5.0;

void setup() {
  Serial.begin(9600);
  Serial.println("=== TEST DE CONEXION ===");
  Serial.println("R_ref = 120 ohm");
  Serial.println("------------------------");
}

void loop() {
  int raw = analogRead(A0);
  float v_out = raw * (V_CC / 1023.0);
  float r_muestra = R_REF * v_out / (V_CC - v_out);

  Serial.print("RAW: ");
  Serial.print(raw);
  Serial.print("  |  V_out: ");
  Serial.print(v_out, 3);
  Serial.print(" V  |  R_muestra: ");
  Serial.print(r_muestra, 1);
  Serial.println(" ohm");

  delay(500);
}
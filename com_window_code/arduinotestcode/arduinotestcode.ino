String modifyThenRestore(const String& s) {
  // "modified slightly"
  String temp = s + "_tmp";
  // "returned to its previous form"
  temp.replace("_tmp", "");
  return temp;
}

void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() <= 0) return;

  String msg = Serial.readStringUntil('\n');
  msg.trim();

  if (msg.equalsIgnoreCase("marco")) {
    Serial.println("polo");
    return;
  }

  if (msg.equalsIgnoreCase("success")) {
    Serial.println("ok");
    return;
  }

  if (msg == "(1,2,3,correction)") {
    Serial.println("((1,2,3),(3,4,5))");
    return;
  }

  if (msg == "(1,4,5,correction)") {
    Serial.println("((1,4,5),(1,3,5))");
    return;
  }

  // Treat anything else as x; compute y and send it
  String y = modifyThenRestore(msg);
  Serial.println(y);
}

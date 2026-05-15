const int btn_cw   = 2;
const int btn_ccw  = 3;
const int btn_stop = 4;

const int pwmPin   = 5;
const int relayPin = 6;

int currentSpeed = 0;
int targetSpeed  = 0;
bool currentDir  = true;

const int RAMP_STEP  = 5;
const int RAMP_DELAY = 15;

void rampDown() {
  targetSpeed = 0;
  while (currentSpeed > 0) {
    currentSpeed = max(0, currentSpeed - RAMP_STEP);
    analogWrite(pwmPin, currentSpeed);
    delay(RAMP_DELAY);
  }
  Serial.println("[RAMP] 降速完成，currentSpeed=0");
}

void setDirection(bool cw) {
  if (currentDir != cw) {
    Serial.print("[DIR] 換向中... 先降速 → ");
    rampDown();
    currentDir = cw;
    digitalWrite(relayPin, cw ? HIGH : LOW);
    Serial.print("繼電器設為 ");
    Serial.println(cw ? "HIGH（正轉）" : "LOW（反轉）");
    delay(50);
  }
}

void setup() {
  Serial.begin(9600);
  Serial.println("=== 馬達控制除錯模式啟動 ===");

  pinMode(btn_cw,   INPUT_PULLUP);
  pinMode(btn_ccw,  INPUT_PULLUP);
  pinMode(btn_stop, INPUT_PULLUP);
  pinMode(pwmPin,   OUTPUT);
  pinMode(relayPin, OUTPUT);
  digitalWrite(relayPin, LOW);

  // 啟動時讀一次腳位初始狀態
  Serial.print("[INIT] btn_cw(D2)=");   Serial.println(digitalRead(btn_cw));
  Serial.print("[INIT] btn_ccw(D3)=");  Serial.println(digitalRead(btn_ccw));
  Serial.print("[INIT] btn_stop(D4)="); Serial.println(digitalRead(btn_stop));
  Serial.print("[INIT] pwmPin(D5)=");   Serial.println(pwmPin);
  Serial.print("[INIT] relayPin(D6)="); Serial.println(relayPin);
  Serial.println("========================");
}

// 每 500ms 印一次狀態
unsigned long lastPrint = 0;

void loop() {
  bool cw   = (digitalRead(btn_cw)   == LOW);
  bool ccw  = (digitalRead(btn_ccw)  == LOW);
  bool stop = (digitalRead(btn_stop) == LOW);

  // 按鈕狀態
  if (cw) {
    Serial.println("[BTN] 正轉按下");
    setDirection(true);
    targetSpeed = 200;
  } else if (ccw) {
    Serial.println("[BTN] 反轉按下");
    setDirection(false);
    targetSpeed = 200;
  } else if (stop) {
    Serial.println("[BTN] 停止按下");
    rampDown();
    targetSpeed = 0;
  }

  // 緩速追蹤
  if (currentSpeed < targetSpeed) {
    currentSpeed = min(targetSpeed, currentSpeed + RAMP_STEP);
    analogWrite(pwmPin, currentSpeed);
    delay(RAMP_DELAY);
  } else if (currentSpeed > targetSpeed) {
    currentSpeed = max(targetSpeed, currentSpeed - RAMP_STEP);
    analogWrite(pwmPin, currentSpeed);
    delay(RAMP_DELAY);
  }

  // 每 500ms 印一次目前狀態（不管有沒有按鈕）
  if (millis() - lastPrint >= 500) {
    lastPrint = millis();
    Serial.print("[STATUS] dir=");
    Serial.print(currentDir ? "正轉" : "反轉");
    Serial.print("  relay=");
    Serial.print(digitalRead(relayPin) ? "HIGH" : "LOW");
    Serial.print("  currentSpeed=");
    Serial.print(currentSpeed);
    Serial.print("  targetSpeed=");
    Serial.print(targetSpeed);
    Serial.print("  btn_cw=");
    Serial.print(!digitalRead(btn_cw));
    Serial.print("  btn_ccw=");
    Serial.print(!digitalRead(btn_ccw));
    Serial.print("  btn_stop=");
    Serial.println(!digitalRead(btn_stop));
  }
}

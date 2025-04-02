#include "HX711.h"
#include "Wire.h"
#include "Adafruit_GFX.h"
#include "Adafruit_SSD1306.h"

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET     -1  // Reset pin non usato con I2C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

const int LOADCELL_DOUT_PIN = 2;
const int LOADCELL_SCK_PIN = 3;

float calibration_factor = -0.425;
float units;
float ounces;

HX711 scale;

void setup() {
  Serial.begin(9600);
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("Display OLED non trovato"));
    for (;;); // Blocca tutto
  }

  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("Calibrazione...");
  display.display();

  long zero_factor = scale.read_average();
  Serial.print("Zero factor: ");
  Serial.println(zero_factor);
}

void loop() {
  scale.set_scale(calibration_factor);

  int numReadings = 0;
  float sum = 0;
  unsigned long startTime = millis();

  while (millis() - startTime < 500) {
    units = scale.get_units(1);
    if (units < 0) units = 0.0;
    ounces = (units / 1000);
    sum += ounces;
    numReadings++;
  }

  float averageOunces = sum / numReadings;
  Serial.println(averageOunces);

  // Mostra su OLED
  display.clearDisplay();
  display.setTextSize(2);
  display.setCursor(0, 0);
  display.print("Peso:");

  display.setCursor(0, 30);
  display.setTextSize(3);
  display.print(averageOunces, 2);
  display.setTextSize(2);
  display.print(" kg");

  display.display();
  Serial.println(averageOunces);

  if (Serial.available()) {
    char temp = Serial.read();
    if (temp == '+' || temp == 'a') {
      calibration_factor += 0.001;
    } else if (temp == '-' || temp == 'z') {
      calibration_factor -= 0.001;
    }
  }
}

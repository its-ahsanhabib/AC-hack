byte REQ[] = {
  0xBB, 0x00, 0x01, 0x03, 0x1D, 0x00, 0x00, 0x64, 0x03, 0x55, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x96
};
// BB 00 01 04 02 01 00 BDn
// BB 00 01 04 02 01 00 BD


#define AIRCON_SERIAL_BAUD 9600

#define DEBUG Serial
#define AIRCON Serial1  // 18-TX1, 19-RX1
#define AC_RX Serial2   // 16-TX2, 17-RX2
#define AC_TX Serial3   // 14-TX3, 15-RX3

void setup() {
  // pinMode(0, INPUT);
  DEBUG.begin(115200);
  AIRCON.begin(AIRCON_SERIAL_BAUD);  // 18-TX1, 19-RX1
  AC_TX.begin(AIRCON_SERIAL_BAUD,SERIAL_8E1);   // 14-TX3, 15-RX3
  AC_RX.begin(AIRCON_SERIAL_BAUD);   // 16-TX2, 17-RX2

  DEBUG.println("################## Code Started ##################");

  DEBUG.println("REQ STATUS : ");
  for (int i = 0; i < sizeof(REQ); i++) {
    AIRCON.write(REQ[i]);
  }
}

void loop() {
  if (DEBUG.available() > 0) {
    DEBUG.print("DBG CMD:");
    delay(50);
    DEBUG.print("=>");
    String dbg_cmd = DEBUG.readStringUntil('\n');
    DEBUG.print(dbg_cmd + "<> ");
    if (dbg_cmd == "r") {
      DEBUG.print("Request for data Sending");
      for (int i = 0; i < sizeof(REQ); i++) {
        AC_TX.write(REQ[i]);
      }
    }
    DEBUG.println();
  }


  if (AC_TX.available() > 0) {
    DEBUG.print("AC TX:");
    delay(75);
    int byte = 0;
    DEBUG.print(AC_TX.available());
    DEBUG.print("=>");
    while (AC_TX.available()) {
      byte = AC_TX.read();
      DEBUG.print(byte < 16 ? "0" : "");
      DEBUG.print(byte, HEX);
      DEBUG.print(' ');
    }
    DEBUG.println();
  }

  if (AC_RX.available() > 0) {
    DEBUG.print("AC RX:");
    delay(50);
    int byte = 0;
    DEBUG.print(AC_RX.available());
    DEBUG.print("=>");
    while (AC_RX.available()) {
      byte = AC_RX.read();
      DEBUG.print(byte < 16 ? "0" : "");
      DEBUG.print(byte, HEX);
      DEBUG.print(' ');
    }
    DEBUG.println();
  }
}

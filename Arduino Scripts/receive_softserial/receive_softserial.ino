#include <mcp_can.h>
#include <SPI.h>
#include <SoftwareSerial.h>

long unsigned int rxId;
unsigned char len = 0;
unsigned char rxBuf[8];

MCP_CAN CAN0(10);                               // Set CS to pin 10

SoftwareSerial mySerial(4, 5); // RX, TX

void setup()
{
  mySerial.begin(9600);
  CAN0.begin(CAN_500KBPS);                       // init can bus : baudrate = 500k 
  pinMode(2, INPUT);                            // Setting pin 2 for /INT input
  mySerial.println("MCP2515 Library Receive Example...");
}

void loop()
{
    if(!digitalRead(2))                         // If pin 2 is low, read receive buffer
    {
      CAN0.readMsgBuf(&len, rxBuf);              // Read data: len = data length, buf = data byte(s)
      rxId = CAN0.getCanId();                    // Get message ID
      mySerial.print("ID: ");
      mySerial.print(rxId, HEX);
      mySerial.print("  Data: ");
      for(int i = 0; i<len; i++)                // Print each byte of the data
      {
        if(rxBuf[i] < 0x10)                     // If data byte is less than 0x10, add a leading zero
        {
          mySerial.print("0");
        }
        mySerial.print(rxBuf[i], HEX);
        mySerial.print(" ");
      }
      mySerial.println();
    }
}


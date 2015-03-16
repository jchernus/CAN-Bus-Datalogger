#include <mcp_can.h>
#include <SPI.h>
#include <FileIO.h>
#include <Wire.h> //I2c Library
#include "RTClib.h"

RTC_DS1307 rtc;
MCP_CAN CAN0(10);                               // Set CS to pin 10

//variables used to read from CAN Bus
long unsigned int rxId;
unsigned char len = 0;
unsigned char rxBuf[8];
char filename[] = "/mnt/sda1/datalog.txt";

//variables used to process data
uint8_t counter = 0;

//all of the variables of interest
byte CAN_data[22];

void setup()
{
  Serial.begin(9600);

  Bridge.begin();
  FileSystem.begin();

  CAN0.begin(CAN_500KBPS); // init can bus : baudrate = 500k
  pinMode(2, INPUT); // Setting pin 2 for /INT input
  Serial.println("MCP2515 Library Receive Example...");

  //  Wire.begin();
  //  rtc.begin();
  //  Serial.println("RTC starting");
  //  if (! rtc.isrunning()) {
  //    Serial.println("RTC is NOT running!");
  //  }
}

void loop()
{
  //If 1 second has passed, write variables to log
  if (true)
  {
    String dataString = ""; // string used to store data to be logged
    //dataString += getTimeStamp();

    //Write first 18 variables to log
    for (int i = 0; i <= 21; i++)
    {
      dataString += CAN_data[i];
    }

    // open file
    File dataFile = FileSystem.open(filename, FILE_APPEND);

    // write to log
    if (dataFile)
  {
    dataFile.println(dataString);
      dataFile.close();
    }
    else // error
    {
      Serial.print("Error opening ");
      Serial.println(filename);
    }
    counter += 1; // advance counter that is used to measure 30 seconds
  }

  if (!digitalRead(2)) // If pin 2 is low, read receive buffer
  {
    CAN0.readMsgBuf(&len, rxBuf); // Read data: len = data length, buf = data byte(s)
    rxId = CAN0.getCanId(); // Get message ID

    if (String(rxId, HEX) == "477" || String(rxId, HEX) == "475" || String(rxId, HEX) == "270" || String(rxId, HEX) == "294" || String(rxId, HEX) == "306")
    {
      Serial.print(", ID: ");
      Serial.print(rxId, HEX);
      Serial.print(", Data: ");

      if (String(rxId, HEX) == "477")
      {
        for (int i = 0; i < 4; i++) // Print the 1-second interval bytes
        {
          if (rxBuf[i] < 0x10) // If data byte is less than 0x10, add a leading zero
          {
            CAN_data[i] = rxBuf[i];
            Serial.print("0");
          }
          Serial.print(rxBuf[i], HEX);
          Serial.print(" ");
        }
        for (int i = 4; i < 7; i++) // Print the 30-second interval bytes
        {
          if (rxBuf[i] < 0x10)
          {
            CAN_data[i+14] = rxBuf[i];
            Serial.print("0");
          }
          Serial.print(rxBuf[i], HEX);
          Serial.print(" ");
        }
      }
      else if (String(rxId, HEX) == "475")
      {
        for (int i = 0; i < 7; i++)
        {
          if (rxBuf[i] < 0x10)
          {
            CAN_data[i+14] = rxBuf[i];
            Serial.print("0");
          }
          Serial.print(rxBuf[i], HEX);
          Serial.print(" ");
        }
      }
      else if (String(rxId, HEX) == "270")
      {
        
      }
      else if (String(rxId, HEX) == "294")
      {
        
      }
      else if (String(rxId, HEX) == "306")
      {
        
      }
      Serial.println("");
    }
  }
}

String getTimeStamp()
{
  DateTime now = rtc.now();
  String time = "";

  time = String(now.month()) + "/" + String(now.day()) + "/" + String(now.year()) + " " + String(now.hour()) + ":" + String(now.minute()) + "." + String(now.second());

  return time;
}

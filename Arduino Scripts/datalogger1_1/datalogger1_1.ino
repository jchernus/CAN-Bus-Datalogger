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
char filename[] = "/mnt/sda1/";

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

    //Write first 18 variables to Serial
    for (int i = 0; i <= 21; i++)
    {
      if (CAN_data[i] < 0x10)
      {
        Serial.print("0");
      }
      Serial.print(CAN_data[i], HEX);
      Serial.print(" ");
    }

    // open file
    ("/mnt/sda1/" + getDate() + ".txt").toCharArray(filename, 21); //getDate computes the date in YYMMMDD format
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
      String time = getTimeStamp();
      Serial.print(time);
      Serial.print(", ID: ");
      Serial.print(rxId, HEX);
      Serial.print(", Data: ");

      if (String(rxId, HEX) == "477")
      {
        for (int i = 0; i < 4; i++) // Print the 1-second interval bytes
        {
          CAN_data[i] = rxBuf[i];
        }
        for (int i = 4; i < 7; i++) // Print the 30-second interval bytes
        {
          CAN_data[i + 14] = rxBuf[i];
        }
      }
      else if (String(rxId, HEX) == "475")
      {
        CAN_data[4] = rxBuf[0];
        CAN_data[5] = rxBuf[1];
        CAN_data[21] = rxBuf[5];
        CAN_data[6] = rxBuf[6];
        CAN_data[7] = rxBuf[7];
      }
      else if (String(rxId, HEX) == "270")
      {
        CAN_data[8] = rxBuf[6];
        CAN_data[9] = rxBuf[7];
      }
      else if (String(rxId, HEX) == "294")
      {
        CAN_data[10] = rxBuf[6];
        CAN_data[11] = rxBuf[7];
      }
      else if (String(rxId, HEX) == "306")
      {
        CAN_data[12] = rxBuf[2];
        CAN_data[13] = rxBuf[3];
        CAN_data[14] = rxBuf[4];
        CAN_data[15] = rxBuf[5];
        CAN_data[16] = rxBuf[6];
        CAN_data[17] = rxBuf[7];
      }

      //Just for debugging purposes
      for (int i = 0; i < len; i++)
      {
        if (rxBuf[i] < 0x10)
        {
          Serial.print("0");
        }
        Serial.print(rxBuf[i], HEX);
        Serial.print(" ");
      }
    }
  }
}

String getTimeStamp()
{
  DateTime now = rtc.now();
  String time = String(now.hour()) + ":" + String(now.minute()) + ":" + String(now.second());
  return time;
}

String getDate()
{
  DateTime now = rtc.now();

  String date = "";
  date += String(now.year()).substring(0, 2);

  int month = now.month();
  if (month == 1)
  {
    date += "JAN";
  }
  else if (month == 2) {
    date += "FEB";
  }
  else if (month == 3) {
    date += "MAR";
  }
  else if (month == 4) {
    date += "APR";
  }
  else if (month == 5) {
    date += "MAY";
  }
  else if (month == 6) {
    date += "JUN";
  }
  else if (month == 7) {
    date += "JUL";
  }
  else if (month == 8) {
    date += "AUG";
  }
  else if (month == 9) {
    date += "SEP";
  }
  else if (month == 10) {
    date += "OCT";
  }
  else if (month == 11) {
    date += "NOV";
  }
  else if (month == 12) {
    date += "DEC";
  }

  String day = String(now.day());
  if (day.length() == 1) day = "0" + day;
  date += day;

  return date;
}

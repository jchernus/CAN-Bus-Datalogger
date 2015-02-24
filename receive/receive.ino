#include <mcp_can.h>
#include <SPI.h>
#include <FileIO.h>

long unsigned int rxId;
unsigned char len = 0;
unsigned char rxBuf[8];
char filename[] = "/mnt/sd/datalog.txt";

MCP_CAN CAN0(10);                               // Set CS to pin 10

void setup()
{  
  Serial.begin(9600);
  
  Bridge.begin();
  FileSystem.begin();
  
  CAN0.begin(CAN_500KBPS); // init can bus : baudrate = 500k 
  pinMode(2, INPUT); // Setting pin 2 for /INT input
  Serial.println("MCP2515 Library Receive Example...");
}

void loop()
{
  String dataString = "";
  dataString += "<Time stamp>";
  dataString += ", ID: ";
  
    if(!digitalRead(2)) // If pin 2 is low, read receive buffer
    {
      CAN0.readMsgBuf(&len, rxBuf); // Read data: len = data length, buf = data byte(s)
      rxId = CAN0.getCanId(); // Get message ID
      dataString += String(rxId, HEX);
      dataString += ", Data: ";
      
      for(int i = 0; i<len; i++) // Print each byte of the data
      {
        if(rxBuf[i] < 0x10) // If data byte is less than 0x10, add a leading zero
        {
          dataString += "0";
        }
        dataString += String(rxBuf[i], HEX);
        dataString += " ";
      }
      
      File dataFile = FileSystem.open(filename, FILE_APPEND);

      if (dataFile) // if the file is available, write to it:
      {
        dataFile.println(dataString);
        dataFile.close();
      }
      else // if the file isn't open, pop up an error:
      {
        Serial.println("Error opening datalog.txt");
      }
      
      // print to the serial port too:
      Serial.println(dataString);
    }
}

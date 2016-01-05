# CAN-Bus-Datalogger
CAN Bus Datalogger

This project uses an embedded computer running Linux as a platform for a CAN-Bus Data Logger and Diagnostic Tool. In my case, I am using the device with proprietary vehicles that my company produces for underground mining applications, but the code can easily be modified to support other vehicles, robots, or automation devices.

I use two different sets of hardware - hobby (for testing) and industrial. I will outline and reference the hobbyist hardware here, as it is more likely to be relevant for the average reader.

• An embedded computer running Linux - Raspberry Pi 2 will do.
• MicroSD card to host the OS and files.
• A Pi-CAN board from SK Pang Electronics. This board houses a Microchip MCP2515 CAN controller and MCP2551 CAN transceiver for all of our CAN communication needs.
• A Real Time Clock. I've been using the DS1307 from Adafruit.
• A Wi-Fi Dongle, also from Adafruit.

I use can-utils (http://elinux.org/Can-utils), which is a set of open source CAN drivers and a networking stack created by Volkswagen (thanks!) for the Linux kernel. 

For data logging needs, I simply listen to a subset of messages that are cyclically transmitted on the CAN Bus and parse them for the information that I desire. 

To create the diagnostic functionality, I send SDOs on the canbus requesting specific data. Depending on the device I am communicating with, the communication protocol differs (ex. Sevcon needs a password to release certain data, the Orion BMS will send you more messages, but only if you respond to it's first one in 500ms, etc.).

I rely on a number of packages and tools to get the hardware and code running. Included is an Excel document called Commands which houses some important information about getting your image of Linux setup to a working configuration.

Hopefully this code will help get you started on CAN Bus logging/diagnostics/hacking. :-)

# CircuitPython Documentation

## About the board

The specifications for the Raspberry Pi Pico used in the project can be found [here](https://www.raspberrypi.com/products/raspberry-pi-pico/). For the Trinket M0, it is [here](https://www.adafruit.com/product/3500).

The version of CircuitPython flashed on the board is 8.2.9.

For Raspberry Pi Pico, pin 1 and 2 is used as UART Tx and Rx respectively. Pin 37 and 38 is used as 3.3V power and Ground respectively.
<figure>
    <img src="/assets/picopinout.png" width="800" height="800"
         alt="Pico pinout">
    <figcaption>Raspberry Pi Pico pinout. Source: <a href="https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html">Raspberry Pi Pico Documentation</a> </figcaption>
</figure>

For Trinket M0, pin 3 and 4 is used as UART Rx and Tx respectively. 3V and GND pin is used as their name suggested.
<figure>
    <img src="/assets/m0pinout.png" width="800" height="800"
         alt="Trinket M0 pinout">
    <figcaption>Trinket M0 pinout. Source: <a href="https://learn.adafruit.com/adafruit-trinket-m0-circuitpython-arduino/pinouts">Learn Adafruit website</a> </figcaption>
</figure>

## Code Acknowledgement

```code.py``` and ```custom_finger_lib.py``` are heavily referenced from Adafruit CircuitPython Fingerprint github page ([Python](https://github.com/adafruit/Adafruit_CircuitPython_Fingerprint/tree/main) and [C++](https://github.com/adafruit/Adafruit-Fingerprint-Sensor-Library/tree/master)), more specifically examples/fingerprint_r503.py and examples/fingerprint_template_file_compare.py, while ```adafruit_fingerprint_reduced.py``` is a copy from adafruit_fingerprint.py with unused functions removed. adafruit_fingerprint.cpp was also useful for listing all the possible error codes the sensor can return when using the functions in the library. Credit to the respective authors of these library codes.

## Python Code

### Set up connection with fingerprint sensor

The code will first setup the connection with the fingerprint sensor by scanning the baudrate the sensor is currently set to. It will then change the baudrate of the sensor to 115200 for best data transfer speed and reset the connection one last time. Finally, we will go into our main loop.

If the code cannot establish connection with the sensor, the code would simply end.

    Code done running.

    Press any key to enter the REPL. Use CTRL-D to reload.

### Calling Functions

Dart code can call functions by sending

    "[Command]" + " "(Optional) + "[Argument]"(Optional) + "\n" + "\r"

when prompted with ">" from the Python code. The code python receive this by calling input() with usb_cdc imported.

"\n" signals that this is the end of the user input for input(). "\r" signals this is the end of the data so input() can start reading from the serial port.

**Important**: usb_cdc allows the python code to treat the usb connection as a console/terminal, so print() and input() will automatically work on the serial port without the need for any specialise serial read/write functions.

**Format**: >[Command] [Argument]   (Only when dart code is used as a command line interface)

**Type**:

* Command: *String* from '1' to '6'
* Argument (optional): *String* from '1' to '120'

### code.py API

#### Command '1' - Enroll fingerprint in slot "Argument"

Input: >1 "slot number"

Output:

    >1 1
    1 1
    FINGERREQUEST     #Request User to press finger on sensor
    FINGERHOLD        #Request User to hold finger on sensor
    OKIMAGE           #Image taken successfully
    TEMPLATING        #Converting image to template
    OKTEMPLATE        #Image converted to template successfully
    REMOVEFINGER      #Request User to remove finger off sensor
    FINGERREQUEST     #Request User to press finger on sensor
    FINGERHOLD        #Request User to hold finger on sensor
    OKIMAGE           #Image taken successfully
    TEMPLATING        #Converting image to template
    OKTEMPLATE        #Image converted to template successfully
    CREATEMODEL       #Create Model from template for storage
    OKMODEL           #Create Model successfully
    STOREMODEL        #Storing model on sensor flash memory
    OKSTORAGE         #Model stored successfully
    READTEMPLATE 1 2  #Display all models stored on sensor by listing its slot. Currently in slot 1 and slot 2.
    >                 #Command/Input request

#### Command '2' - Identify fingerprint

Input: >2

Output:

    READTEMPLATE 1 2
    >2
    FINGERREQUEST     #Request User to press finger on sensor
    FINGERHOLD        #Request User to hold finger on sensor
    OKIMAGE           #Image taken successfully
    TEMPLATING        #Converting image to template
    OKTEMPLATE        #Image converted to template successfully
    SEARCHING         #Searching for Model that match template in sensor's flash memory
    OKSEARCH 1 100    #Model found in slot 1 with confidence 100
    READTEMPLATE 1 2
    >

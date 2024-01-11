## **Communicate to Trinket M0 via Dart**

### Description
The set up requires the computer to be connected to the trinket m0 using micro USB on the trinket board. The trinket m0 must not be connected to any serial terminal when the Dart code connects to the trinket board.

The Dart program first lists all the ports available to connect, then it establishes the connection to the selected board. After opening the connection, it probes the trinket m0 by sending '\r' through the serial port through which the trinket m0 responds. The programs will continue this call and response loop with the trinket m0 until it exit via Ctrl + C or Ctrl + D interrupt from the user.

Over on the trinket m0, it continuously run code.py. Code.py is designed to talk to a fingerprint sensor using Adafruit Fingerprint library. The library is further reduced to minimize memory usage. All functions are usable except for download_model as it throws MemoryError (trinket m0 may not be suitable here).

The project is done in **Linux** (Mint) due to libserialport library being easily downloadable. Hence, the how to run section, especially step 3, **does not apply to Window or MacOS**.

### How to Run
1. Download Dart SDK
2. Download dependencies of dart code
```bash
dart pub upgrade
```
3. Download libserialport (C) library using 
```bash
sudo apt install libserialport-dev
```
4. Copy code.py and lib folder into trinket m0
5. Make sure trinket m0 is not in REPL, else press reset button or use Mu editor to input Ctrl + D to rerun the code
6. Run the dart code
```bash
dart communicate_trinket_m0.dart
```
7. Profit


### Updates
Update 9/1/2024:
- Added script to compile python library to board. It also save code.py to board.
- download\_template() is now enroll\_and\_send\_to_usb() (still unfished but _Soooooon_)
- Added userGetInput function to check for valid user input in Dart
- Added printAvailableCommands() to display commands menu
- **Output/print from board is now in the form of all caps short strings (ex: OKIMAGE). If extra output is required, it will be spaced out (ex: OKSEARCH 2 100 -> Finger found at #2, confidence 100). Error codes are in the form: ERROR _\<code\_number\>_. The code number can be found in adafruit fingerprint library (circuitpython or cpp) for debug**
- TODO: Exception handler when failing to connect to fingerprint and when failing to read template

Update 8/1/2024:
- Included lib folder with .mpy file to reduce memory usage (memory error still occurs with download_model)
- Updated README from txt to md
- Added project title, description and how to run in README.md
- Removed trinket_code_v1.py and trinket_code_v2.py. Replace with code.py
- Included library normal .py code before compiling to .mpy
- Added cross compilation tool mpy-cross (require execution permission)

Update 7/1/2024:
- Updated dart code to latest version
- Added python code in trinket m0 (circuitpython)
    + v1: full functionality: enroll, find, delete, set led
          load, get model available but causes MemoryError
    + v2 (latest): remove set led, import specific function only, added gc for
          memory checking, converted load, get model to download model function
          Still not functional due to MemoryError on get_fpdata()

### Reference and Resources
Flutter version of libserialport (Dart) is available [here](https://pub.dev/packages/flutter_libserialport)

libserialport download solution found [here](https://stackoverflow.com/questions/73387868/libserial-is-not-detected-in-my-dart-programm)

Adafruit Fingerprint library (Circuitpython) [here](https://github.com/adafruit/Adafruit_CircuitPython_Fingerprint/blob/main/adafruit_fingerprint.py)

Adafruit Fingerprint code (Circuitpython) [here](https://learn.adafruit.com/adafruit-optical-fingerprint-sensor/circuitpython)

.py to .mpy compilation tool [here](https://learn.adafruit.com/welcome-to-circuitpython/frequently-asked-questions)



Update 7/1/2024
-Updated dart code to latest version
-Add python code in trinket m0 (circuitpython)
    + v1: full functionality: enroll, find, delete, set led
          load, get model available but causes MemoryError
    + v2 (latest): remove set led, import specific function only, added gc for
          memory checking, converted load, get model to download model function
          Still not functional due to MemoryError on get_fpdata()

Note: -libserialport library can be downloaded using sudo apt install libserialport-dev (Linux Debian Based). 
      -Flutter version of this is available at https://pub.dev/packages/flutter_libserialport

libserialport download solution found here: https://stackoverflow.com/questions/73387868/libserial-is-not-detected-in-my-dart-programm






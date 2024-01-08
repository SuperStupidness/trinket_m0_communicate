from usb_cdc import console
from board import TX, RX
import custom_fingerprint_lib as finger_lib
import gc

uart = finger_lib.adafruit_fingerprint_reduced.UART(TX, RX, baudrate=57600)
finger = finger_lib.adafruit_fingerprint_reduced.Adafruit_Fingerprint(uart)
#finger._debug = True

while True:
    finger_lib.show_template(finger)
    user_input = input('>').strip()

    gc.collect()
    start_mem = gc.mem_free()
    print( "Point 1 Available memory: {} bytes".format(start_mem) )

    if user_input == '1':
        finger_lib.enroll_finger(finger, finger_lib.get_num())
    elif user_input == '2':
        finger.set_led(color=3, mode=1)
        if finger_lib.get_fingerprint(finger):
            print("Detected #", finger.finger_id, "with confidence", finger.confidence)
        else:
            print("Finger not found")
    elif user_input == '3':
        if finger.delete_model(finger_lib.get_num()) == finger_lib.adafruit_fingerprint.OK:
            print("Deleted!")
        else:
            print("Failed to delete")
    elif user_input == '4':
        #Memory error here
        finger_lib.download_model(finger, finger_lib.get_num())
    elif user_input == '5':
        print("So nam")

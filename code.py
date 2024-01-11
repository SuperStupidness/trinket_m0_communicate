from usb_cdc import console
from board import GP0, GP1 #TX, RX
import custom_fingerprint_lib as finger_lib
import gc

uart = finger_lib.adafruit_fingerprint_reduced.UART(GP0, GP1, baudrate=57600)
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
        if finger_lib.get_fingerprint(finger):
            #print("Detected #",finger.finger_id," with confidence ",finger.confidence)
            print("{} {}".format(finger.finger_id, finger.confidence))
    elif user_input == '3':
        finger_lib.erase_model(finger, finger_lib.get_num())
    elif user_input == '4':
        #Trinket M0 Memory error here
        print(finger_lib.enroll_and_send_usb(finger))
        #start_mem = gc.mem_free()
        #print( "Point 2 Available memory: {} bytes".format(start_mem))
    elif user_input == '5':
        print("So nam")

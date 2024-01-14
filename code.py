from usb_cdc import console
from board import GP0, GP1 #TX, RX
import custom_fingerprint_lib as finger_lib
from gc import collect

NUMARGUMENT = const(0x57)
LOCATIONVAL = const(0x58)
WRONGCOMMAND = const(0x59)

# finger_lib.init_fingerprint_sensor(baudrate=115200, security_level=5, data_packet_size=128)
# Default is baudrate=57600, security_level=3, data_packet_size=2 (128)
# Sensor is set to baudrate=115200, security_level=3, data_packet_size=3 (256) for best performance
finger_template_test = -1
console.reset_input_buffer()
console.reset_output_buffer()

# Fingerprint initialisation
while True:
    collect() # garbage collection to free ram
    print('SENSORINIT')
    try:
        uart = finger_lib.adafruit_fingerprint_reduced.UART(GP0, GP1, baudrate=115200)
        finger = finger_lib.adafruit_fingerprint_reduced.Adafruit_Fingerprint(uart)
    except RuntimeError:
        uart.deinit()
        collect()
        finger = finger_lib.init_fingerprint_sensor(GP0, GP1, 115200, 3, 3)

    if finger is bool:
        print("CONNECTIONFAIL")
        wait = input('>')
        continue;

    print("PARAMDETAIL {} {} {}".format(finger.baudrate, finger.security_level, finger.data_packet_size))
    break;

while True:
    collect()
    finger_lib.show_template(finger)

    # Check for no input
    user_input = input('>').strip()
    if user_input == "":
        finger_lib.print_error(NUMARGUMENT)
        continue

    user_input = user_input.split()

    commands = user_input[0]
    location = -1

    if commands in ['1','3']:
        if len(user_input) == 2:
            location = int(user_input[1])
            if location <= 0 or location > 120:
                finger_lib.print_error(LOCATIONVAL)
                continue
        else:
            finger_lib.print_error(NUMARGUMENT)
            continue

    if commands == '1':
        finger_lib.enroll_finger(finger, location)
    elif commands == '2':
        if finger_lib.get_fingerprint(finger):
            #print("Detected #",finger.finger_id," with confidence ",finger.confidence)
            print("{} {}".format(finger.finger_id, finger.confidence))
    elif commands == '3':
        finger_lib.erase_model(finger, location)
    elif commands == '4':
        #Trinket M0 Memory error here
        finger_template = finger_lib.enroll_and_send_usb(finger)
        collect()
        if finger_template is not False:
            for i in range(0,2048,128):
                console.write(bytes(finger_template[i:i+128]))

        print(finger_template)

    elif commands == '5':
        finger_lib.upload_and_compare_with_fingerprint(finger, finger_template_test)
    else:
        finger_lib.print_error(WRONGCOMMAND)

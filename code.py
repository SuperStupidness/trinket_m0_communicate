from usb_cdc import console
from board import GP0, GP1 #TX, RX
import custom_fingerprint_lib as finger_lib
from gc import collect
import binascii

NUMARGUMENT = const(0x57)
LOCATIONVAL = const(0x58)
WRONGCOMMAND = const(0x59)

# Default config of uart to sensor is baudrate=57600, security_level=3, data_packet_size=2 (128)

# Reset usb serial input and output buffer
finger_template_test = -1
init_okay = True
console.reset_input_buffer()
console.reset_output_buffer()

# Fingerprint initialisation
#   1. Establish connection to the finger print sensor by scanning the baudrate and select the correct one
#   2. Sensor is set to baudrate=115200, security_level=3, data_packet_size=2 (128) for best performance
#   3. Connection is restarted once more to the desired config and fingerprint class is returned
print('SENSORINIT')
try:
    uart = finger_lib.adafruit_fingerprint_reduced.UART(GP0, GP1, baudrate=115200)
    finger = finger_lib.adafruit_fingerprint_reduced.Adafruit_Fingerprint(uart)
except RuntimeError:
    uart.deinit()
    collect()
    finger = finger_lib.init_fingerprint_sensor(GP0, GP1, 115200, 3, 2)

if finger is bool:
    init_okay = False
else:
    print("PARAMDETAIL {} {} {}".format(finger.baudrate, finger.security_level, finger.data_packet_size))

# Main program loop here
while True and init_okay:
    # Display available template on sensor
    collect()
    # Reset input buffer just in case Dart sent junk data
    finger_lib.show_template(finger)

    # Get input and check it. Expected: >[commands] [location]. Type: int int
    user_input = input('>').strip()
    if user_input == "":
        finger_lib.print_error(NUMARGUMENT)
        continue

    user_input = user_input.split()

    commands = user_input[0]
    location = -1

    # Another one so that supervisor.runtime.serial_bytes_available works
    # inside #1 and #3 for cancelling taking fingerprint
    # console.reset_input_buffer()

    # Check second argument of input. Bound is set by the sensor.
    # Only template location 1-120 is accepted by the sensor
    if commands in ['1','3']:
        if len(user_input) == 2:
            location = int(user_input[1])
            if location <= 0 or location > 120:
                finger_lib.print_error(LOCATIONVAL)
                continue
        else:
            finger_lib.print_error(NUMARGUMENT)
            continue

    #1 -> Enroll fingerprint and store in sensor
    if commands == '1':
        finger_lib.enroll_finger(finger, location)

    #2 -> Get fingerprint and match with model in library
    elif commands == '2':
        if finger_lib.get_fingerprint(finger):
            #print("Detected #",finger.finger_id," with confidence ",finger.confidence)
            print("{} {}".format(finger.finger_id, finger.confidence))

    #3 -> Delete a model in a location in library
    elif commands == '3':
        finger_lib.erase_model(finger, location)

    #4 -> Enroll fingerprint in location 1 and download that model back to usb
    elif commands == '4':
        #Trinket M0 Memory error here
        template = finger_lib.enroll_and_send_usb(finger)
        collect()
        if template is not False:
            string = binascii.hexlify(bytes(template))
            print(string)
            pass
        #Just so that serial port is not accessed at the same time from pc and board
        finger_lib.sleep(1)

    #5 -> Get fingerprint template from database through usb and compare with fingerprint taken
    elif commands == '5':
        finger_template_test = input().strip()
        finger_template_test = binascii.unhexlify(finger_template_test)
        finger_lib.sleep(1)
        finger_lib.upload_and_compare_with_fingerprint(finger, finger_template_test)

    #6 -> Delete every model in the library
    elif commands == '6':
        res = finger.empty_library()
        finger_lib.check_return_code_delete(res)
    else:
        finger_lib.print_error(WRONGCOMMAND)

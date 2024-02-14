from usb_cdc import console
import board
import custom_fingerprint_lib as finger_lib
import binascii

NUMARGUMENT = const(0x57)
LOCATIONVAL = const(0x58)
WRONGCOMMAND = const(0x59)
BADUPLOAD = const(0x5D)
NONHEX = const(0x5E)

init_okay = True
company_logo_file = "\img\carptech_scaled.bmp"
error_logo_file = "\img\crossmark_scaled.bmp"
success_logo_file = "\img\checkmark_scaled.bmp"
working_logo_file = "\img\\tripledot_scaled.bmp"

# Duration to display text on OLED (second)
short_msg_dur = 1
long_msg_dur = 2
long_long_dur = 3
command_msg_dur = 0.5

# color: 1=red, 2=blue, 3=purple
# mode: 1-breathe, 2-flash, 3-on, 4-off, 5-fade_on, 6-fade-off
default_led_color = 2
default_led_mode = 1

# Default config of uart to sensor is baudrate=57600, security_level=3, data_packet_size=2 (128)

# Fingerprint initialisation
#   1. Establish connection to the finger print sensor by scanning the baudrate and select the correct one
#   2. Sensor is set to baudrate=115200, security_level=3, data_packet_size=2 (128) for best performance
#   3. Connection is restarted once more to the desired config and fingerprint class is returned
print('SENSORINIT')

desired_baudrate = 115200 # Change if needed based on sensor

# UART pin name is different in every board make sure to change it to match your board
uart = finger_lib.adafruit_fingerprint_reduced.UART(board.TX, board.RX, baudrate=desired_baudrate)

try:
    finger = finger_lib.adafruit_fingerprint_reduced.Adafruit_Fingerprint(uart)
except RuntimeError as error:
    print("Sensor connection failed: ",  type(error).__name__, "-", error)
    print("Checking sensor's baudrate")
    uart.deinit()
    finger = finger_lib.init_fingerprint_sensor(board.TX, board.RX, desired_baudrate, 3, 2)

if finger is bool:
    init_okay = False
    print("Init failed: Check sensor's connection or UART pin")
else:
    print("PARAMDETAIL {} {} {}".format(finger.baudrate, finger.security_level, finger.data_packet_size))

# Display initialisation and create white background

print('DISPLAYINIT')

finger_lib.displayio.release_displays()

# This I2C function might not be available on everyboard
# Alternative is to use busio.I2C(scl pin, sda pin)
i2c = board.I2C()  # uses board.SCL and board.SDA

try:
    display_bus = finger_lib.displayio.I2CDisplay(i2c, device_address=0x3C)
    display = finger_lib.adafruit_displayio_ssd1306.SSD1306(display_bus, width=128, height=32)
except Exception as error:
    # No display or I2C connection problem
    print("Display init failed: ",  type(error).__name__, "-", error)
    splash = None
else:
    # Make the display context
    splash = finger_lib.displayio.Group()
    display.root_group = splash

    color_bitmap = finger_lib.displayio.Bitmap(128, 32, 1)
    color_palette = finger_lib.displayio.Palette(1)
    color_palette[0] = 0xFFFFFF  # White

    bg_sprite = finger_lib.displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
    splash.append(bg_sprite)

    # Show name and logo of company
    finger_lib.run_start_sequence(splash, "CARPTECH", company_logo_file)

# Main program loop here
while True and init_okay:
    # Clear any unread input
    if console.in_waiting > 0:
        console.read(console.in_waiting)

    finger_lib.display_text_and_logo(splash, "READY", company_logo_file)
    # Led commands not available on R557 so this does nothing
    finger.set_led(color=default_led_color, mode=default_led_mode)
    # Display available template on sensor
    finger_lib.show_template(finger)

    # Get input and check it. Expected: >[commands] [location]. Type: int int
    user_input = input('>').strip()
    if user_input == "":
        finger_lib.print_error(NUMARGUMENT)
        finger_lib.display_sequence_of_text(splash, "Empty input", error_logo_file, short_msg_dur)
        # finger_lib.display_scroll_sequence_of_text(splash, "Incorrect number of argument", error_logo_file, 2, 0.12)
        continue

    user_input = user_input.split()

    commands = user_input[0]
    location = -1

    # Check second argument of input. Bound is set by the sensor.
    # Only template location 1-120 is accepted by the sensor
    if commands in ['1','3']:
        if len(user_input) == 2:
            location = int(user_input[1])
            if location <= 0 or location > 120:
                finger_lib.print_error(LOCATIONVAL)
                finger_lib.display_sequence_of_text(splash, "Bad location value", error_logo_file, long_msg_dur)
                continue
        else:
            finger_lib.print_error(NUMARGUMENT)
            finger_lib.display_sequence_of_text(splash, "Wrong number of argument", error_logo_file, long_msg_dur)
            continue

    #1 -> Enroll fingerprint and store in sensor
    if commands == '1':
        finger_lib.display_text_and_logo(splash, "ENROLL", working_logo_file)
        if finger_lib.enroll_finger(finger, location, splash):
            finger_lib.display_sequence_of_text(splash, "Enroll success!", success_logo_file, short_msg_dur)

    #2 -> Get fingerprint and match with model in library
    elif commands == '2':
        finger_lib.display_text_and_logo(splash, "IDENTIFY", working_logo_file)
        if finger_lib.get_fingerprint(finger, splash):
            #print("Detected #",finger.finger_id," with confidence ",finger.confidence)
            print("{} {}".format(finger.finger_id, finger.confidence))
            finger_lib.display_scroll_sequence_of_text(splash, "Detected #{} with confidence {}!".format(finger.finger_id, finger.confidence), success_logo_file, long_long_dur, 0.15)

    #3 -> Delete a model in a location in library
    elif commands == '3':
        finger_lib.display_text_and_logo(splash, "DELETE", working_logo_file)
        if finger_lib.erase_model(finger, location, splash):
            finger_lib.display_sequence_of_text(splash, "Delete #{} Success!".format(location), success_logo_file, long_msg_dur)

    #4 -> Enroll fingerprint in location 1 and download that model back to usb
    elif commands == '4':
        finger_lib.display_text_and_logo(splash, "DOWNLOAD", working_logo_file)
        #Trinket M0 Memory error here
        template = finger_lib.enroll_and_send_usb(finger, splash=splash)
        if template is not False:
            finger_lib.display_sequence_of_text(splash, "Download success!", success_logo_file, short_msg_dur)
            string = binascii.hexlify(bytes(template))
            finger_lib.display_text_and_logo(splash, "Sending", working_logo_file)
            print(string)
            pass
        #Just so that serial port is not accessed at the same time from pc and board
        finger_lib.sleep(1)

    #5 -> Get fingerprint template from database through usb and compare with fingerprint taken
    elif commands == '5':
        finger_template = input().strip()

        # Check template uploaded from dart
        if len(finger_template) != 4096 or len(finger_template) % 2 != 0:
            finger_lib.print_error(WRONGUPLOAD)
            continue
        try:
            finger_template = binascii.unhexlify(finger_template)
        except ValueError as error:
            finger_lib.print_error(NONHEX)
            continue

        finger_lib.display_text_and_logo(splash, "UPLOAD", working_logo_file)
        finger_lib.sleep(1)
        if finger_lib.upload_and_compare_with_fingerprint(finger, finger_template, splash):
            finger_lib.display_sequence_of_text(splash, "Finger match!", success_logo_file, short_msg_dur)

    #6 -> Delete every model in the library
    elif commands == '6':
        finger_lib.display_sequence_of_text(splash, "EMPTY", working_logo_file, command_msg_dur)
        res = finger.empty_library()
        if finger_lib.check_return_code_delete(res):
            finger_lib.display_sequence_of_text(splash, "Library emptied!", working_logo_file, short_msg_dur)
    else:
        finger_lib.display_sequence_of_text(splash, "Invalid Command", working_logo_file, short_msg_dur)
        finger_lib.print_error(WRONGCOMMAND)


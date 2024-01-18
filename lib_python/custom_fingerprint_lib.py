# Write your code here :-)
from usb_cdc import console
from time import sleep
import adafruit_fingerprint_reduced
import supervisor

##################################################

'''
Packet error code from fingerprint sensor
OK = const(0x0)
PACKETRECIEVEERR = const(0x01)
NOFINGER = const(0x02)
IMAGEFAIL = const(0x03)
IMAGEMESS = const(0x06)
FEATUREFAIL = const(0x07)
NOMATCH = const(0x08)
NOTFOUND = const(0x09)
ENROLLMISMATCH = const(0x0A)
BADLOCATION = const(0x0B)
DBRANGEFAIL = const(0x0C)
UPLOADFEATUREFAIL = const(0x0D)
PACKETRESPONSEFAIL = const(0x0E)
UPLOADFAIL = const(0x0F)
DELETEFAIL = const(0x10)
DBCLEARFAIL = const(0x11)
PASSFAIL = const(0x13)
INVALIDIMAGE = const(0x15)
FLASHERR = const(0x18)
INVALIDREG = const(0x1A)
ADDRCODE = const(0x20)
PASSVERIFY = const(0x21)
MODULEOK = const(0x55)

Status string output
'''
# FINGERREQUEST
# TEMPLATING
# SEARCHING
# REMOVEFINGER
# CREATEMODEL
# STOREMODEL
# READTEMPLATE
# FINGERHOLD
# NUMBERREQUEST
# PARAMDETAIL
# SENSORINIT
# TEMPDOWNLOAD
# TEMPUPLOAD

# Success String Output
# OKIMAGE
# OKTEMPLATE
# OKMODEL
# OKSTORAGE
# OKDELETE
# OKSEARCH
# OKPARAMSET
# OKDOWNLOAD
# OKMATCH
# OKUPLOAD

SETPARAMFAIL = const(0x56)
DOWNLOADFAIL = const(0x5A)
UPLOADFAIL = const(0x5B)
MATCHFAIL = const(0x5C)

# How long the sensor waits before taking the image
# Adjust to balance between responsiveness and accuracy.
# Too fast -> bad image due to user finger not pressed well against sensor.
hold_duration = 0.1

def init_fingerprint_sensor(TX, RX, baudrate, security_level, data_package_size):
    PARAM_NUM = [4, 5, 6] # Baud rate, Security Level, Data Packet Length
    current_baudrate = 9600
    uart = adafruit_fingerprint_reduced.UART(TX, RX, baudrate=current_baudrate)

    # Test all baudrate and connect using the desired one
    for i in range(6,13):
        try:
            finger = adafruit_fingerprint_reduced.Adafruit_Fingerprint(uart)
        except RuntimeError:
            current_baudrate = 9600*i
            uart.baudrate = current_baudrate
        else:
            if set_sensor_parameter(finger, PARAM_NUM[0], int(baudrate/9600)):
                break
            else:
                return False

    uart.deinit()
    uart = adafruit_fingerprint_reduced.UART(TX, RX, baudrate=baudrate)
    finger = adafruit_fingerprint_reduced.Adafruit_Fingerprint(uart)

    # Set security_level to desired level
    if set_sensor_parameter(finger, PARAM_NUM[1], security_level):
        pass
    else:
        return False

    # Set data_package_size to desired data_package_size
    if set_sensor_parameter(finger, PARAM_NUM[2], data_package_size):
        pass
    else:
        return False

    return finger

def get_fingerprint(finger):
    """Get a finger print image, template it, and see if it matches!"""
    print('FINGERREQUEST')

    # User presses finger
    while True:
        i = finger.get_image()
        if i == adafruit_fingerprint_reduced.OK:
            print('OKIMAGE')
            break
        if i == adafruit_fingerprint_reduced.NOFINGER:
            # print_error(adafruit_fingerprint_reduced.NOFINGER)
            if supervisor.runtime.serial_bytes_available:
                data = input().strip()
                if data == 'CANCEL':
                    return False
        elif i == adafruit_fingerprint_reduced.IMAGEFAIL:
            print_error(adafruit_fingerprint_reduced.IMAGEFAIL)
            return False
        elif code == adafruit_fingerprint_reduced.PACKETRECIEVEERR:
            print_error(adafruit_fingerprint_reduced.PACKETRECIEVEERR)
            return False
        else:
            print_error(None)
            return False



    # User holds finger
    print('FINGERHOLD')
    sleep(hold_duration)

    # Image now taken
    i = finger.get_image()
    if i == adafruit_fingerprint_reduced.OK:
        print('OKIMAGE')
    elif i == adafruit_fingerprint_reduced.NOFINGER:
        print_error(adafruit_fingerprint_reduced.NOFINGER)
    elif i == adafruit_fingerprint_reduced.IMAGEFAIL:
        print_error(adafruit_fingerprint_reduced.IMAGEFAIL)
        return False
    elif i == adafruit_fingerprint_reduced.PACKETRECIEVEERR:
        print_error(adafruit_fingerprint_reduced.PACKETRECIEVEERR)
        return False
    else:
        print_error(None)
        return False

    print('TEMPLATING')
    i = finger.image_2_tz(1)
    if not check_return_code_template(i):
        return False

    print('SEARCHING')
    i = finger.finger_search()
    if not check_return_code_search(i):
        return False

    return True

# pylint: disable=too-many-statements
def enroll_finger(finger, location):
    """Take a 2 finger images and template it, then store in 'location'"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print('FINGERREQUEST')
        else:
            print('FINGERREQUEST')

        # User presses finger
        i = finger.get_image()
        while i != adafruit_fingerprint_reduced.OK:
            if supervisor.runtime.serial_bytes_available and i == adafruit_fingerprint_reduced.NOFINGER:
                data = input().strip()
                if data == 'CANCEL':
                    return False

            i = finger.get_image()

        # User holds finger to get a good image
        print('FINGERHOLD')
        sleep(hold_duration)

        i = finger.get_image()
        if i == adafruit_fingerprint_reduced.OK:
            print('OKIMAGE')
        elif i == adafruit_fingerprint_reduced.NOFINGER:
            print_error(adafruit_fingerprint_reduced.NOFINGER)
        elif i == adafruit_fingerprint_reduced.IMAGEFAIL:
            print_error(adafruit_fingerprint_reduced.IMAGEFAIL)
            return False
        elif i == adafruit_fingerprint_reduced.PACKETRECIEVEERR:
            print_error(adafruit_fingerprint_reduced.PACKETRECIEVEERR)
            return False
        else:
            print_error(None)
            return False

        print('TEMPLATING')
        i = finger.image_2_tz(fingerimg)
        if not check_return_code_template(i):
            return False

        if fingerimg == 1:
            print('REMOVEFINGER')
            sleep(0.1)
            while i != adafruit_fingerprint_reduced.NOFINGER:
                i = finger.get_image()

    print('CREATEMODEL')
    i = finger.create_model()
    if not check_return_code_model(i):
        return False

    print('STOREMODEL')
    i = finger.store_model(location)
    if not check_return_code_storage(i):
        return False

    return True

# Model is similar to template.
# Img file -> char file (via img2tz) -> template/model (via create_model)
# Adafruit Library does not have function that request img file.


# Circuitpython is set up so that the files are read only through its python program
# Hence we can't save the template locally on the board via file open() and write()
# Template is sent directly to usb. Connection must be stable while doing so
def enroll_and_send_usb(finger, location: int = 1):
    """Take a 2 finger images and template it, then store it in a file"""
    if enroll_finger(finger, location):
        print("TEMPDOWNLOAD")
        try:
            data = finger.get_fpdata("char", 1)
        except RuntimeError:
            print_error(DOWNLOADFAIL)
            return False
        else:
            print("OKDOWNLOAD {}".format(len(data)))
            return data
    else:
        return False

# Upload template data ("char" type) to sensor and take a fingerprint to compare
def upload_and_compare_with_fingerprint(finger, data):
    # Copied from get_fingerprint except for the search part
    print('FINGERREQUEST')

    # User presses finger
    while True:
        i = finger.get_image()
        if i == adafruit_fingerprint_reduced.OK:
            print('OKIMAGE')
            break
        if i == adafruit_fingerprint_reduced.NOFINGER:
            # print_error(adafruit_fingerprint_reduced.NOFINGER)
            if supervisor.runtime.serial_bytes_available:
                data = input().strip()
                if data == 'CANCEL':
                    return False
        elif i == adafruit_fingerprint_reduced.IMAGEFAIL:
            print_error(adafruit_fingerprint_reduced.IMAGEFAIL)
            return False
        elif code == adafruit_fingerprint_reduced.PACKETRECIEVEERR:
            print_error(adafruit_fingerprint_reduced.PACKETRECIEVEERR)
            return False
        else:
            print_error(None)
            return False

    # User holds finger
    print('FINGERHOLD')
    sleep(hold_duration)

    # Image now taken
    i = finger.get_image()
    if i == adafruit_fingerprint_reduced.OK:
        print('OKIMAGE')
    elif i == adafruit_fingerprint_reduced.NOFINGER:
        print_error(adafruit_fingerprint_reduced.NOFINGER)
    elif i == adafruit_fingerprint_reduced.IMAGEFAIL:
        print_error(adafruit_fingerprint_reduced.IMAGEFAIL)
        return False
    elif i == adafruit_fingerprint_reduced.PACKETRECIEVEERR:
        print_error(adafruit_fingerprint_reduced.PACKETRECIEVEERR)
        return False
    else:
        print_error(None)
        return False

    print('TEMPLATING')
    i = finger.image_2_tz(1)
    if not check_return_code_template(i):
        return False

    try:
        finger.send_fpdata(data, "char", 2)
    except RuntimeError:
        print_error(UPLOADFAIL)
        return False

    i = finger.compare_templates()
    if i == adafruit_fingerprint_reduced.OK:
        print("OKMATCH")
        return True
    elif i == adafruit_fingerprint_reduced.NOMATCH:
        print_error(MATCHFAIL)

    return False

def set_sensor_parameter(finger, param_num, param_val):
    try:
        res = finger.set_sysparam(param_num, param_val)
    except:
        print_error(SETPARAMFAIL)
    else:
        print('OKPARAMSET {} {}'.format(param_num, param_val))
        return True

    return False

def show_template(finger):
    if finger.read_templates() != adafruit_fingerprint_reduced.OK:
        raise RuntimeError("Failed to read templates")

    print('READTEMPLATE', end=' ')
    if len(finger.templates) == 0:
        print('0')
    else:
        print(*finger.templates)

    return

# Based on possible return packet from the sensor
# (refer to adafruit fingerprint library .cpp version)

def check_return_code_template(code):
    if code == adafruit_fingerprint_reduced.OK:
        print('OKTEMPLATE')
        return True
    elif code == adafruit_fingerprint_reduced.IMAGEMESS:
        print_error(adafruit_fingerprint_reduced.IMAGEMESS)
        return False
    elif code == adafruit_fingerprint_reduced.FEATUREFAIL:
        print_error(adafruit_fingerprint_reduced.FEATUREFAIL)
        return False
    elif code == adafruit_fingerprint_reduced.PACKETRECIEVEERR:
        print_error(adafruit_fingerprint_reduced.PACKETRECIEVEERR)
        return False
    elif code == adafruit_fingerprint_reduced.INVALIDIMAGE:
        print_error(adafruit_fingerprint_reduced.INVALIDIMAGE)
        return False
    else:
        print_error(None)
        return False

def check_return_code_model(code):
    if code == adafruit_fingerprint_reduced.OK:
        print('OKMODEL')
        return True
    elif code == adafruit_fingerprint_reduced.ENROLLMISMATCH:
        print_error(adafruit_fingerprint_reduced.ENROLLMISMATCH)
        return False
    elif code == adafruit_fingerprint_reduced.PACKETRECIEVEERR:
        print_error(adafruit_fingerprint_reduced.PACKETRECIEVEERR)
        return False
    else:
        print_error(None)
        return False

def check_return_code_storage(code):
    if code == adafruit_fingerprint_reduced.OK:
        print('OKSTORAGE')
        return True
    elif code == adafruit_fingerprint_reduced.BADLOCATION:
        print_error(adafruit_fingerprint_reduced.BADLOCATION)
        return False
    elif code == adafruit_fingerprint_reduced.FLASHERR:
        print_error(adafruit_fingerprint_reduced.FLASHERR)
        return False
    elif code == adafruit_fingerprint_reduced.PACKETRECIEVEERR:
        print_error(adafruit_fingerprint_reduced.PACKETRECIEVEERR)
        return False
    else:
        print_error(None)
        return False

def check_return_code_search(code):
    if code == adafruit_fingerprint_reduced.OK:
        print('OKSEARCH', end=' ')
        return True
    elif code == adafruit_fingerprint_reduced.NOTFOUND:
        print_error(adafruit_fingerprint_reduced.NOTFOUND)
        return False
    elif code == adafruit_fingerprint_reduced.PACKETRECIEVEERR:
        print_error(adafruit_fingerprint_reduced.PACKETRECIEVEERR)
        return False
    else:
        print_error(None)
        return False

def check_return_code_delete(code):
    if code == adafruit_fingerprint_reduced.OK:
        print('OKDELETE')
        return True
    elif code == adafruit_fingerprint_reduced.BADLOCATION:
        print_error(adafruit_fingerprint_reduced.BADLOCATION)
        return False
    elif code == adafruit_fingerprint_reduced.FLASHERR:
        print_error(adafruit_fingerprint_reduced.FLASHERR)
        return False
    elif code == adafruit_fingerprint_reduced.PACKETRECIEVEERR:
        print_error(adafruit_fingerprint_reduced.PACKETRECIEVEERR)
        return False
    else:
        print_error(None)
        return False

def erase_model(finger, location):
    i = finger.delete_model(location)
    if not check_return_code_delete(i):
        return False

    return True

##################################################


def print_error(error_code):
    if error_code is None:
        print('ERROR')
    else:
        print('ERROR', end=' ')
        print(error_code)

    return


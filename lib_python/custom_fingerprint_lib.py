# Write your code here :-)
from time import sleep
import adafruit_fingerprint_reduced

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

# Success String Output
# OKIMAGE
# OKTEMPLATE
# OKMODEL
# OKSTORAGE
# OKDELETE
# OKSEARCH

# How long the sensor waits before taking the image
# Adjust to balance between responsiveness and accuracy.
# Too fast -> bad image due to user finger not pressed well against sensor.
hold_duration = 0.1


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
            print_error(adafruit_fingerprint_reduced.NOFINGER)
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
    while True:
        i = finger.get_image()
        if i == adafruit_fingerprint_reduced.OK:
            print('OKIMAGE')
            break
        if i == adafruit_fingerprint_reduced.NOFINGER:
            print_error(adafruit_fingerprint_reduced.NOFINGER)
        elif i == adafruit_fingerprint_reduced.IMAGEFAIL:
            print_error(adafruit_fingerprint_reduced.IMAGEFAIL)
            return False
        elif code == adafruit_fingerprint_reduced.PACKETRECIEVEERR:
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
        while finger.get_image() != adafruit_fingerprint_reduced.OK:
            pass

        # User holds finger to get a good image
        print('FINGERHOLD')
        sleep(hold_duration)

        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint_reduced.OK:
                print('OKIMAGE')
                break
            if i == adafruit_fingerprint_reduced.NOFINGER:
                print_error(adafruit_fingerprint_reduced.NOFINGER)
            elif i == adafruit_fingerprint_reduced.IMAGEFAIL:
                print_error(adafruit_fingerprint_reduced.IMAGEFAIL)
                return False
            elif code == adafruit_fingerprint_reduced.PACKETRECIEVEERR:
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
            sleep(1)
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


#Circuitpython is set up so that the files are read only through its python program
#Hence we can't save the template locally on the board via file open() and write()
#Template is sent directly to usb. Connection must be stable while doing so
def enroll_and_send_usb(finger, location: int = 1):
    """Take a 2 finger images and template it, then store it in a file"""
    if enroll_finger(finger, location):
        print("Downloading template...")
        data = finger.get_fpdata("char", 1)
        print("Data length received: " + str(len(data)))
        return data
    else:
        return None

def fingerprint_check_from_file(finger):
    data = input()
    finger.send_fpdata(list(bytearray(data)), "char", 2)
    i = finger.compare_templates()


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
        print(adafruit_fingerprint_reduced.BADLOCATION)
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
        print(adafruit_fingerprint_reduced.BADLOCATION)
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


def get_num():
    """Use input() to get a valid number from 1 to 127. Retry till success!"""
    i = 0
    while (i > 127) or (i < 1):
        try:
            #print("Enter ID # from 1-127", end='')
            print('NUMBERREQUEST')
            i = int(input('>').strip())
        except ValueError:
            pass
    return i

def print_error(error_code):
    if error_code is None:
        print('ERROR')
    else:
        print('ERROR', end=' ')
        print(error_code)

    return


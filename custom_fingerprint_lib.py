# Write your code here :-)
from time import sleep
import adafruit_fingerprint_reduced

##################################################

def get_fingerprint(finger):
    """Get a finger print image, template it, and see if it matches!"""
    print("Waiting for image...")
    print('3', end='...')
    sleep(1)
    print('2', end='...')
    sleep(1)
    print('1', end='...')
    sleep(1)

    while finger.get_image() != adafruit_fingerprint_reduced.OK:
        pass
    print("Templating...")
    if finger.image_2_tz(1) != adafruit_fingerprint_reduced.OK:
        return False
    print("Searching...")
    if finger.finger_search()!= adafruit_fingerprint_reduced.OK:
        return False
    return True

# pylint: disable=too-many-statements
def enroll_finger(finger, location):
    """Take a 2 finger images and template it, then store in 'location'"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Place finger on sensor...")
        else:
            print("Place same finger again...")

        print('3', end='...')
        sleep(1)
        print('2', end='...')
        sleep(1)
        print('1', end='...')
        sleep(1)

        while True:
            i = finger.get_image()
            if i == adafruit_fingerprint_reduced.OK:
                print("Image taken")
                break
            if i == adafruit_fingerprint_reduced.NOFINGER:
                print(".", end="")
            elif i == adafruit_fingerprint_reduced.IMAGEFAIL:
                print("Imaging error")
                return False
            else:
                print("Other error")
                return False

        print("Templating...", end="")
        i = finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint_reduced.OK:
            print("Templated")
        else:
            if i == adafruit_fingerprint_reduced.IMAGEMESS:
                print("Image too messy")
            elif i == adafruit_fingerprint_reduced.FEATUREFAIL:
                print("Could not identify features")
            elif i == adafruit_fingerprint_reduced.INVALIDIMAGE:
                print("Image invalid")
            else:
                print("Other error")
            return False

        if fingerimg == 1:
            print("Remove finger")
            sleep(1)
            while i != adafruit_fingerprint_reduced.NOFINGER:
                i = finger.get_image()

    print("Creating model...", end="")
    i = finger.create_model()
    if i == adafruit_fingerprint_reduced.OK:
        print("Created")
    else:
        if i == adafruit_fingerprint_reduced.ENROLLMISMATCH:
            print("Prints did not match")
        else:
            print("Other error")
        return False

    print("Storing model #%d..." % location, end="")
    i = finger.store_model(location)
    if i == adafruit_fingerprint_reduced.OK:
        print("Stored")
    else:
        if i == adafruit_fingerprint_reduced.BADLOCATION:
            print("Bad storage location")
        elif i == adafruit_fingerprint_reduced.FLASHERR:
            print("Flash storage error")
        else:
            print("Other error")
        return False

    return True

# Model is similar to template.
# Img file -> char file (via img2tz) -> template/model (via create_model)
# Adafruit Library does not have function that request img file.
def download_model(finger, location):
    i = finger.load_model(location)
    if i == adafruit_fingerprint_reduced.BADLOCATION:
        print("Invalid location")
        return False
    elif i == adafruit_fingerprint_reduced.PACKETRECIEVEERR:
        print("Communication error")
        return False
    elif i == adafruit_fingerprint_reduced.OK:
        print(finger.get_fpdata())
    return True

def show_template(finger):
    if finger.read_templates() != adafruit_fingerprint_reduced.OK:
        raise RuntimeError("Failed to read templates")
    print("Fingerprint templates:", finger.templates)
    return

##################################################


def get_num():
    """Use input() to get a valid number from 1 to 127. Retry till success!"""
    i = 0
    while (i > 127) or (i < 1):
        try:
            print("Enter ID # from 1-127", end='')
            i = int(input('>').strip())
        except ValueError:
            pass
    return i





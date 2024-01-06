# Write your code here :-)
import gc
from usb_cdc import console
from time import sleep
from board import TX, RX
from busio import UART
gc.collect()
import adafruit_fingerprint

uart = UART(TX, RX, baudrate=57600)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)

gc.collect()
print( "Point 1 Available memory: {} bytes".format(gc.mem_free()))
##################################################

def get_fingerprint():
    """Get a finger print image, template it, and see if it matches!"""
    print("Waiting for image...")
    print('3', end='...')
    sleep(1)
    print('2', end='...')
    sleep(1)
    print('1', end='...')
    sleep(1)

    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print("Templating...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False
    print("Searching...")
    if finger.finger_search()!= adafruit_fingerprint.OK:
        return False
    return True


# pylint: disable=too-many-branches
def get_fingerprint_detail():
    """Get a finger print image, template it, and see if it matches!
    This time, print out each error instead of just returning on failure"""
    print("Getting image...", end="")
    i = finger.get_image()
    if finger.get_image() == adafruit_fingerprint.OK:
        print("Image taken")
    else:
        if i == adafruit_fingerprint.NOFINGER:
            print("No finger detected")
        elif i == adafruit_fingerprint.IMAGEFAIL:
            print("Imaging error")
        else:
            print("Other error")
        return False

    print("Templating...", end="")
    i = finger.image_2_tz(1)
    if i == adafruit_fingerprint.OK:
        print("Templated")
    else:
        if i == adafruit_fingerprint.IMAGEMESS:
            print("Image too messy")
        elif i == adafruit_fingerprint.FEATUREFAIL:
            print("Could not identify features")
        elif i == adafruit_fingerprint.INVALIDIMAGE:
            print("Image invalid")
        else:
            print("Other error")
        return False

    print("Searching...", end="")
    i = finger.finger_fast_search()
    # pylint: disable=no-else-return
    # This block needs to be refactored when it can be tested.
    if i == adafruit_fingerprint.OK:
        print("Found fingerprint!")
        return True
    else:
        if i == adafruit_fingerprint.NOTFOUND:
            print("No match found")
        else:
            print("Other error")
        return False


# pylint: disable=too-many-statements
def enroll_finger(location):
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
            if i == adafruit_fingerprint.OK:
                print("Image taken")
                break
            if i == adafruit_fingerprint.NOFINGER:
                print(".", end="")
            elif i == adafruit_fingerprint.IMAGEFAIL:
                print("Imaging error")
                return False
            else:
                print("Other error")
                return False

        print("Templating...", end="")
        i = finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint.OK:
            print("Templated")
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                print("Image too messy")
            elif i == adafruit_fingerprint.FEATUREFAIL:
                print("Could not identify features")
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                print("Image invalid")
            else:
                print("Other error")
            return False

        if fingerimg == 1:
            print("Remove finger")
            sleep(1)
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()

    print("Creating model...", end="")
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        print("Created")
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            print("Prints did not match")
        else:
            print("Other error")
        return False

    print("Storing model #%d..." % location, end="")
    i = finger.store_model(location)
    if i == adafruit_fingerprint.OK:
        print("Stored")
    else:
        if i == adafruit_fingerprint.BADLOCATION:
            print("Bad storage location")
        elif i == adafruit_fingerprint.FLASHERR:
            print("Flash storage error")
        else:
            print("Other error")
        return False

    return True

# Model is similar to template.
# Img file -> char file (via img2tz) -> template/model (via create_model)
# Adafruit Library does not have function that request img file.
def download_model(location):
    
    
    print(finger.get_fpdata())

    return True

##################################################


def get_num():
    """Use input() to get a valid number from 1 to 127. Retry till success!"""
    i = 0
    while (i > 127) or (i < 1):
        try:
            print("Enter ID # from 1-127> ", end='')
            i = int(console.readline())
        except ValueError:
            pass
    return i


# initialize default LED color
# led_color = 1
# led_mode = 3
# empty input from serial when the code restart or lost connection
# so the next input is the latest one

console.readline()

while True:
    gc.collect()
    print( "Point 2 Available memory: {} bytes".format(gc.mem_free()) )

    # Turn on LED
    finger.set_led(color=1, mode=3)
    print("----------------")
    if finger.read_templates() != adafruit_fingerprint.OK:
        raise RuntimeError("Failed to read templates")
    print("Fingerprint templates:", finger.templates)
    print("e) enroll print")
    print("f) find print")
    print("d) delete print")
    print("g) get model")
    # print("l) set LED")
    print("----------------")
    print('>', end='');
    c = str(console.readline())[2]
    
    gc.collect()
    print( "Point 3 Available memory: {} bytes".format(gc.mem_free()) )
    
    #if c == "l":
    #    c = input("color(r,b,p anything else=off)> ")
    #    led_mode = 3
    #    if c == "r":
    #        led_color = 1
    #    elif c == "b":
    #        led_color = 2
    #    elif c == "p":
    #        led_color = 3
    #    else:
    #        led_color = 1
    #        led_mode = 4
    if c == "e":
        enroll_finger(get_num())
    elif c == "f":
        # breathing LED
        finger.set_led(color=3, mode=1)
        if get_fingerprint():
            print("Detected #", finger.finger_id, "with confidence", finger.confidence)
        else:
            print("Finger not found")
    elif c == "d":
        if finger.delete_model(get_num()) == adafruit_fingerprint.OK:
            print("Deleted!")
        else:
            print("Failed to delete")
    elif c == "g":
        download_model(get_num())
    else:
        #led_color = 1
        #sleep(1)
        #led_color = 2
        print("Invalid choice: Try again")


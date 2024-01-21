import 'package:libserialport/libserialport.dart';
import 'dart:io';
import 'dart:async';
import 'dart:typed_data';

final TEMPLATEBUFFERSIZE = 4096;

///List all serail port available connected to device
///Return number of port connected
int listAvailablePort()
{
    print('Listing available ports...');
    var i = 0;
    for (final name in SerialPort.availablePorts) {
        final sp = SerialPort(name);
        print('Port Number ${++i}: $name');
        print('\tDescription: ${sp.description}');
        print('\tManufacturer: ${sp.manufacturer}');
        print('\tSerial Number: ${sp.serialNumber}');
        print('\tProduct ID: 0x${sp.productId!.toRadixString(16)}');
        print('\tVendor ID: 0x${sp.vendorId!.toRadixString(16)}');
        print('\tRead/Write Available: ${sp.openReadWrite()}');
        sp.dispose();
  }
  print('Done');
  return SerialPort.availablePorts.length;
}

///Get user input and check for errors
///Return selected port number
int serialPortSelect()
{
    var numberOfPort = SerialPort.availablePorts.length;

    while ((SerialPort.availablePorts).isNotEmpty)
    {
        stdout.write('Please select fingerprint port number (-1 to exit or 0 to list all available port): ');

        //tryParse return null if fail
        int? userInput = int.tryParse(stdin.readLineSync() ?? '0');

        if (userInput == null)
        {
            print("Error: Input must be an integer. Please try again.");
            continue;
        }

        if (userInput > numberOfPort || userInput < -1)
        {
            print("Error: Port index out of range. Please try again.");
            continue;
        }

        switch (userInput)
        {
            case 0:
                listAvailablePort();
                break;
            case -1:
                return userInput;
                break;
            default:
                return userInput;
                break;
        }
    }
    print("No serial port detected.");
    return -1;
}

void printPortDescription(int portNumber)
{
    final name = SerialPort.availablePorts[portNumber - 1];
    final sp = SerialPort(name);
    print('\tPort Name: $name');
    print('\tDescription: ${sp.description}');
    print('\tManufacturer: ${sp.manufacturer}');
    print('\tSerial Number: ${sp.serialNumber}');
    print('\tProduct ID: 0x${sp.productId!.toRadixString(16)}');
    print('\tVendor ID: 0x${sp.vendorId!.toRadixString(16)}');
    sp.dispose();
}

Uint8List stringToUint8List(String msg)
{
    List<int> data = msg.codeUnits;
    return Uint8List.fromList(data);
}

void printSerialPortConfig(SerialPort port)
{
    SerialPortConfig config = port.config;
    print("\tCurrent Configuration of ${port.name}");
    print("\tBaud rate: ${config.baudRate}");
    print("\tNumber of Data Bits: ${config.bits}");
    print("\tNumber of Parity Bits: ${config.parity}");
    print("\tNumber of Stop Bits: ${config.stopBits}");
    print("\tRts Cts: ${config.rts} ${config.cts}");
    print("\tDsr Dtr: ${config.dsr} ${config.dtr}");
    print("\tXonXoff: ${config.xonXoff}");
    return;
}

///Based on working case with Linux laptop to trinket m0 using micro usb
///Recommended in documentation to set a default config. Change if needed.
void setDefaultSerialPortConfig(SerialPort port)
{
    print("Setting ${port.name} to default config based on working config (Linux -> trinket m0)");
    port.config.baudRate = 115200;
    port.config.bits = 8;
    port.config.parity = 0;
    port.config.stopBits = 1;
    print("Success!");
    return;
}

void printAvailableCommands()
{
    print('Dart: Fingerprint Commands:');
    print('\t1 -> Enroll fingerprint');
    print('\t2 -> Identify fingerprint');
    print('\t3 -> Delete fingerprint');
    print('\t4 -> Enroll and send template back via USB');
    print('\t5 -> Upload template, get fingerprint and verify');
    print('\t6 -> Clear all templates in sensor\'s library');
    print('\tstop -> end communication with board and exit');
    print('\treset -> Rerun code python on board (Send Ctrl + D command)');
    return;
}

//Check for template data message and return template data
int checkIsMessage(Uint8List data, String message)
{
    var messageCode = message.codeUnits;
    int count = 0;

    for (int i = 0; i < data.length; i++)
    {
        if (data[i] == messageCode[count])
        {
            count += 1;
        } else if ((count == 1) & (data[i] != messageCode[count])) //Quick return
        {
            return -1;
        }

        if (count == message.length)
        {
            return i-count+1;
        }
    }

    return -1;
}

int min(int num1, int num2)
{
    if (num1 < num2)
    {
        return num1;
    } else
    {
        return num2;
    }
}

void getTemplateData(Uint8List data, Uint8List templateBuffer, int length)
{
    if (length < TEMPLATEBUFFERSIZE)
    {
        templateBuffer.setAll(length, data.sublist(0, min(data.length, TEMPLATEBUFFERSIZE)));
    }
    return;
}

void main() async
{
    if (listAvailablePort() == 0)
    {
        print("No serial port available for communication. Please check and try again.");
        return;
    }

    //Get user input after listing connected port
    int portNumber = serialPortSelect();

    if (portNumber == -1)
    {
        print("Exit program.");
        return;
    }

    //Create port object
    final name = SerialPort.availablePorts[portNumber - 1];
    final fingerprintPort = SerialPort(name);
    print("\tPort ${portNumber} selected.");
    printPortDescription(portNumber);

    //Open port for communication
    fingerprintPort.openReadWrite();
    print('');

    //Print serial port configuration and set to default config
    printSerialPortConfig(fingerprintPort);
    print('');
    setDefaultSerialPortConfig(fingerprintPort);
    printSerialPortConfig(fingerprintPort);

    //Wake up trinket m0 with bad data to get menu
    //String line = stdin.readLineSync() ?? ' ';
    Uint8List sendBuffer = stringToUint8List('\r'+'\n');
    fingerprintPort.write(sendBuffer);

    //Print all commands that can be send to board
    print('');
    printAvailableCommands();
    print('');

    //Listening for response
    final fingerprintReader = SerialPortReader(fingerprintPort);

    // Template extraction variables
    int takeDataNextPacketFlag = 0;
    int length = 0;
    int removeFirstByte = 0;
    Uint8List templateBuffer = Uint8List(TEMPLATEBUFFERSIZE);
    templateBuffer.fillRange(0, TEMPLATEBUFFERSIZE, 2);

    // Interrupt taking fingerprint flag
    int interruptFingerFlag = -1;
    final interruptCheckStream = stdin.asBroadcastStream();
    final interruptStreamController = StreamController.broadcast();
    interruptStreamController.addStream(interruptCheckStream);
    final subscription = interruptCheckStream.listen((data) {
        if (data[0] == 27) // 27 is Esc key
        {
            //print('Cancelling taking fingerprint...');
            Uint8List sendBuffer = stringToUint8List('CANCEL'+'\n'+'\r');
            fingerprintPort.write(sendBuffer);
        }
    });
    subscription.pause();

    print('Displaying output from board...');
    fingerprintReader.stream.listen((data) async {
         //print('Recieved ${data} ${data.length}');
        // Decode data into ascii and print it
        for (var i in data)
        {
            // Remove character that is not letter, number or punctuation. Permit \n
            if ((i >= 32) & (i < 127) | (i == 10))
            {
                String char = String.fromCharCode(i);
                stdout.write('${char}');
                // > indicate that trinket request input. Input section
                if ((char == '>'))
                {
                    String line = stdin.readLineSync() ?? '';
                    if (line.compareTo('stop') == 0)
                    {
                        //Exit program
                        subscription.cancel();
                        fingerprintReader.close();
                        exit(0);
                    } else if (line.compareTo('reset') == 0)
                    {
                        // Send Ctrl+D to board
                        Uint8List sendBuffer = stringToUint8List('\x04'+'\r');
                        fingerprintPort.write(sendBuffer);
                        break;
                    } else if (line.compareTo('5') == 0)
                    {
                        // Upload template to board
                        Uint8List sendBuffer = stringToUint8List(line+'\n'+'\r');
                        fingerprintPort.write(sendBuffer);
                        fingerprintPort.drain();
                        fingerprintPort.write(templateBuffer);
                        fingerprintPort.drain();
                        sendBuffer = stringToUint8List('\n'+'\r');
                        fingerprintPort.write(sendBuffer);
                        //print(templateBuffer);

                    } else if (line.compareTo('help') == 0)
                    {
                        printAvailableCommands();
                        Uint8List sendBuffer = stringToUint8List('\r'+'\n');
                        fingerprintPort.write(sendBuffer);
                    } else
                    {
                        Uint8List sendBuffer = stringToUint8List(line+'\n'+'\r');
                        fingerprintPort.write(sendBuffer);
                    }
                }

                // Other data extraction/function section
                if ((takeDataNextPacketFlag == 1) & (removeFirstByte == 0))
                {
                    // Save template data
                    if (length == 4096)
                    {
                        takeDataNextPacketFlag = 0;
                        // print('Dart:');
                        // print(String.fromCharCodes(templateBuffer.toList()));
                    } else if (i != 39) // Not take '
                    {
                        templateBuffer[length] = i;
                        length += 1;
                    }
                } else if ((removeFirstByte == 1) & (i == 98)) //98 is 'b'
                {
                    removeFirstByte = 0;
                }
            }
        }

        // Check message section
        int dataPosition = checkIsMessage(data, 'OKDOWNLOAD');
        if ((dataPosition != -1) & (takeDataNextPacketFlag == 0))
        {
            // Signal take fingerprint template
            takeDataNextPacketFlag = 1;
            removeFirstByte = 1;
            length = 0;
        }

        if (checkIsMessage(data, 'FINGERREQUEST') != -1)
        {
            // Start listening to see if user want to cancle operation
            if (subscription.isPaused)
            {
                subscription.resume();
            }
        } else if ((checkIsMessage(data, 'OKIMAGE') != -1) | (checkIsMessage(data, 'READTEMPLATE') != -1))
        {
            // If finger is taken successfully, stop
            if (!subscription.isPaused)
            {
                subscription.pause();
            }
        }
    });

    fingerprintPort.dispose();
}

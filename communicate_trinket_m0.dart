import 'package:libserialport/libserialport.dart';
import 'dart:io';
import 'dart:typed_data';

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
    Uint8List sendBuffer = stringToUint8List('\r');
    fingerprintPort.write(sendBuffer);

    //Listening for response
    final fingerprintReader = SerialPortReader(fingerprintPort);
    fingerprintReader.stream.listen((data) {
        //print('Received: ${data} ${data.length}');
        for (var i in data)
        {
            if ((i >= 32) & (i < 127) | (i == 10))
            {
                String char = String.fromCharCode(i);
                stdout.write('${char}');
                // > indicate that trinket request input
                if ((char == '>'))
                {
                    String line = stdin.readLineSync() ?? '';
                    if (line.compareTo('stop') == 0)
                    {
                        fingerprintReader.close();
                    }
                    Uint8List sendBuffer = stringToUint8List(line+'\n'+'\r');
                    fingerprintPort.write(sendBuffer);
                }

            }
        }

        //print('');
    });

    fingerprintPort.dispose();
    //print("This ran");
}

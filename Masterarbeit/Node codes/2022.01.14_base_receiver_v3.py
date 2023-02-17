#   Author: Carlos Reyes
#   Created on: 2022.01.14
#   Brief:  Second simple Python code for the Drifter's Communication Board test (reception)
#   Requisites:
#   Working time: 1 hr (21 21:21)
#               1.5 hrs (From v2)

#   TODO
#   High priority
#       -Unpack the data according to TXv2
#   Low Priority: Optimization
#   DONE
#   2022.01.21
#       -   Hex and int prints for received data
#   2022.01.16
#       -   Received from Commboard

#   Notes:  This test code works with the CAN implementation of canio lib. For maximum throughput a implementation of CAN FD should be implemented.
#           Info about structs to format a message: https://docs.python.org/3/library/struct.html#format-strings
#               Currently messages are sent using unsigned int, little-endian and its default padding
#
import board
import time
import neopixel
import digitalio
import struct
import canio

print("Hallo Grom: This is receiver v3")


# If the CAN transceiver has a standby pin, bring it out of standby mode
if hasattr(board, 'CAN_STANDBY'):
    standby = digitalio.DigitalInOut(board.CAN_STANDBY)
    standby.switch_to_output(False)

# If the CAN transceiver is powered by a boost converter, turn on its supply
if hasattr(board, 'BOOST_ENABLE'):
    boost_enable = digitalio.DigitalInOut(board.BOOST_ENABLE)
    boost_enable.switch_to_output(True)

# Use this line if your board has dedicated CAN pins. (Feather M4 CAN and Feather STM32F405)
can = canio.CAN(rx=board.CAN_RX, tx=board.CAN_TX, baudrate=125_000, auto_restart=True, silent=False, loopback=False)
# On ESP32S2 most pins can be used for CAN.  Uncomment the following line to use IO5 and IO6
#can = canio.CAN(rx=board.IO6, tx=board.IO5, baudrate=250_000, auto_restart=True)
#   Specific CANbus identifiers
int_canRcvrId = 0x408
float_timeout = 2.0 #   Timeout in seconds
listener = can.listen(matches=[canio.Match(int_canRcvrId)], timeout=float_timeout)

old_bus_state = None
old_count = -1

#   Enablling red LED
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
#   Enabling the NEOPIXEL power
neop = neopixel.NeoPixel(board.NEOPIXEL, 1)
b_dummyCtrl = digitalio.DigitalInOut(board.NEOPIXEL_POWER)
b_dummyCtrl.switch_to_output(True)

counter = 0


while True:
    bus_state = can.state
    neop.fill((255, 0, 0))
    led.value = False
    if bus_state != old_bus_state:
        print(f"Bus state changed to {bus_state}")
        old_bus_state = bus_state

    message = listener.receive()
    if message is None:
        print("No messsage received within timeout")
        continue
    # A message was received!
    neop.fill((0, 255, 0))
    led.value = True
    data = message.data
    if len(data) != 8:
        print(f"Unusual message length {len(data)}")
        continue



    #   Unpacking raw data
    print(f"Unpacked data as second segment is: ")
    canDataPacketX = struct.unpack('<hhhh',data)
    print(" ".join(str(n) for n in canDataPacketX))

    print(f"Unpacked data as third segment is: ")
    canDataPacketX = struct.unpack('<hhf',data)
    print(" ".join(str(n) for n in canDataPacketX))

    print(f"Unpacked data as fourth segment is: ")
    canDataPacketX = struct.unpack('<ff',data)
    print(" ".join(str(n) for n in canDataPacketX))

    print(" ".join(hex(n) for n in data))
    data2 = struct.unpack('<BBBBBBBB',data)
    print(f"Unpacked little-endian is:")

    #   Periodic print of state
    if counter%20==0:
        print(f"Current Bus state {bus_state}")


    #   Default sleep time
    time.sleep(0.5)
    counter = (counter+1)%20



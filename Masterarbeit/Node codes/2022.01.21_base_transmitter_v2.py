#   Author: Carlos Reyes
#   Created on: 2021.12.18
#   Brief:  Simple Python code for the Drifter's Communication Board test
#   Version: 2.0
#   Requisites:
#   Working time:   4.5 hrs (as for 2022.01.31)
#                   6 hrs (From V1)
#   TODO
#   High Priority: Test framework
#       

#
#   Low Priority: Optimization
#       -   Update the  Msg ID fo receiver
#       -   Characterize the maximum transmission speed
#       -   Add a function that would divide the data to be sent into packets of 8 bytes each
#       -   Send data only if Ack received from the bus (with fix destination) Use remoteTransmissionRequest?
#
#   DONE
#       2022.01.30
#           - Node ID updated
#           -Dummy data added as an example
#           -   Compare data at receiver nodo -- OK
#       2022.01.21
#           -Send data chunk as specified in: http://jira.ha.tuhh.de:8090/display/PRJMES/CAN+Tests?src=contextnavpagetreemode
#           -Write an array with identifiers and config bytes (constant)
#           -Array of integers and floats of constant size (afterways can be extended) (failed review)
#           -Write on them
#           -Pack them in one single object
#           -divide them into 8 bytes parts
#           -Send 4 of them
#       2022.01.16
#       -   Try sending messages on 3v3 level
#
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

print("Hallo Grom")

#   Initial config
# If the CAN transceiver has a standby pin, bring it out of standby mode
if hasattr(board, "CAN_STANDBY"):
    print("CAN was on STANDBY")
    standby = digitalio.DigitalInOut(board.CAN_STANDBY)
    standby.switch_to_output(False)
# If the CAN transceiver is powered by a boost converter, turn on its supply
if hasattr(board, "BOOST_ENABLE"):
    boost_enable = digitalio.DigitalInOut(board.BOOST_ENABLE)
    boost_enable.switch_to_output(True)    #True if 5V

can = canio.CAN(rx=board.CAN_RX, tx=board.CAN_TX, baudrate=125_000, auto_restart=True)
monitorBusState = canio.BusState

#   Specific CANbus identifiers
#   Total size 32 bytes for version 1
int_nodeTxMsgId = 0x111   #   Filter that commboard is listening to
#   Data size should be kept as specified, otherwise inconsistencies may occur.
#--- 1 - 8 bytes
uchar_nodeID = 0x11         #   Not larger than 7F. See documentation. Filters: Rx = 0x110 Tx = 0x111
uchar_version = 0x01
uchar_intFlag = 0x01
uchar_nrOfInt = 0x03
uchar_floatFlag = 0x01
uchar_nrOfFloat = 0x03
uchar_command = 0x00
uchar_reserved01 = 0xF0
#   Payload
#--- 9 - 16 bytes
short_int0 = 0x00
short_int1 = 0x00
short_int2 = 0x00
short_reserved00 = 0x0FFF
#--- 17 - 24 bytes
short_reserved01 = 0x0FFF
short_reserved02 = 0x0FFF
float_float0 = 0.0
#--- 25 - 32 bytes
float_float1 = 0.0
float_float2 = 0.0
#--- 33 - 40 bytes
#   Not implemented
#--- 41 - 48 bytes
#   Not implemented
#--- 49 - 56 bytes
#   Not implemented
#--- 57 - 64 bytes
#   Not implemented


#   Enablling red LED
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
#   Enabling the NEOPIXEL power
neop = neopixel.NeoPixel(board.NEOPIXEL, 1)
b_dummyCtrl = digitalio.DigitalInOut(board.NEOPIXEL_POWER)
b_dummyCtrl.switch_to_output(True)

#   Some print variables
old_bus_state = None
count = 0
#   Some user variables variables
user_int0 = 0
user_float0 = 0.0

#   Some useful data

print(f"Node's ID (dec): ",uchar_nodeID)
print(f"Node's CAN Packet version: ",uchar_version)
print(f"Node's TX MSG ID: ",int_nodeTxMsgId)

#   This is the main execution loop
while True:
    # print("Hey Grom!!")
    neop.fill((255, 0, 0))
    led.value = True
    # ------------------------------
    #   User modifies the intx or floatx according to limits. Do not go beyond their defined size.
    #--------------------------------

    #   Example: This only increases the value of one integer and one float (no overflow).
    user_int0 += 10
    if user_int0 > 100:
        user_int0 = -100

    user_float0 += 10.5
    if user_float0 > 100.0:
        user_float0 = -100.0

    #   Copying the user data to common can data packets
    short_int0 = user_int0
    short_int1 = user_int0+10
    short_int2 = user_int0+20
    float_float0 = user_float0
    float_float1 = user_float0+.5
    float_float2 = user_float0-5.25

    #--------------------------------
    #   Here finishes space for user's modification
    # -------------------------------
    
    
    #   Monitoring the state of the device
    bus_state = can.state
    if bus_state != old_bus_state:
        print(f"Bus state changed to {bus_state}")
        old_bus_state = bus_state

    #   Total size 32 bytes for version 1

    #   Packing up the common CAN data packets
    canDataPacket0 = struct.pack("<BBBBBBBB",
                                            uchar_nodeID,
                                            uchar_version,
                                            uchar_intFlag,
                                            uchar_nrOfInt,
                                            uchar_floatFlag,
                                            uchar_nrOfFloat,
                                            uchar_command,
                                            uchar_reserved01)
    canDataPacket1 = struct.pack("<hhhh",
                                            short_int0,
                                            short_int1,
                                            short_int2,
                                            short_reserved00)
    canDataPacket2 = struct.pack("<hhf",
                                            short_reserved01,
                                            short_reserved02,
                                            float_float0)
    canDataPacket3 = struct.pack("<ff",
                                            float_float1,
                                            float_float2)

    canDataPacket = (canDataPacket0, canDataPacket1, canDataPacket2, canDataPacket3)

    if bus_state == monitorBusState.ERROR_ACTIVE or True:   #   Always send over CAN
        now_ms = (time.monotonic_ns() // 1_000_000) & 0xFFFFFFFF
        print(f"Sending message: count={count} now_ms={now_ms}")

        print("Message to be sent:")
        for i in range(4):
            print("".join(hex(n) for n in canDataPacket[i]))
        for i in range(4):
            message = canio.Message(
                id=int_nodeTxMsgId, data = canDataPacket[i]
            )
            can.send(message)
            #time.sleep(0.2)    #   No delay between the 8-bytes segments


        #   Simple print of the state every 5 messages
        count += 1
        if count % 5 == 0:
            print(f"Current bus state{bus_state}")
    else:
        print(f"No message will be sent as the bus is not active")

    # ------------------------------
    led.value = False
    neop.fill((0, 0, 255))
    time.sleep(6)   #  Each 2 seconds sends a new common can data packet

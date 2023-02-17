#   Author: Carlos Reyes
#   Created: 2022.01.29
#   Brief:  Reads out a SBD file received from a Mobile Originated Message according to v1 of AMUSED's communication Prototype


import struct

#   Open the desired .sbd file
f= open(r"example_file5.sbd",'rb')
content = f.read()
print("Hallo Amused User!")
print("This is the binary content of the SBD file:")
print(content)
f.close()
canDataPacketX = struct.unpack_from('BBBBBBBBhhhhhhfffBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB',content,0)
print("This is the tuple that contains the decoded 70-bytes-data according to V1 of the data packet:")
print(canDataPacketX)

#!/usr/bin/env python
# started from # starter code: https://github.com/abencz/python_socketcan/blob/master/python_socketcan_example.py
# Thank you Alex Bencz!
# Copyright (c) 2017 melissa alleyne
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import socket
import argparse
import struct
import errno
import collections # mna - circular buffer use
import json


class CANSocket(object):
  FORMAT = "<IB3x8s" # byte order  - < = little endian | I = unsigned int (can id) | B = unsigned char | 3x = padding 3 | 8s = 8-byte string
  FD_FORMAT = "<IB3x64s" # byte order  - < = little endian | I = unsigned int (can id) | B = unsigned char | 3x = padding 3 | 64s = 64-byte string
  CAN_RAW_FD_FRAMES = 5

  def __init__(self, interface=None):
    self.sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
    if interface is not None:
      self.bind(interface)

  def bind(self, interface):
    self.sock.bind((interface,))
    self.sock.setsockopt(socket.SOL_CAN_RAW, self.CAN_RAW_FD_FRAMES, 1)

  #def send(self, cob_id, data, flags=0):
  #  cob_id = cob_id | flags
  #  can_pkt = struct.pack(self.FORMAT, cob_id, len(data), data)
  #  self.sock.send(can_pkt)

  def recv(self, flags=0):
    can_pkt = self.sock.recv(72) #mna - read call will block for 72 seconds

    if len(can_pkt) == 16:
      cob_id, length, data = struct.unpack(self.FORMAT, can_pkt) 
    else:
      cob_id, length, data = struct.unpack(self.FD_FORMAT, can_pkt)

    # mna - Begin
    # our CAN messages have only three values we care about - 
    # the type of msg, the value of the msg, timestamp of message
    # our can msg type is specified by the cob_id
    # the first 4 bytes of data is the timestamp (unsigned)
    # the second 4 bytes of data is the value (signed)
    #
    # raspberry pi stores data in little endian e.g.
    # 0x1122334455667788 normal order
    # Timestamp | 4 bytes | (unsigned) - 88776655
    # Value | 4 bytes (signed) - 44332211

    timestamp, value = struct.unpack('<Ii', data)
    # mna - End


    cob_id &= socket.CAN_EFF_MASK # mna - If sending a CAN packet with an extended (29 bit) CAN-ID, the “Identifier extension bit” needs to be set
    return (cob_id, data[:length], timestamp, value) # mna - trim to the actual length received based on the length field from the packet

    


# ------------ Outside of class -------------

def format_data(data):
    return ''.join([hex(byte)[2:] for byte in data])


#def generate_bytes(hex_string):
#    if len(hex_string) % 2 != 0:
#      hex_string = "0" + hex_string
#
#    int_array = []
#    for i in range(0, len(hex_string), 2):
#        int_array.append(int(hex_string[i:i+2], 16))
#
#    return bytes(int_array)


#def send_cmd(args):
#    try:
#      s = CANSocket(args.interface)
#    except OSError as e:
#      sys.stderr.write('Could not send on interface {0}\n'.format(args.interface))
#      sys.exit(e.errno)
#
#    try:
#      cob_id = int(args.cob_id, 16)
#    except ValueError:
#      sys.stderr.write('Invalid cob-id {0}\n'.format(args.cob_id))
#      sys.exit(errno.EINVAL)
#
#    s.send(cob_id, generate_bytes(args.body), socket.CAN_EFF_FLAG if args.extended_id else 0)



# mna CAN-related functions BEGIN
def listen_cmd(args):
    try:
      s = CANSocket(args.interface)
    except OSError as e:
      sys.stderr.write('Could not listen on interface {0}\n'.format(args.interface))
      sys.exit(e.errno)

    print('Listening on {0}'.format(args.interface))

    while True:
        cob_id, data, timestamp, value = s.recv() #mna
        print('%s %03x#%s' % (args.interface, cob_id, format_data(data)))
        print('timestamp = %s | value = %s' % (timestamp, value))
        insertCanMsg(cob_id, timestamp, value)



def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    #send_parser = subparsers.add_parser('send', help='send a CAN packet')
    #send_parser.add_argument('interface', type=str, help='interface name (e.g. vcan0)')
    #send_parser.add_argument('cob_id', type=str, help='hexadecimal COB-ID (e.g. 10a)')
    #send_parser.add_argument('body', type=str, nargs='?', default='',
    #  help='hexadecimal msg body up to 8 bytes long (e.g. 00af0142fe)')
    #send_parser.add_argument('-e', '--extended-id', action='store_true', default=False,
    #  help='use extended (29 bit) COB-ID')
    #send_parser.set_defaults(func=send_cmd)

    listen_parser = subparsers.add_parser('listen', help='listen for and print CAN packets')
    listen_parser.add_argument('interface', type=str, help='interface name (e.g. vcan0)')
    listen_parser.set_defaults(func=listen_cmd)

    return parser.parse_args()

# mna CAN-related functions END


# mna Circular Buffer-related functions BEGIN
circularBuffer = collections.deque(maxlen = 100) # - mna what's a good length here?

#read CAN message and store in circular buffer
def insertCanMsg(cob_id, timestamp, value): #mna
    jsonCanMsg = jsonifyCanMsg(cob_id, timestamp, value)
    circularBuffer.append(jsonCanMsg) # mna insert to the right of the circ buf. when the buf is full items on the left will drop off to make room for new items coming in on the right

def serveCanMsg(): #mna
    jsonCanMsg = circularBuffer.popleft() # mna pull off the oldest msg first
    #serve on websockets


# mna - check
def jsonifyCanMsg(cob_id, timestamp, value): #mna
    jsonresult = { cob_id : 
                    { "timestamp" : timestamp,
                      "value" : value
                     } 
                  } 

    return json.dumps(jsonresult)

    
# mna Circular Buffer-related functions END

def main():
    args = parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
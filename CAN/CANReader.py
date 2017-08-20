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
import collections # circular buffer use
import json
import threading





class CANSocket(object):
  FORMAT = "<IB3x8s" # byte order  : < = little endian | I = unsigned int (can id) | B = unsigned char | 3x = padding 3 | 8s = 8-byte string
  FD_FORMAT = "<IB3x64s" # byte order : < = little endian | I = unsigned int (can id) | B = unsigned char | 3x = padding 3 | 64s = 64-byte string
  CAN_RAW_FD_FRAMES = 5

  def __init__(self, interface=None):
    self.sock = socket.socket(socket.PF_CAN, socket.SOCK_RAW, socket.CAN_RAW)
    if interface is not None:
      self.bind(interface)

  def bind(self, interface):
    self.sock.bind((interface,))
    self.sock.setsockopt(socket.SOL_CAN_RAW, self.CAN_RAW_FD_FRAMES, 1)


  # unpack can msg
  def recv(self, flags=0):
    can_pkt = self.sock.recv(72) # read call will block for 72 seconds

    if len(can_pkt) == 16:
      cob_id, length, data = struct.unpack(self.FORMAT, can_pkt) 
    else:
      cob_id, length, data = struct.unpack(self.FD_FORMAT, can_pkt)

  
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

    cob_id &= socket.CAN_EFF_MASK # If sending a CAN packet with an extended (29 bit) CAN-ID, the “Identifier extension bit” needs to be set
    return (cob_id, data[:length], timestamp, value) # trim to the actual length received based on the length field from the packet

# ------------- Outside of class -------------








# ------------- Read & Parse CAN messages related functions BEGIN -------------

def format_data(data):
    return ''.join([hex(byte)[2:] for byte in data])


# read can msg as binary and store in circular buffer as json message
def listen(interface):
    try:
      s = CANSocket(interface)
    except OSError as e:
      sys.stderr.write('Could not listen on interface {0}\n'.format(interface))
      sys.exit(e.errno)

    print('Listening on {0}'.format(interface))

    while True:
        cob_id, data, timestamp, value = s.recv()
        print('%s %03x#%s' % (interface, cob_id, format_data(data)))
        print('timestamp = %s | value = %s' % (timestamp, value))
        insertCanMsg(cob_id, timestamp, value)




# ------------- Circular Buffer-related functions BEGIN -------------

circularBuffer = collections.deque(maxlen = 1000) # - TODO what's a good length here?
lock = threading.Lock()

# package can message id, timestamp, and value as json
# and store in circular buffer
def insertCanMsg(cob_id, timestamp, value):
    jsonCanMsg = jsonifyCanMsg(cob_id, timestamp, value)
    
    lock.acquire()
    try:
      circularBuffer.append(jsonCanMsg) # insert to the right of the circ buf. when the buf is full items on the left will drop off to make room for new items coming in on the right
    finally:
      lock.release()



def serveCanMsg(): 
    result = createEmptyJsonCanMsg()
    if len(circularBuffer) <= 0:
      return result 
    

    lock.acquire()
    try:
      result = circularBuffer.popleft() # pull off the oldest msg first
    finally:
      lock.release()

    return result

def createEmptyJsonCanMsg():
    jsonresult = { -1 : 
                    { "timestamp" : -1,
                      "value" : -1
                     } 
                  } 
    return json.dumps(jsonresult)
                  

def jsonifyCanMsg(cob_id, timestamp, value):
    jsonresult = { cob_id : 
                    { "timestamp" : timestamp,
                      "value" : value
                     } 
                  } 

    return json.dumps(jsonresult)

    



# ------------- Main function BEGIN -------------

def main():
    threading.Thread(target=listen, kwargs={"interface":"can0"}).start() #hardcode interface to be can0


if __name__ == '__main__':
    main()
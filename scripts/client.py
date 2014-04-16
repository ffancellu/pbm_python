#-*- coding:utf-8 -*-

import zmq

context = zmq.Context()

#  Socket to talk to server
print("Connecting to the server to get the sentences analyzed...")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:3001")

#  Do 10 requests, waiting each time for a response
request = "This is ."
print("Sending request: %s …" % request)
socket.send(request)

#  Get the reply.
message = socket.recv()
print("Received reply %s" % (message))
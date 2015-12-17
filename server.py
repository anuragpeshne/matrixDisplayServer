import RPi.GPIO as GPIO
import time
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import json

# HW pins configuration
# We are using two 3 X 8 demux to control 8 X 8 matrix
# anode side
anode = {
    'a0' : 26,
    'a1' : 19,
    'a2' : 13
}

# cathode side
cathode = {
    'a0' : 21,
    'a1' : 20,
    'a2' : 16
}

enable = 4

# some constants
LED_ROWS = 8
LED_COLS = 8
DELAY = 0.001
PRINT_ITERATION = 80
PORT = 8000

def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    for wire, port in anode.iteritems():
        GPIO.setup(port, GPIO.OUT)
        GPIO.output(port, 0);

    for wire, port in cathode.iteritems():
        GPIO.setup(port, GPIO.OUT)
        GPIO.output(port, 0);

    GPIO.setup(enable, GPIO.OUT)
    GPIO.output(enable, 1)

# this method only works for numbers upto 8!
# find something better or add entries according to your demux
def convToBin(input):
    table = [[0,0,0], [0,0,1], [0,1,0], [0,1,1], [1,0,0,], [1,0,1,], [1,1,0,], [1,1,1,]]
    return table[input]

def testLEDs():
    times = 0
    while times < 100:
        i = times % LED_ROWS
        binRep = convToBin(i)
        GPIO.output(cathode['a0'], binRep[2])
        GPIO.output(cathode['a1'], binRep[1])
        GPIO.output(cathode['a2'], binRep[0])
        for j in range(LED_ROWS):
            binRep = convToBin(j)
            GPIO.output(anode['a0'], binRep[2])
            GPIO.output(anode['a1'], binRep[1])
            GPIO.output(anode['a2'], binRep[0])
            time.sleep(.01)
        times = times + 1

def cleanup():
    GPIO.cleanup()

def draw(matrix):
    assert not isinstance(matrix, basestring) # make sure we have been passed an array
    assert len(matrix) == LED_ROWS # asset the dimension of array
    assert len(matrix[0]) == LED_COLS

    for row in range(LED_ROWS):
        for col in range(LED_COLS):
            if matrix[row][col] == 1:
                selectRow(row)
                selectColumn(col)
                time.sleep(DELAY) # we assume loop takes 0 time

def selectRow(row):
    enableLine(row, cathode)

def selectColumn(col):
    enableLine(col, anode)

def enableLine(line, polarity):
    binRep = convToBin(line)
    GPIO.output(polarity['a0'], binRep[2])
    GPIO.output(polarity['a1'], binRep[1])
    GPIO.output(polarity['a2'], binRep[0])

class ServerHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))
        self.send_response(200)
        self.end_headers()

        data = json.loads(self.data_string)
        for d in range(1000):
            draw(data)
        return

init()
testLEDs()
httpd = SocketServer.TCPServer(("", PORT), ServerHandler)
httpd.serve_forever()
cleanup()

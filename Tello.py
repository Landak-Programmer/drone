import socket
import threading
import time
from cv2 import cv2
import datetime
import os

import libh264decoder
import numpy as np


class Tello:
    # constant var
    _prod = 'PROD'
    _UAT = 'UAT'

    _takeoff = 'takeoff'
    _land = 'land'
    _stop = 'stop'

    _telloIp = '192.168.10.1'
    _localIp = ''
    _localPort = 8889
    _telloPort = 8889
    _timeout = .5
    _videoPort = 11111

    _imagePath = './img/'

    # For now we hard coded speed. I too lazy to do
    # 100 cm (1 meter)
    _defaultSpeed = 100

    def __init__(self, mode):

        # set mode
        self.mode = mode

        # tello local var
        self.isPreplan = False

        self.decoder = libh264decoder.H264Decoder()
        self.res = None
        self.frame = None
        self.is_freeze = False
        self.last_frame = None
        self.last_height = 0
        self.telloAddress = (self._telloIp, self._telloPort)

        # socket
        self.cmdSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.videoSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind cmd port
        self.cmdSocket.bind((self._localIp, self._localPort))

        # Read thread
        self.readThread = threading.Thread(target=self._readResponse)
        self.readThread.daemon = True
        self.readThread.start()

        # Cmd to initiate video
        self.cmdSocket.sendto(b'command', self.telloAddress)
        self.cmdSocket.sendto(b'streamon', self.telloAddress)

        # Bind video port
        self.videoSocket.bind((self._localIp, self._videoPort))

        # Video thread
        self.videoThread = threading.Thread(target=self._readVideoFeed)
        self.videoThread.daemon = True
        self.videoThread.start()

    # --- All command are here ---

    def startCmd(self):
        return self._sendCommand(self._takeoff)

    def stopCmd(self):
        return self._sendCommand(self._land)

    def pauseCmd(self):
        return self._sendCommand(self._stop)

    def turnClockwiseCmd(self):
        return self._sendCommand('cw 90')

    def turnAntiClockWisetCmd(self):
        return self._sendCommand('ccw 90')

    def upCmd(self):
        return self._moveCmd('up')

    def downCmd(self):
        return self._moveCmd('down')

    def forwardCmd(self):
        return self._moveCmd('forward')

    def backCmd(self):
        return self._moveCmd('back')

    def leftCmd(self):
        return self._moveCmd('left')

    def rightCmd(self):
        return self._moveCmd('right')

    def _moveCmd(self, direction):
        return self._sendCommand('%s %s' % (direction, self._defaultSpeed))

    def takePictureCmd(self):
        ts = datetime.datetime.now()
        filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
        p = os.path.sep.join((self._imagePath, filename))
        cv2.imwrite(p, cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR))

    def preplanCmd(self):
        # avoid multiple override
        if self.isPreplan is False:
            self.isPreplan = True
            self.preplanInitThread()

    # --- End of command ---

    # --- All utils are here ---

    def _sendCommand(self, command):
        if self.isPreplan is True:
            return self._sendCommandWithOverride(command, True)
        else:
            return self._sendCommandWithOverride(command)

    def _sendCommandWithOverride(self, command, override=False):

        if override is True:
            self._preplanTerminate()

        self.cmdSocket.sendto(command.encode('utf-8'), self.telloAddress)

        time.sleep(self._timeout)

        if self.mode is self._prod:
            if self.res is None:
                res = 'No response...'
            else:
                res = self.res.decode('utf-8')
        else:
            res = command

        self.res = None

        return res

    def _h264_decode(self, packet_data):
        res_frame_list = []
        frames = self.decoder.decode(packet_data)
        for framedata in frames:
            (frame, w, h, ls) = framedata
            if frame is not None:
                # print 'frame size %i bytes, w %i, h %i, linesize %i' % (len(frame), w, h, ls)
                frame = np.fromstring(frame, dtype=np.ubyte, count=len(frame), sep='')
                frame = (frame.reshape((h, ls / 3, 3)))
                frame = frame[:, :w, :]
                res_frame_list.append(frame)
        return res_frame_list

    def _readResponse(self):
        while True:
            try:
                self.response = self.cmdSocket.recvfrom(3000)
            except socket.error as exc:
                # catch exception
                print ("%s" % exc)

    def _readVideoFeed(self):
        packet_data = ""
        while True:
            try:
                res_string, ip = self.videoSocket.recvfrom(2048)
                packet_data += res_string
                if len(res_string) != 1460:
                    for frame in self._h264_decode(packet_data):
                        self.frame = frame
                    packet_data = ""

            except socket.error as exc:
                print ("%s" % exc)

    # --- End of utils ---

    # --- Preplan ---

    def preplanInitThread(self):
        self.preplanLock = True
        self.preplanThread = threading.Thread(target=self._preplanThreadStart)
        # probably dangerous
        self.preplanThread.daemon = True
        self.preplanThread.start()

    def _preplanThreadStart(self):
        print('-- Test --')
        print('-- Preplan in progress... --')
        lcIt = 0
        # 5 sec sleep
        while lcIt < 5 and self.preplanLock:
            time.sleep(1)
            lcIt += 1
        if lcIt is 5:
            print('-- Preplan successful! --')
        else:
            print('-- Preplan terminate! --')
        self.preplanLock = False
        self.isPreplan = False

    def _preplanTerminate(self):
        self.preplanLock = False

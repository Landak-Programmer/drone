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
    _defaultdistance = 100

    # reverse map
    reverseMap = {'up 100': 'down 100', 'down 100': 'up 100',
                  'cw 90': 'ccw 90', 'ccw 90': 'cw 90',
                  'forward 100': 'back 100', 'back 100': 'forward 100',
                  'left 90': 'right 90', 'right 90': 'left 90'}

    def __init__(self, mode):

        # set mode
        self.mode = mode

        # tello is on local flag
        self.on = False

        # tello local var
        self.isPreplan = False
        self.res = None
        self.frame = None

        self.decoder = libh264decoder.H264Decoder()
        self.telloAddress = (self._telloIp, self._telloPort)

        self.trace = []
        self.isReverting = False

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
        self.on = True
        return self._sendCommand(self._takeoff)

    def stopCmd(self):
        self.on = False
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

    def _moveCmd(self, direction, distance=None):
        if distance is None:
            return self._sendCommand('%s %s' % (direction, self._defaultdistance))
        else:
            return self._sendCommand('%s %s' % (direction, distance))

    def takePictureCmd(self):
        lastFrame = self.getFrame()
        return self._processSaveImage(lastFrame)

    def _processSaveImage(self, lastFrame):
        now = datetime.datetime.now()
        filename = "{}.jpg".format(now.strftime("%Y-%m-%d_%H-%M-%S"))
        p = os.path.sep.join((self._imagePath, filename))
        cv2.imwrite(p, cv2.cvtColor(lastFrame, cv2.COLOR_RGB2BGR))

    def preplanCmd(self):
        # avoid multiple override
        if self.isPreplan is False:
            self.isPreplan = True
            self.preplanInitThread()
        else:
            # revert!
            self.revertMovement()

    # --- End of command ---

    # --- All utils are here ---

    def _sendCommand(self, command):

        if self.isReverting:
            print('DO NOT GIVE COMMAND WHEN REVERTING MOVEMENT!')
            return

        if self.isPreplan is True:
            return self._sendCommandWithOverride(command, True)
        else:
            return self._sendCommandWithOverride(command)

    def _sendCommandWithOverride(self, command, override=False):

        if override is True:
            if self.preplanLock:
                self._preplanOverride()
            # track it
            self.trace.append(command)

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

    def _h264Decoder(self, packetData):
        frameArr = []
        frames = self.decoder.decode(packetData)
        for frameData in frames:
            (frame, w, h, ls) = frameData
            if frame is not None:
                frame = np.fromstring(frame, dtype=np.ubyte, count=len(frame), sep='')
                frame = (frame.reshape((h, ls / 3, 3)))
                frame = frame[:, :w, :]
                frameArr.append(frame)
        return frameArr

    def _readResponse(self):
        while True:
            self.response = self.cmdSocket.recvfrom(3000)

    def getFrame(self):
        return self.frame

    def _readVideoFeed(self):
        resData = ""
        while True:
            res = self.videoSocket.recvfrom(2048)
            resData += res
            if len(res) != 1460:
                for frame in self._h264Decoder(resData):
                    self.frame = frame
                resData = ""

    # --- End of utils ---

    # --- Preplan ---

    def preplanInitThread(self):
        self.preplanLock = True
        self.preplanThread = threading.Thread(target=self._preplanThreadStart)
        # probably dangerous
        self.preplanThread.daemon = True
        self.preplanThread.start()

    def _preplanThreadStart(self):
        print('-- Preplan in progress... --')

        pathArr = ['forward 100', 'ccw 90', 'forward 80', 'ccw 90', 'forward 40', 'ccw 90', 'forward 40', 'cw 90',
                   'forward 60', 'ccw 90', 'forward 40']

        for path in pathArr:
            if self.preplanLock:
                self._sendCommandWithOverride(path)
                time.sleep(1.5)
            else:
                # save state here! Only proceed until
                # it is lock again!
                while not self.preplanLock:
                    # sleep the thread 3 sec
                    time.sleep(3.0)

                # after it get's out meaning preplan can proceed
                time.sleep(1.5)
                self._sendCommandWithOverride(path)

        print('-- Preplan successful! --')

        self.preplanLock = False
        self.isPreplan = False

    def _preplanOverride(self):
        print('-- Preplan Override! --')
        self.preplanLock = False

    def revertMovement(self):

        # while reverting the drone cannot override!
        self.isReverting = True

        for cmd in self.trace:
            rvCmd = self.reverseMap.get(cmd, 'stop')
            print(rvCmd)
            self._sendCommandWithOverride(rvCmd)
            time.sleep(1.5)

        self.isReverting = False
        self.preplanLock = True

        print('-- Revert Successful! --')

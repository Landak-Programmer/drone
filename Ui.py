from tkinter import *
import tkinter as cp
from PIL import Image
from PIL import ImageTk as itk
import time
import threading


class Ui:

    def __init__(self, tello):
        self.cp = cp.Tk()
        self.tello = tello
        self.videoScreen = None
        self.uiOn = True

        # add label on UI

        # - Title -
        title_lbl = cp.Label(text='Drone CP', font='Arial 16 bold')
        title_lbl.pack(side='top', padx=10, pady=10)

        # - Instruction Title -
        instruction_main_lbl = cp.Label(text='Instruction:', justify="left", font='Arial 12 bold')
        instruction_main_lbl.pack(side='top', anchor=cp.W, padx=10, pady=5)

        # - Instruction -
        instruction_child_lbl = cp.Label(text='Use Up, Down, Left and Right button to move the drone\n\n'
                                              'Use W, S, A and D button for control the drone',
                                         justify="left", font='Arial 11')
        instruction_child_lbl.pack(side='top', anchor=cp.W, padx=10, pady=5)

        # add entry box
        self.display = StringVar()
        screen = Entry(self.cp, textvariable=self.display, state=DISABLED)
        screen.pack(side='top', expand="yes", fill="both", padx=10, pady=5)
        screen.config(disabledbackground='white')

        # add button on UI

        # init icon
        self.playIcon = itk.PhotoImage(Image.open('resources\play.png'))
        self.preplanIcon = itk.PhotoImage(Image.open('resources\preplan.png'))
        self.cameraIcon = itk.PhotoImage(Image.open('resources\camera.png'))
        self.pauseIcon = itk.PhotoImage(Image.open('resources\pause.png'))
        self.stopIcon = itk.PhotoImage(Image.open('resources\stop.png'))

        # - Start -
        self.start_btn = cp.Button(self.cp, text="Start", image=self.playIcon, compound="left", relief="raised",
                                   command=lambda: self.updateScreen(tello.startCmd))
        self.start_btn.pack(side="top", fill="both", expand="yes", padx=10, pady=10)
        self.start_btn.config(background='#32CD32')

        # - Preplan -
        self.preplan_btn = cp.Button(self.cp, text="Preplan", image=self.preplanIcon, compound="left", relief="raised",
                                     command=lambda: self.preplanMsg(tello.preplanCmd))
        self.preplan_btn.pack(side="top", fill="both", expand="yes", padx=10, pady=10)

        # - Capture -
        self.snap_btn = cp.Button(self.cp, text="Capture", image=self.cameraIcon, compound="left", relief="raised",
                                  command=lambda: self.updateScreen(tello.takePictureCmd))
        self.snap_btn.pack(side="top", fill="both", expand="yes", padx=10, pady=10)

        # - Pause -
        self.pause_btn = cp.Button(self.cp, text="Pause", image=self.pauseIcon, compound="left", relief="raised",
                                   command=lambda: self.updateScreen(tello.pauseCmd))
        self.pause_btn.pack(side="top", fill="both", expand="yes", padx=10, pady=5)

        # - Stop -
        self.stop_btn = cp.Button(self.cp, text="Stop", image=self.stopIcon, compound="left", relief="raised",
                                  command=lambda: self.updateScreen(tello.stopCmd))
        self.stop_btn.pack(side="top", fill="both", expand="yes", padx=10, pady=15)
        self.stop_btn.config(background='#ED2939')

        # - Arrow key -
        self.key = cp.Frame(width=100, height=2)
        self.key.bind('<KeyPress-Up>', lambda event,: self.keyAction(tello.upCmd))
        self.key.bind('<KeyPress-Down>', lambda event,: self.keyAction(tello.downCmd))
        self.key.bind('<KeyPress-Left>', lambda event,: self.keyAction(tello.turnAntiClockWisetCmd))
        self.key.bind('<KeyPress-Right>', lambda event,: self.keyAction(tello.turnClockwiseCmd))

        self.key.bind('<KeyPress-w>', lambda event,: self.keyAction(tello.forwardCmd))
        self.key.bind('<KeyPress-s>', lambda event,: self.keyAction(tello.backCmd))
        self.key.bind('<KeyPress-a>', lambda event,: self.keyAction(tello.leftCmd))
        self.key.bind('<KeyPress-d>', lambda event,: self.keyAction(tello.rightCmd))
        self.key.pack(side="bottom")
        self.key.focus_set()

        # Video thread
        self.videoThread = threading.Thread(target=self.videoThreadStart)
        self.videoThread.start()

        self.cp.wm_title("Control Panel")
        self.cp.geometry("550x550")
        self.cp.wm_protocol("WM_DELETE_WINDOW", self.terminateAll)

    # --- All utils ---

    def videoThreadStart(self):
        while self.uiOn:
            while self.tello.on and self.uiOn:
                self.frame = self.tello.readFrame()
                if self.frame is None or self.frame.size is 0:
                    continue
                image = Image.fromarray(self.frame)
                if self.videoScreen is None:
                    self.videoScreen = cp.Label(image=image)
                    self.videoScreen.image = image
                    self.videoScreen.pack(side="left", padx=20, pady=20)
                else:
                    self.videoScreen.configure(image=image)
                    self.videoScreen.image = image

    def keyAction(self, fx):
        # stop movement
        self.tello.stopCmd()
        # FIXME: gap before sending new movement command
        time.sleep(.3)
        # send command
        self.updateScreen(fx)

    def updateScreen(self, fx):
        self.display.set(fx())

    def preplanMsg(self, fx):
        self.display.set('-- Preplan initiate --')
        fx()

    def terminateAll(self):
        self.uiOn = False
        self.cp.quit()

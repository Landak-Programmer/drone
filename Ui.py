from tkinter import *
import tkinter as cp
from PIL import Image
from PIL import ImageTk as itk


class Ui:

    def __init__(self, tello):
        self.cp = cp.Tk()
        self.tello = tello

        # add label on UI

        # - Title -
        title_lbl = cp.Label(text='Drone CP', font='Arial 16 bold')
        title_lbl.pack(side='top', padx=10, pady=10)

        # - Instruction Title -
        instruction_main_lbl = cp.Label(text='Instruction:', justify="left", font='Arial 12 bold')
        instruction_main_lbl.pack(side='top', anchor=cp.W, padx=10, pady=5)

        # - Instruction -
        instruction_child_lbl = cp.Label(text='Use Up, Down, Left and Right button to control the drone',
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
                                     command=lambda: self.updateScreen(tello.preplanCmd))
        self.preplan_btn.pack(side="top", fill="both", expand="yes", padx=10, pady=10)

        # - Capture -
        self.snap_btn = cp.Button(self.cp, text="Capture", image=self.cameraIcon, compound="left", relief="raised",
                                  command=lambda: self.updateScreen(tello.pauseCmd))
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
        self.key.bind('<KeyPress-w>', lambda event,: self.keyAction(tello.upCmd))
        self.key.bind('<KeyPress-s>', lambda event,: self.keyAction(tello.downCmd))
        self.key.bind('<KeyPress-a>', lambda event,: self.keyAction(tello.turnAntiClockWisetCmd))
        self.key.bind('<KeyPress-d>', lambda event,: self.keyAction(tello.turnClockwiseCmd))

        self.key.bind('<KeyPress-Up>', lambda event,: self.keyAction(tello.forwardCmd))
        self.key.bind('<KeyPress-Down>', lambda event,: self.keyAction(tello.backCmd))
        self.key.bind('<KeyPress-Left>', lambda event,: self.keyAction(tello.leftCmd))
        self.key.bind('<KeyPress-Right>', lambda event,: self.keyAction(tello.rightCmd))
        self.key.pack(side="bottom")
        self.key.focus_set()

        self.cp.wm_title("Control Panel")
        self.cp.geometry("500x500")
        self.cp.wm_protocol("WM_DELETE_WINDOW")

    # --- All utils ---

    def keyAction(self, fx):
        # stop movement
        self.tello.stopCmd()
        # send command
        self.updateScreen(fx)

    def updateScreen(self, fx):
        self.display.set(fx())

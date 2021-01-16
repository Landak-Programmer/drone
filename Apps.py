import Tello
from Ui import Ui

# UAT - for testing
# PROD - for real testing
mode = 'UAT'

def main():
    print("Starting....")
    drone = Tello.Tello(mode)
    ui = Ui(drone)
    ui.cp.mainloop()

if __name__ == "__main__":
    main()

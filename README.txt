Hello. And good day.

1) First and foremost, clone the repo
2 ) Go into install folder and pick your machine. Click the following
	- windows : install.bat
	- mac : mac_install
	- linux : linux_install
3) Done.

Troubleshoot:

If you guys have problem, check if you have python in your machine. The installation will install
python 2.7. So there might be some conflict if you have python previously. Try to uninstall and
run the installation again.

------------------------------------------------------------------------------------------------------

So what does this CP can do?

1) Move up, down, cw, and ccw

What is cw and ccw? clockwise and counterclockwise
By default, the movement are 100 cm for movement and 90 degree for cw/ccw
For ex, up 100 means up 100 cm

2) Move forward, back, left, and right

Same, all default 100 cm. Left and right means drone move LEFT and RIGHT. Not rotating like cw

3) Video feed

By using socket, we get response from the tello video port and convert it into image using 264decoder
Sending command also use socket. But different socket. Means we got 2 socket

4) Capture image

Extension from features above, we take the last frame and save it using OpenCv2

5) Preplan

This is the most interesting one. So we can trigger preplan and go through pre coded path
If we click any button (meaning send any command), we can override the preplan and take control
By clicking preplan again, the drone will trace previous path and continue to execute preplan


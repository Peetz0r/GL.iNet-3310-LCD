#GL.iNet + 3310 LCD#


##The hardware##
You basically connect the 3310 LCD pins directly to the GPIO pins of the GL.iNet. I hardwired the CE pin to GND and the led/backlight pin to 3.3V so I needed just 4 GPIO's. You could add a transistor and connect the led trough the 5th GPIO and change the brightness using PWM, but I did not do that.
- http://imgur.com/a/mL6XN
- http://imgur.com/a/PmQAw

I get 18 hours of battery life out of this 5200mAh USB battery pack. Quite impressive, with the backlight on and WiFi enabled all the time :)

##How to run this##
- Get a GL.iNet
- Flash a stock OpenWRT image on it
- Run `opkg install python python-imaging-library`
- If you run LuCI or uHTTPd (or anything really) on port 80, change this to another port
- Place the script, html file and optionally the image in /root (or any directory)
- Edit /etc/rc.local to start the script in the background
- I configured OpenWRT to use wifi as WAN connection with a static IP (not using it as access point) and adding some firewall rules to make port 80 reacable on any interface
- I also use another server as reverse proxy, but mostly just to use a subdomain (name-based virtual host) for this project where I only have one IP address
- Reboot (or manually start the script in the background)
- ...
- PROFIT!

See it live at http://3310.haas-en-berg.nl/ (not 24/7, but close enough)
(currently down because of wifi problems)

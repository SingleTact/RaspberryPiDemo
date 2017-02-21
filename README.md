PPS SingleTact Demo
===================

PREREQUISITES
=============
Linux version for Raspberry Pi 3 is NOOB (Raspbian) shipped with Raspberry Pi 3 SDCARD

On Raspberry Pi, issue these commands to install required packages need to run the SingleTact Demo

```
$ sudo apt-get update
$ sudo apt-get install python-gi-cairo python-smbus i2c-tools
```


RUNNING
=======

Copy 'pps-singletact' binary into the Pi, assuming it was copied in /home/pi directory 
(default password for pi user is 'raspberry')

```
$ cd ~
$ python pps-singletact
```

To reset the graph, long touch at upmost-left screen (near the 700 value)
Or by mouse triple clicks or by SPACE key (keyboard)

By default, I2C (the communication protocol used to communicate with the SingleTact device) is not enabled on the Pi. I2C can be enabled in the raspi-config tool.

```
$ sudo raspi-config
```
Select Advanced Options -> I2C – Enable/Disable automatic loading, and then select yes.

If running Raspbian releases before 3.18 the following config file must be edited.
```
$ sudo nano /etc/modprobe.d/raspi-blacklist.conf 
```
Comment out the following by adding a “#” to the start of each line.
```
blacklist spi-bcm2708
blacklist i2c-bcm2708
```


AUTORUN
=======

append this to /etc/profile

```
$ echo "sudo python pps-singletact.py" | sudo tee -a /etc/profile
```
To exit after autorun you must open up a new virtual terminal by pressing Ctrl + alt + f1
then 

```
$ sudo top
```
kill the python process, usually press k enter and then 9.

then return to desktop with Ctrl + alt + f7





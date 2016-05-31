PPS SingleTact Demo
===================

PREREQUISITES
=============
Linux version for Raspberry Pi 3 is NOOB (Raspbian) shipped with Raspberry Pi 3 SDCARD

On Raspberry Pi, issue these commands to install required packages need to run the SingleTact Demo

```
$ sudo apt-get update
$ sudo apt-get install python-gi-cairo python-smbus
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


AUTORUN
=======

Make sure autologin has been enabled for 'pi' user.
To enable this, goto:

Menu -> Preferences -> Raspberry Pi Configuration -> Auto login

Then, copy the pps-singletact.desktop file into /home/pi/.config/autostart

```
$ cp pps-singletact.desktop /home/pi/.config/autostart
```

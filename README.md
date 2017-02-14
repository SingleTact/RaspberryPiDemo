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

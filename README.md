info-beamer video wall
======================

This example code shows a way to play different fullscreen videos on different
devices at the same time. You can use it (for example) to build a video wall
consisting of four screens each connected to it's own PI.

Preparing the PIs
-----------------

You have to repeat this step for each Pi you want to use.

Install [Raspbian](http://raspbian.org). 
Download [info-beamer for the pi](https://info-beamer.com/pi)
and extract the tar.gz somewhere. This readme assumes
you extracted the tar to `/root/info-beamer-pi`.

Please follow the instructions in `/root/info-beamer-pi/README.txt` to make sure
your Pi has enough video memory available. You can test info-beamer by running:

```
$ /root/info-beamer-pi/info-beamer /root/info-beamer-pi/samples/hello
```

This readme also assumes that this readme and all related files (node.lua,
master.py, ...) are in `/root/videowall`.

Copy the videos(s) you want to display to the directory
`/root/videowall`. Only h264 videos are supported.

Create the file `playlist.txt` and add one or many lines consisting of the video
filenames that should be played. It might look like this:

```
video1-left.mp4,video1-right.mp4
video2-left.mp4,video2-right.mp4
```

The first line tells the system that you want to play `video1-left.mp4` on the
first device and `video1-right.mp4` on the second device at the same time.

Videos should match the aspect ratio of each screen. So don't try to play 4:3
videos on a 16:9 screen. They should also have the same length, otherwise the
screen showing the shorter video will show the last frame of that video until
the other screen(s) complete their video.

You are not limited to only two videos. You can add as many videos in a single
row as you have screens/devices available.

Making sure info-beamer starts after booting
--------------------------------------------

Edit `/etc/rc.local` and add the following line before the existing `exit 0`
line:

```
INFOBEAMER_ADDR=0.0.0.0 /root/info-beamer-pi/info-beamer /root/videowall &
```

This will start info-beamer each time the Pi starts. Make sure you have ssh
access configured for the Pi, otherwise the screen will be black after booting
since info-beamer will show a black screen while waiting for video playback.

Be careful: This setup assumes that your network is trusted. Any machine in the
same network can control which of the provided videos is displayed on each
screen.

Starting playback
-----------------

Once all PIs are configured it's time to start playing videos. One of the PIs
(or any other computer) will act as the master server that coordinates playback.

This readme assumes that one of the previously configured PIs acts as the
master. Start the master program like this:

```
cd /root/videowall
python master.py playlist.txt 192.168.1.50 192.168.1.51
```

This assumes that the PI for the first screen configured uses the IP address
192.168.1.50 and the second one uses 192.168.1.51.  Yours probably have other IP
addresses, so be sure to change those values. You have to provide the same
number of screens as you have videos configured in your `playlist.txt` file.

If this is running successfully you might want to add those lines to
`/etc/rc.local` as well. It might look like this (be sure to change the IP
addresses as well as there number to match your setup) on the master PI
now:

```
INFOBEAMER_ADDR=0.0.0.0 /root/info-beamer-pi/info-beamer /root/videowall &

cd /root/videowall
python master.py playlist.txt 192.168.1.50 192.168.1.51 &
```

Feedback?
---------

Please [get in contact](https://info-beamer.com/doc/about) if you successfully
use this setup or have any questions.

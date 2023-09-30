# How to use `imggrab` if you've never touched Python before

Before starting, run `pk;export` in DMs with PluralKit, and save the file it
gives you somewhere you'll be able to find it later, like your desktop.
This is important - the script won't work without that export file.

**If you're on Windows or macOS**: [download Python from python.org][pydownload]
and install it - you want the latest version (3.11.5 at the time of writing this).

(If you're on Linux, Python is probably already installed - but if you're running
Linux, you probably already know how to run a Python script, so I don't know why
you'd be reading this.)

Download the script by right-clicking on [this link][imggrab-raw] and clicking
"Save link as..." (or similar, depending on your browser). Save it somewhere 
like your desktop, where you'll be able to find it later.

Double-click on the downloaded `imggrab` file on your computer, and you should
see a window pop up like this:

![imggrab window prompting for file](./assets/imggrab-start.png)

At this point, you'll want to do exactly that - drag your PluralKit export file
from a File Explorer / Finder window onto the `imggrab` window, and press Enter.

The script will automatically start downloading all your avatars and banners,
and will place them in a new folder named after your system's 5-character ID,
usually alongside wherever you downloaded the `imggrab.py` file to.

If any error occurs, the error message will show up in that window, and the script
will pause. Take a screenshot of the window, and send that to Iris in the PK Discord.
Pressing Enter at this point will close the window.

[pydownload]: https://python.org/downloads/
[imggrab-raw]: https://raw.githubusercontent.com/u1f408/pkmisc/main/imggrab.py

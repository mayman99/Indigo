Indigo MySensors plugin
=======================
The Indigo MySensors plugin adds interaction with MySensors (see http://www.mysensors.org) to Indigo (see http://www.perceptiveautomation.com).


This plugin is a work in progress and so is the readme...

You can 'play' with the plugin but so far only the ardiuno node, arduino relay, light, temperature and (hopefully) the motion sensor have been implemented.

Installation
============
This plugin is not yet ready for primetime so don't use the plugin on a live system yet!

When you decide to download the plugin you will download a zipped archive named 'indigo-mysensors-master.zip'.
Unzip the archive and rename the forlder to 'MySensors.indigoPlugin'.

When you have Indigo installed the folder will show as a single file (a so called package).
When you doubleclick on the file you will automatically open Indigo (or bring it to the front) and you will be asked if you want to install and enable it.

Attach the Gateway
==================
Next thing should be simple. Create a Gateway from the sample sketch that you most likely already downloaded here (https://github.com/mysensors/Arduino). You need the SerialGateway.ino sketch
After uploading the sketch to your Arduino board you can attach it to your Mac.
You now go to the configuration menu of the plugin (plugins > MySensors > configure) and select the correct port.
Now you are ready to add your devices.

Include devices
===============
Now comes the part that I am not yet really sure about but I took the rather arbitrary (I was alone :)) decision to 
make the plugin so that new devices/boards are recognised always and not only when inclusion mode is activated.
The only thing you really need to do to (re-)activate a device is (re-)start (push button or plug in a power source) it while the devices you want to use is within reach of the MySensors network. This will make the plugin aware of the device and will try to add a node id to the device.

Now you have to watch your event log to see what is going on and wait until the device starts sending out details about its sensor. When the device and its sensors are known (have an id) you can start adding the device to Indigo so you can start using it.

Now click the 'New' button, select the device type 'MySensors', select the device and, when you selected the correct one click the 'Add Device' button. Notice that you actually selected a board and that the sensors are included after clicking the 'Add Device' button. It does not matter how many sensors the board has, they should all appear as long as they are known to the plugin.

Word of advice: It is ok when the board already has a node id but this will make that you are in charge of handing out the id's instead of the plugin and you should really beware of not using a node id twice (and certainly stay away from 0 because this is used for the Gateway by default).

Using triggers, actions etc.
============================
When you are at this point the device behaves similar to what you are used to in Indigo so I am not going to spend many more words than necessary here. Triggers, actions etc. are defined based on what is available for a sensor in MySensors. So this is pretty standard stuff. When you miss something that is available in MySensors but not in the plugin you can either let me know or fork the master and add it yourself.

Menu Items
==========
The following menu items are available:

Toggle Debugging
This works like any other plugin in Indigo.
It toggles debugging output on and off.
And, like with all plugins you should use it with care and/or when you are asked to use it because it can give you an overload of output and slow down your system.

Start Inclusion Mode
This will trigger inclusion mode on the Gateway. Right now, as described above, the only thing it does is activate inclusion mode on your Gateway. The plugin ignores it.

Reload Devices
This will delete all board/sensor metadate stored and used by the plugin.
It does not delete/remove the devices setup within Indigo.
Although the plugin will try to reconnect and recreate your board and sensor metadata you should use it with care.
Three words of advice here:
- Don't do this unless you are asked to when you are unsure.
- Use it when you want to reset the system but you should (in this order): remove devices, reload devices, clear node id's on the board and upload new sketches and start 'fresh'.
- When you use it you should always (re-)activate a board to make it know to the Gateway again or you will end up with a mess.

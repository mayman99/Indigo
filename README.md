indigo-mysensors
================
The Indigo MySensors plugin adds interaction with MySensors (see http://www.mysensors.org) to Indigo (see http://www.perceptiveautomation.com).


This plugin is a work in progress and so is the readme...

You can 'play' with the plugin but so far only the ardiuno node, arduino relay, light, temperature and (hopefully) the motion sensor have been implemented.

Don't use the plugin on a live system yet!

Using the plugin
================
These files is not yet ready to use.
When you really want to you should create a folder on your mac and name it 'MySensors.indigoPlugin'.
When you have Indigo installed the folder will show as a single file that you can doubleclick to activate it in Indigo.

Next thing is simple: Add your MySensors Gateway to your Mac, go to the configuration menu of the plugin and select the correct port. Now you are ready to add your devices.

Restart (push button or plug in a power source) while the devices you want to use is within reach of the MySensors network. This will make Indigo aware of the device and will try to add a node id to the device.
It is ok when the device already has a node id but this will make that you are in charge of handing out the id's instead of the plugin.
Please watch your event log to see what is going on.

When the device is known (has an id) you can start adding it to Indigo.

It does not matter if the device has one or more sensors.
They will all be recognized and added (when the plugin is ready).

Menu Items
==========
Plugins > MySensors >

Toggle Debugging
Works like any other plugin in Indigo.
It toggles debugging output on and off

Start Inclusion Mode
This will trigger inclusion mode on the Gateway.

Reload Devices
This will delete the internally stored devices and not those defined by you within Indigo.

Use it with causion as it will reset everything and remove devices not attached at that present moment.

Also you will have to press the startup/inclusion button on all of your devices or you will get unpredictable results!


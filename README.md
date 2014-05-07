indigo-mysensors
================

The Indigo MySensors plugin adds interaction with MySensors (see http://www.mysensors.org) to Indigo (see http://www.perceptiveautomation.com).


This plugin is a work in progress and so is the readme...

You can 'play' with the plugin but so far only the ardiuno node, arduino relay, light, temperature and (hopefully) the motion sensor have been implemented.

Don't use the plugin on a live system yet!

Menu Items
================
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


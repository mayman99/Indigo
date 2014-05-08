#! /usr/bin/env python
# -*- coding: utf-8 -*-

####################
# MySensors plugin interface for Indigo 6
#
# Copyright (c)2014-2014 Marcel Trapman.
####################
import httplib, urllib, sys, os, threading, glob, time

kOnlineState = "online"
kOfflineState = "offline"

kBaudrate = 115200

kInterval = 5
kWorkerSleep = 1

kMaxNodeId = 255
kMaxChildId = 255

kGatewayId = 0
kBoardNodeId = 255
kBoardChildId = 255

#MESSAGE message types (M_)
kMessageTypes = {
    "PRESENTATION": 0,
    "SET_VARIABLE"	: 1,
    "REQ_VARIABLE"	        : 2,
    "ACK_VARIABLE"	        : 3,
    "INTERNAL"		        : 4
}

#PRESENTATION sensor types (S_)
kSensorTypes = {
    "DOOR" 			        : [0,  "Door"],
    "MOTION" 		        : [1,  "Motion"],
    "SMOKE" 		        : [2,  "Smoke"],
    "LIGHT" 		        : [3,  "Relay"],
    "DIMMER" 		        : [4,  "Dimmer"],
    "COVER" 		        : [5,  "Window"],
    "TEMP" 			        : [6,  "Temperature"],
    "HUM" 			        : [7,  "Humidity"],
    "BARO" 			        : [8,  "Barometer"],
    "WIND" 			        : [9,  "Wind"],
    "RAIN" 			        : [10, "Rain"],
    "UV" 			        : [11, "UV"],
    "WEIGHT" 		        : [12, "Weight"],
    "POWER" 		        : [13, "Power"],
    "HEATER" 		        : [14, "Heater"],
    "DISTANCE" 		        : [15, "Distance"],
    "LIGHT_LEVEL"	        : [16, "Lux"],
    "ARDUINO_NODE"	        : [17, "Arduino Node"],
    "ARDUINO_RELAY"	        : [18, "Arduino Repeater"],
    "LOCK" 			        : [19, "Lock"],
    "IR" 			        : [20, "IR"],
    "WATER" 		        : [21, "Water"]
}

#SET_VARIABLE, REQ_VARIABLE, ACK_VARIABLE sensor variables (V_)
kVariableTypes = {
    "TEMP"			        : [0,  "temperature",   "sensor update to"],
    "HUM"			        : [1,  "humidity",      "sensor update to"],
    "LIGHT"			        : [2,  "onOffState",    "update to"],
    "DIMMER"		        : [3,  "dimmer",        "update to"],
    "PRESSURE"		        : [4,  "barometer",     "update to"],
    "FORECAST"		        : [5,  "barometer",     "update to"],
    "RAIN"			        : [6,  "rain",          "update to"],
    "RAINRATE"		        : [7,  "rain",          "update to"],
    "WIND"			        : [8,  "wind",          "update to"],
    "GUST"			        : [9,  "wind",          "update to"],
    "DIRECTION"		        : [10, "direction",     "update to"],
    "UV"			        : [11, "uv",            "update to"],
    "WEIGHT"		        : [12, "scale",         "update to"],
    "DISTANCE"		        : [13, "distance",      "update to"],
    "IMPEDANCE"		        : [14, "scale",         "update to"],
    "ARMED"			        : [15, "security",      "update to"],
    "TRIPPED"		        : [16, "onoroff",       "update to"],
    "WATT"			        : [17, "energy",        "update to"],
    "KWH"			        : [18, "energy",        "update to"],
    "SCENE_ON"		        : [19, "scene",         "update to"],
    "SCENE_OFF"		        : [20, "scene",         "update to"],
    "HEATER"		        : [21, "user",          "update to"],
    "HEATER_SW"		        : [22, "onoroff",       "update to"],
    "LIGHT_LEVEL"	        : [23, "light",         "update to"],
    "VAR_1"			        : [24, "var",           "update to"],
    "VAR_2"			        : [25, "var",           "update to"],
    "VAR_3"			        : [26, "var",           "update to"],
    "VAR_4"			        : [27, "var",           "update to"],
    "VAR_5"			        : [28, "var",           "update to"],
    "UP"			        : [29, "door",          "update to"],
    "DOWN"			        : [30, "door",          "update to"],
    "STOP"			        : [31, "door",          "update to"],
    "IR_SEND"		        : [32, "ir",            "update to"],
    "IR_RECEIVE"	        : [33, "ir",            "update to"],
    "FLOW"			        : [34, "water",         "update to"],
    "VOLUME"		        : [35, "water",         "update to"],
    "LOCK_STATUS"	        : [36, "lock",          "update to"]
}

#INTERNAL internal messages (I_)
kInternalTypes = {
    "BATTERY_LEVEL"	        : [0,  "battery level"],
    "BATTERY_DATE"	        : [1,  "last battery update"],
    "LAST_TRIP"	            : [2,  "last trip"],
    "TIME"			        : [3,  "time"],
    "VERSION"		        : [4,  "Arduino library version"],
    "REQUEST_ID"	        : [5,  "request id"],
    "INCLUSION_MODE"        : [6,  "inclusion mode"],
    "RELAY_NODE"	        : [7,  "repeater"],
    "LAST_UPDATE"	        : [8,  "last update"],
    "PING"			        : [9,  "ping"],
    "PING_ACK"		        : [10, "ping ack"],
    "LOG_MESSAGE"	        : [11, "log message"],
    "CHILDREN"		        : [12, "children"],
    "UNIT"			        : [13, "unit"],
    "SKETCH_NAME"	        : [14, "sketch name"],
    "SKETCH_VERSION"        : [15, "sketch version"]
}

#VALIDATION return values crc check of received message
kValidationTypes = {
    "VALIDATE_OK"	        : 0,
    "VALIDATE_BAD_CRC"	    : 1,
    "VALIDATE_BAD_VERSION"	: 2
}

class Plugin(indigo.PluginBase):

    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)

        self.debug                  = False
        self.inclusionMode          = False

        self.connection             = None
        self.connectionAttempts     = 0

        self.interval               = kInterval

        self.devices                = indigo.Dict()
        self.nodeIds                = indigo.Dict()

    def __del__(self):
        indigo.PluginBase.__del__(self)

    def startup(self):
        self.debug = self.pluginPrefs.get("showDebugInfo", False)

        self.debugLog(u"Connecting...")

        self.address = self.pluginPrefs["address"]
        self.unit = self.pluginPrefs.get("unit", "M")

        result = False

        while not result and self.connectionAttempts < 6:
            result = self.openConnection()

            self.sleep(kWorkerSleep)

        if not result:
            indigo.server.log \
                (u"Permanently failed connecting at address: %s (baudrate: %s)" % (self.address, kBaudrate))

        self.loadDevices()

    def shutdown(self):
        self.debugLog(u"Disconnecting...")

        if self.connection:
            self.connection.close()

        #self.pluginPrefs["devices"] = self.devices

    def deviceStartComm(self, indigoDevice):
        self.debugLog(u"Device started: \"%s\" %s" % (indigoDevice.name, indigoDevice.id))
        pass

    def deviceStopComm(self, indigoDevice):
        self.debugLog(u"Device stopped: \"%s\" %s" % (indigoDevice.name, indigoDevice.id))

        try:
            deviceId = indigoDevice.id

            if not deviceId in indigo.devices:
                properties = indigoDevice.pluginProps

                address = self.getAddress(address = properties["address"])

                device = self.devices[address]

                device["id"] = ""

                self.devices[address] = device
        except:
            pass

    def didDeviceCommPropertyChange(self, oldIndigoDevice, indigoDevice):
        return True

    def update(self):
        self.debugLog(u"Update method called")

        try:
            self.readMessage()
        except reference.CommandError:
            return

    def runConcurrentThread(self):
        self.debugLog(u"Running thread")

        try:
            while True:
                if self.connection and self.connection.isOpen():
                    self.processIncoming()

                self.sleep(self.interval)
        except self.StopThread:
            pass

    ########################################
    # DeviceFactory methods (specified in Devices.xml)
    ########################################
    def getDeviceGroupList(self, filter, valuesDict, deviceIdList):
        menuItems = []

        for deviceId in deviceIdList:
            if deviceId in indigo.devices:
                indigoDevice = indigo.devices[deviceId]

                deviceName = indigoDevice.name
            else:
                deviceName = u"- device not found -"

            menuItems.append((deviceId, deviceName))

        return menuItems

    def getVariableValue(self, field, value):
        if not field:
            return None

        if field == "onOffState":
            if value == None:
                return 0
            else:
                return int(value)

        return None

    def getAvailableDevices(self, filter, valuesDict, deviceIdList):
        menuItems = []

        for address in self.devices:
            device = self.devices[address]

            identifiers = self.getIdentifiers(address)

            nodeId = identifiers[0]
            childId = identifiers[1]

            if childId == kBoardChildId and self.hasChildren(nodeId):
                try:
                    if not device["id"]:
                        deviceName = "%s" % nodeId

                        if device["model"]:
                            deviceName = "%s - %s" % (deviceName, device["model"])
                        else:
                            try:
                                deviceName = "%s - %s" % (deviceName, self.getSensorName(device["type"]))
                            except:
                                pass

                        if device["modelVersion"]:
                            deviceName = "%s (%s)" % (deviceName, device["modelVersion"])

                        menuItems.append((nodeId, deviceName))
                except:
                    pass

        return menuItems

    def addIndigoDevice(self, valuesDict, deviceIdList):
        self.debugLog(u"addIndigoDevice deviceIdList: %s" % deviceIdList)

        nodeId = -1

        try:
            nodeId = int(valuesDict["selecteddevice"])

            if nodeId > -1:
                self.addIndigoChildren(nodeId)
        except:
            pass

        return valuesDict

    def getDeviceFactoryUiValues(self, devIdList):
        valuesDict = indigo.Dict()
        errorMsgDict = indigo.Dict()

        return (valuesDict, errorMsgDict)

    def validateDeviceFactoryUi(self, valuesDict, devIdList):
        errorsDict = indigo.Dict()

        return (True, valuesDict, errorsDict)

    def validateDeviceConfigUi(self, valuesDict, typeId, devId):
        return (True, valuesDict)

    def closedDeviceFactoryUi(self, valuesDict, userCancelled, devIdList):
        return

    def validatePrefsConfigUi(self, valuesDict):
        return True

    def actionControlDimmerRelay(self, pluginAction, indigoDevice):
        try:
            properties = indigoDevice.pluginProps

            address = properties["address"]

            identifiers = self.getIdentifiers(address)

            nodeId = identifiers[0]
            childId = identifiers[1]

            #if pluginAction.deviceAction == indigo.kDimmerRelayAction.RequestStatus:
            #    self.sendRequestVariableCommand(nodeId, childId, "LIGHT", "")
            #
            #    return
            #el
            if pluginAction.deviceAction == indigo.kDimmerRelayAction.TurnOn:
                onOffState = True
            elif pluginAction.deviceAction == indigo.kDimmerRelayAction.TurnOff:
                onOffState = False
            elif pluginAction.deviceAction == indigo.kDimmerRelayAction.Toggle:
                onOffState = not indigoDevice.onState

            self.updateState(indigoDevice, "LIGHT", onOffState)

            if onOffState:
                value = 1
            else:
                value = 0

            self.sendSetVariableCommand(nodeId, childId, "LIGHT", value)
        except:
			indigo.server.log(u"action failed: %s" % "%s" % sys.exc_info()[0], isError = True)

    ########################################
    # actions
    ########################################
    def send(self, pluginAction):
        self.debugLog(u"Send method called")

    ########################################
    # events
    ########################################
    def triggerStartProcessing(self, trigger):
        status = trigger.pluginProps["status"]

        self.debugLog(u"Start processing trigger: %s for: %s status: %s" % (unicode(trigger.id), "sensor", status))

        triggerType = trigger.pluginTypeId

    def triggerStopProcessing(self, trigger):
        status = trigger.pluginProps["status"]

        self.debugLog(u"Stop processing trigger: %s for: %s status: %s" % (unicode(trigger.id), "sensor", status))

        triggerType = trigger.pluginTypeId

    ########################################
    # Incoming messages
    ########################################
    def processIncoming(self):
        arguments = None

        request = None
        nodeId = kBoardNodeId
        childId = -1
        messageType = -1
        itemType = -1
        payload = ""

        try:
            request = self.connection.readline()
        except:
            error = "%s" % sys.exc_info()[0]

            indigo.server.log(u"process incoming failed: %s" % error, isError = True)

            if "serial" in error:
                self.connection = None

                return

            request = None
        finally:
            if request:
                request = request.strip("\n\r")

                self.debugLog("receiving raw command %s" % request)

                if len(request) == 0:
                    payload = "empty request"
                elif request[0].isalpha() or request.find(";") == -1 or request.count(";") < 4:
                    payload = request
                else:
                    try:
                        arguments = request.split(";")

                        nodeId = int(arguments[0])
                        childId = int(arguments[1])
                        messageType = int(arguments[2])
                        itemType = int(arguments[3])
                        payload = ";".join(arguments[4:])
                    except:
                        nodeId = kBoardNodeId
                        childId = -1
                        messageType = -1
                        itemType = -1
                        payload = request

                if messageType == self.getMessageNumber("PRESENTATION"):
                    self.processPresentationCommand(nodeId, childId, itemType, payload)
                elif messageType == self.getMessageNumber("SET_VARIABLE"):
                    self.processSetVariableCommand(nodeId, childId, itemType, payload)
                elif messageType == self.getMessageNumber("REQ_VARIABLE"):
                    self.processRequestVariableCommand(nodeId, childId, itemType, payload)
                elif messageType == self.getMessageNumber("INTERNAL"):
                    self.processInternalCommand(nodeId, childId, itemType, payload)
                else:
                    indigo.server.log(u"raw command failed: (%s)" % payload, isError = True)

    def processPresentationCommand(self, nodeId, childId, itemType, payload):
        indigo.server.log(u"PRESENTATION %s (%s:%s) %s" % (self.getSensorName(itemType), nodeId, childId, payload))

        address = self.getAddress(nodeId = nodeId, childId = childId)

        device = self.checkDevice(address = address)

        model = self.getSensorName(itemType)

        try:
            if device:
                device = self.updateDevice(device, address, { "type" : itemType, "model" : model, "version" : payload })

                if device["id"]:
                    indigoDevice = indigo.devices[device["id"]]

                    if indigoDevice:
                        self.updateProperties(indigoDevice, { "type" : itemType, "model" : model, "version" : payload })
        except:
            pass

    def processSetVariableCommand(self, nodeId, childId, itemType, payload):
        try:
            device = self.checkDevice(nodeId = nodeId, childId = childId)
            if device and device["id"]:
                indigoDevice = indigo.devices[device["id"]]

                if indigoDevice:
                    value = self.updateState(indigoDevice, itemType, payload)

                    if value:
                        indigo.server.log(u"received \"%s\" %s" % (indigoDevice.name, value))
        except:
            self.errorLog(u"processSetVariableCommand failed: %s" % sys.exc_info()[0])
            pass

    def processRequestVariableCommand(self, nodeId, childId, itemType, payload):
        indigo.server.log \
            (u"received req variable %s (%s:%s) %s" % (self.getVariableText(itemType), nodeId, childId, payload))

        device = self.checkDevice(nodeId = nodeId, childId = childId)

        field = self.getVariableField(itemType)
        value = None

        try:
            if device and device["id"]:
                indigoDevice = indigo.devices[device["id"]]

                if indigoDevice:
                    value = indigoDevice.states[field]
        except:
            pass
        finally:
            value = self.getVariableValue(field, value)

            if value is not None:
                self.sendAcknowledgeVariableCommand(nodeId, childId, itemType, value)

    def processAcknowledgeVariableCommand(self, nodeId, childId, itemType, payload):
        indigo.server.log \
            (u"received acq variable %s (%s:%s) %s" % (self.getVariableText(itemType), nodeId, childId, payload))

        device = self.checkDevice(nodeId = nodeId, childId = childId)

        try:
            if device and device["id"]:
                indigoDevice = indigo.devices[device["id"]]

                if indigoDevice:
                    pass
        except:
            pass

    def processInternalCommand(self, nodeId, childId, itemType, payload):
        indigo.server.log(u"%s (%s:%s) %s" % (self.getInternalName(itemType), nodeId, childId, payload))

        if itemType == self.getInternalNumber("BATTERY_DATE"):
            # 1 Deprecated
            return
        elif itemType == self.getInternalNumber("LAST_TRIP"):
            # 2 Deprecated
            return
        elif itemType == self.getInternalNumber("LAST_UPDATE"):
            # 8 Deprecated
            return
        elif itemType == self.getInternalNumber("PING"):
            # 9 Ignore
            return
        elif itemType == self.getInternalNumber("PING_ACK"):
            # 10 Ignore
            return

        address = self.getAddress(nodeId = nodeId, childId = childId)

        device = self.checkDevice(address = address)

        indigoDevice = None

        try:
            if device and device["id"]:
                indigoDevice = indigo.devices[device["id"]]
        except:
            indigo.server.log(u"processing failed: %s" % sys.exc_info()[0], isError = True)

        if itemType == self.getInternalNumber("BATTERY_LEVEL"):
            # 0
            value = self.updateState(indigoDevice, "batteryLevel", payload)

            if value:
                indigo.server.log(u"received \"%s\" %s" % (indigoDevice.name, value))
        elif itemType == self.getInternalNumber("TIME"):
            # 3
            self.sendInternalCommand(nodeId, childId, itemType, time.time())
        elif itemType == self.getInternalNumber("VERSION"):
            # 4
            self.updateDevice(device, address, { "version" : payload })

            self.updateProperties(indigoDevice, { "version" : payload})
        elif itemType == self.getInternalNumber("REQUEST_ID"):
            # 5
            self.sendInternalCommand(nodeId, childId, itemType, self.nextAvailableNodeId())
        elif itemType == self.getInternalNumber("INCLUSION_MODE"):
            # 6
            if nodeId == 0 and childId == 0:
                if payload == "1":
                    self.inclusionMode = True
                else:
                    self.inclusionMode = False
        elif itemType == self.getInternalNumber("RELAY_NODE"):
            # 7
            if payload == "1":
                self.updateState(indigoDevice, "state", kOnlineState)
            elif indigoDevice and indigoDevice.errorState != kOfflineState:
                indigoDevice.setErrorStateOnServer(kOfflineState)
        elif itemType == self.getInternalNumber("LOG_MESSAGE"):
            # 11
            if "Arduino startup complete" in payload:
                self.updateState(indigoDevice, "state", kOnlineState)

                self.sendInternalCommand(nodeId, childId, "VERSION", "Get version")

                self.startInclusionMode()
        elif itemType == self.getInternalNumber("CHILDREN"):
            # 12
            self.updateProperties(indigoDevice, { "children" : payload })
        elif itemType == self.getInternalNumber("UNIT"):
            # 13
            self.sendInternalCommand(nodeId, childId, itemType, self.unit)
        elif itemType == self.getInternalNumber("SKETCH_NAME"):
            # 14
            self.updateDevice(device, address, { "model" : payload })

            self.updateProperties(indigoDevice, { "model" : payload })
        elif itemType == self.getInternalNumber("SKETCH_VERSION"):
            # 15
            self.updateDevice(device, address, { "modelVersion" : payload })

            self.updateProperties(indigoDevice, { "modelVersion" : payload })

    ########################################
    # Outgoing messages
    ########################################
    def sendPresentationCommand(self, nodeId, childId, itemType, value):
        itemType = self.getSensorNumber(itemType)

        self.sendCommand(nodeId, childId, "PRESENTATION", itemType, value)

    def sendAcknowledgeVariableCommand(self, nodeId, childId, itemType, value):
        itemType = self.getVariableNumber(itemType)

        self.sendCommand(nodeId, childId, "ACK_VARIABLE", itemType, value)

    def sendSetVariableCommand(self, nodeId, childId, itemType, value):
        itemType = self.getVariableNumber(itemType)

        self.sendCommand(nodeId, childId, "SET_VARIABLE", itemType, value)

    def sendRequestVariableCommand(self, nodeId, childId, itemType, value):
        itemType = self.getVariableNumber(itemType)

        self.sendCommand(nodeId, childId, "REQ_VARIABLE", itemType, value)

    def sendInternalCommand(self, nodeId, childId, itemType, value):
        itemType = self.getInternalNumber(itemType)

        self.sendCommand(nodeId, childId, "INTERNAL", itemType, value)

    def sendCommand(self, nodeId, childId, messageType, itemType, value):
        messageType = self.getMessageNumber(messageType)

        command = "%s;%s;%s;%s;%s" % (nodeId, childId, messageType, itemType, value)

        if self.connection and self.connection.writable:
            self.connection.write(command + "\n")
            self.debugLog(u"Sending Command %s" % command)

            return True
        else:
            indigo.server.log(u"send command %s failed: Can't write to serial port" % command, isError = True)

            return False

    ########################################
    # Device methods
    ########################################
    def checkDevice(self, indigoDevice = None, nodeId = None, childId = None, address = None):
        if nodeId and (nodeId == -1 or nodeId == kBoardNodeId or childId == -1):
            return None

        if not address:
            address = self.getAddress(nodeId = nodeId, childId = childId)
        else:
            address = self.getAddress(address = address)

            identifiers = self.getIdentifiers(address)

            nodeId = identifiers[0]
            childId = identifiers[1]

        #if self.inclusionMode or indigoDevice or nodeId == 0:

        if not address in self.devices:
            device = self.createDevice(nodeId, childId, address)
        else:
            device = self.devices[address]

            if indigoDevice:
                properties = { "id" : indigoDevice.id }

                self.updateDevice(device, address, properties)

            self.updateNodeIds(nodeId, False)

        if self.connection and device and nodeId != kMaxNodeId:
            if not device["version"]:
                self.sendInternalCommand(nodeId, childId, "VERSION", "Get Version")

            if device["type"] != self.getSensorNumber("ARDUINO_NODE") and device["type"] != self.getSensorNumber \
                            ("ARDUINO_RELAY"):
                if not device["model"]:
                    self.sendInternalCommand(nodeId, childId, "SKETCH_NAME", "Get Sketch Name")

                #if not device["modelVersion"]:
                #    self.sendInternalCommand(nodeId, childId, "SKETCH_VERSION", "Get Sketch Version")

        if address in self.devices:
            return self.devices[address]
        else:
            return None

    def createDevice(self, nodeId, childId, address):
        device = indigo.Dict()

        if nodeId == 0:
            device["type"] = self.getSensorNumber("ARDUINO_NODE")
        else:
            device["type"] = -1

        device["version"] = ""
        device["id"] = ""
        device["model"] = self.getSensorName(device["type"])
        device["modelVersion"] = ""

        self.devices[address] = device

        self.pluginPrefs["devices"] = self.devices

        self.updateNodeIds(nodeId, False)

    def updateDevice(self, device, address, properties):
        if not device:
            return

        self.debugLog(u"updateDevice %s %s" % (properties, address))

        updated = False

        for property in properties:
            if not hasattr(device, property) or not device[property] == properties[property]:
                device[property] = properties[property]

                updated = True

        if updated:
            self.devices[address] = device

            self.pluginPrefs["devices"] = self.devices

        return device

    def updateNodeIds(self, nodeId, value):
        if nodeId == kMaxNodeId:
            return

        id = "N%s" % nodeId

        if self.nodeIds[id] != value:
            self.nodeIds[id] = value

            self.pluginPrefs["nodeIds"] = self.nodeIds

    def updateState(self, indigoDevice, itemType, payload):
        if not indigoDevice:
            return

        name = self.getVariableText(itemType)
        field = self.getVariableField(itemType)

        uiValue = None

        if field == "temperature":
            value = float(payload)

            if self.unit == "M":
                uiValue = u"%.1f °C" % value
            else:
                uiValue = u"%.1f °F" % value
        elif field == "onOffState":
            value = self.booleanValue(payload)
        elif field == "onoroff":
            value = self.booleanValue(payload)

            if value:
                uiValue = u"on"
            else:
                uiValue = u"off"
        else:
            value = str(payload)

        if indigoDevice:
            if value != indigoDevice.states[field]:
                if uiValue:
                    indigoDevice.updateStateOnServer(field, value = value, uiValue = uiValue)

                    return u"%s %s" % (name, uiValue)
                else:
                    indigoDevice.updateStateOnServer(field, value = value)

                    return u"%s %s" % (name, value)

        return None

    def updateProperties(self, indigoDevice, properties):
        if not indigoDevice:
            return

        indigoProperties = indigoDevice.pluginProps

        for property in properties:
            if hasattr(indigoProperties, property) and indigoProperties[property] == properties[property]:
                del properties[property]

        if len(properties) > 0:
            indigoProperties.update(properties)
            indigoDevice.replacePluginPropsOnServer(indigoProperties)

    def hasChildren(self, selectedNodeId):
        for address in self.devices:
            device = self.devices[address]

            identifiers = self.getIdentifiers(address)

            nodeId = identifiers[0]
            childId = identifiers[1]

            if nodeId == selectedNodeId and childId < kBoardChildId and device["type"] > -1:
                return True

        return False

    def addIndigoChildren(self, selectedNodeId):
        if selectedNodeId == 0:
            boardAddress = self.getAddress(nodeId = selectedNodeId, childId = 0)
        else:
            boardAddress = self.getAddress(nodeId = selectedNodeId, childId = kBoardChildId)

        board = self.getDevice(address = boardAddress)

        for address in self.devices:
            try:
                identifiers = self.getIdentifiers(address)

                nodeId = identifiers[0]
                childId = identifiers[1]

                if selectedNodeId == nodeId and address != boardAddress:
                    device = self.getDevice(address = address)

                    deviceName = self.getSensorName(device["type"])
                    deviceType = self.getSensorKey(device["type"])

                    indigoDevice = indigo.device.create(indigo.kProtocol.Plugin, deviceTypeId = deviceType)

                    if board["model"]:
                        boardModel = board["model"]
                    else:
                        boardModel = self.getSensorName(board["type"])

                    if board["modelVersion"]:
                        indigoDevice.model = ("%s (%s)" % (boardModel, board["modelVersion"]))
                    else:
                        indigoDevice.model = ("%s" % boardModel)

                    indigoDevice.subModel = deviceName

                    indigoDevice.replaceOnServer()

                    self.updateDevice(device, address, { "id" : indigoDevice.id })

                    properties = dict()

                    if address:
                        properties["address"] = self.formatAddress(address)
                    else:
                        properties["address"] = ""

                    if deviceType:
                        properties["deviceType"] = self.getSensorNumber(device["type"])
                    else:
                        properties["deviceType"] = -1

                    if device["version"]:
                        properties["version"] = device["version"]
                    else:
                        properties["version"] = ""

                    if indigoDevice.model:
                        properties["model"] = indigoDevice.model
                    else:
                        properties["model"] = ""

                    self.updateProperties(indigoDevice, properties)

                    self.sendInternalCommand(nodeId, childId, "VERSION", "Get version")
            except:
                indigo.server.log(u"add children failed: %s" % sys.exc_info()[0], isError = True)

    def loadDevices(self):
        if "devices" in self.pluginPrefs:
            self.devices = self.pluginPrefs["devices"]

        self.debugLog(u"devices:\n%s" % self.devices)

        if "nodeIds" in self.pluginPrefs:
            self.nodeIds = self.pluginPrefs["nodeIds"]
        else:
            self.setupNodeIds()

        #self.debugLog(u"nodeIds:\n%s" % self.nodeIds)

        for deviceId in indigo.devices.iter("self"):
            try:
                indigoDevice = indigo.devices[deviceId]

                #self.debugLog(u"indigoDevice:\n%s" % indigoDevice)
                self.debugLog(u"indigoDevice: %s %s %s" % (indigoDevice.name, indigoDevice.id, indigoDevice.address))

                if indigoDevice.address:
                    address = self.getAddress(address = indigoDevice.address)

                    self.checkDevice(indigoDevice, address = address)

                properties = indigoDevice.pluginProps

                if len(properties) > 0:
                    if properties["deviceType"] == "ARDUINO_NODE" or properties["deviceType"] == "ARDUINO_RELAY":
                        if self.connection and self.connection.isOpen():
                            self.updateState(indigoDevice, "state", kOnlineState)
                        elif indigoDevice and indigoDevice.errorState != kOfflineState:
                            indigoDevice.setErrorStateOnServer(kOfflineState)
            except:
                indigo.server.log(u"load devices failed %s" % sys.exc_info()[0], isError = True)

    def getDevice(self, nodeId = None, childId = None, address = None):
        device = None

        if not address:
            address = self.getAddress(nodeId = nodeId, childId = childId)

        try:
            device = self.devices[address]
        except:
            pass

        self.debugLog(u"getDevice device: %s" % device)

        return device

    ########################################
    # Lookup methods
    ########################################
    def getMessageNumber(self, itemType):
        if isinstance(itemType, int):
            return itemType
        elif itemType in kMessageTypes:
            return kMessageTypes[itemType]

        return -1

    def getMessageKey(self, itemType):
        if isinstance(itemType, int):
            for key in kMessageTypes:
                if kMessageTypes[key][0] == itemType:
                    return key
        elif itemType in kMessageTypes:
            return itemType

        return None

    def getSensorNumber(self, itemType):
        if isinstance(itemType, int):
            return itemType
        elif itemType in kSensorTypes:
            return kSensorTypes[itemType][0]

        return -1

    def getSensorName(self, itemType):
        if isinstance(itemType, int):
            for key in kSensorTypes:
                if kSensorTypes[key][0] == itemType:
                    return kSensorTypes[key][1]
        elif itemType in kSensorTypes:
            return kSensorTypes[itemType][1]

        return ""

    def getSensorKey(self, itemType):
        if isinstance(itemType, int):
            for key in kSensorTypes:
                if kSensorTypes[key][0] == itemType:
                    return key
        elif itemType in kSensorTypes:
            return itemType

        return None

    def getVariableNumber(self, itemType):
        if isinstance(itemType, int):
            return itemType
        elif itemType in kVariableTypes:
            return kVariableTypes[itemType][0]

        return -1

    def getVariableField(self, itemType):
        if isinstance(itemType, int):
            for key in kVariableTypes:
                if kVariableTypes[key][0] == itemType:
                    return kVariableTypes[key][1]
        elif itemType in kVariableTypes:
            return kVariableTypes[itemType][1]

        return None

    def getVariableText(self, itemType):
        if isinstance(itemType, int):
            for key in kVariableTypes:
                if kVariableTypes[key][0] == itemType:
                    return kVariableTypes[key][2]
        elif itemType in kVariableTypes:
            return kVariableTypes[itemType][2]

        return None

    def getVariableKey(self, itemType):
        if isinstance(itemType, int):
            for key in kVariableTypes:
                if kVariableTypes[key][0] == itemType:
                    return key
        elif itemType in kVariableTypes:
            return itemType

        return None

    def getInternalNumber(self, itemType):
        if isinstance(itemType, int):
            return itemType
        elif itemType in kInternalTypes:
            return kInternalTypes[itemType][0]

        return -1

    def getInternalName(self, itemType):
        if isinstance(itemType, int):
            for key in kInternalTypes:
                if kInternalTypes[key][0] == itemType:
                    return kInternalTypes[key][1]
        elif itemType in kInternalTypes:
            return kInternalTypes[itemType][1]

        return None

    def getInternalKey(self, itemType):
        if isinstance(itemType, int):
            for key in kInternalTypes:
                if kInternalTypes[key][0] == itemType:
                    return key
        elif itemType in kInternalTypes:
            return itemType

        return None

    def nextAvailableNodeId(self):
        for nodeId in range(1, kMaxNodeId):
            id = "N%s" % nodeId

            if self.nodeIds[id]:
                return nodeId

        return kMaxNodeId

    ########################################
    # Helper methods
    ########################################
    def getAddress(self, nodeId = None, childId = None, address = None):
        if address:
            try:
                identifiers = self.getIdentifiers(address)

                nodeId = identifiers[0]
                childId = identifiers[1]
            except:
                pass

        return "N%sC%s" % (nodeId, childId)

    def getIdentifiers(self, address):
        if address:
            if address[0].isalpha():
                try:
                    identifiers = address[1:].split("C")

                    return [ int(identifiers[0]), int(identifiers[1]) ]
                except:
                    pass
            elif ":" in address:
                try:
                    identifiers = address.split(":")

                    return [ int(identifiers[0]), int(identifiers[1]) ]
                except:
                    pass

        return None

    def formatAddress(self, address):
        try:
            identifiers = self.getIdentifiers(address)

            return "%s:%s" % (identifiers[0], identifiers[1])
        except:
            pass

        return ""

    def setupNodeIds(self):
        for index in range(0, kMaxNodeId):
            id = "N%s" % index

            self.nodeIds[id] = True

        self.updateNodeIds(0, False)

    def booleanValue(self, value):
        try:
            if isinstance(value, int) or isinstance(value, float):
                return value > 0
            elif isinstance(value, str):
                return value.lower() in [ "yes", "true", "t", "1" ]
            elif type(value) is bool:
                return value
        except:
            pass

        return None

    def numberValue(self, value):
        try:
            if isinstance(value, int):
                return int(value)
            elif isinstance(value, float):
                return float(value)
            elif type(value) is bool:
                if value:
                    return 1
                else:
                    return 0
        except:
            pass

        return None

    ########################################
    # Start connecting
    ########################################
    def openConnection(self):
        if self.address:
            self.connection = self.openSerial("com.it2be.indigo.mysensors", portUrl = self.address, baudrate = kBaudrate, timeout = 0)
        else:
            self.address = "undefined"

        address = self.getAddress(nodeId = 0, childId = 0)

        device = None
        indigoDevice = None

        if "address" in self.devices:
            device = self.devices[address]

            if device and device["id"]:
                indigoDevice = indigo.devices[device["id"]]

        if self.connection:
            self.connectionAttempts = 0

            indigo.server.log(u"Connected at address: %s (baudrate: %s)" % (self.address, kBaudrate))

            return True
        else:
            self.connectionAttempts = self.connectionAttempts + 1

            return False

    ########################################
    # Config Methods
    ########################################
    def loadSerialPorts(self, filter = "", valuesDict = None, typeId = "", targetId = 0):
        self.debugLog(u"Ports loading")

        returnList = list()

        if not valuesDict:
            valuesDict = {}

        portList = glob.glob("/dev/tty.*") + glob.glob("/dev/cu.*")

        for port in portList:
            if "usb" in port.lower():
                returnList.append((port, port))

        return returnList

    ########################################
    # Menu Methods
    ########################################
    def toggleDebugging(self):
        if self.debug:
            indigo.server.log(u"Turning off debug logging")
            self.pluginPrefs["showDebugInfo"] = False
        else:
            indigo.server.log(u"Turning on debug logging")
            self.pluginPrefs["showDebugInfo"] = True

        self.debug = not self.debug

    def startInclusionMode(self):
        indigo.server.log(u"Turning on inclusion mode")

        self.inclusionMode = True

        self.interval = kWorkerSleep

        self.sendInternalCommand(kGatewayId, 0, "INCLUSION_MODE", 1)

    def stopInclusionMode(self):
        indigo.server.log(u"Turning off inclusion mode")

        self.interval = kInterval

        self.inclusionMode = False

        self.sendInternalCommand(kGatewayId, 0, "INCLUSION_MODE", 0)

    def reloadDevices(self):
        indigo.server.log(u"Reload devices")

        self.devices = indigo.Dict()
        self.nodeIds = indigo.Dict()

        self.setupNodeIds()

        self.pluginPrefs["devices"] = self.devices
        self.pluginPrefs["nodeIds"] = self.nodeIds

        self.startInclusionMode()

        self.loadDevices()
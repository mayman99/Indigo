class core(object):

    def str2bool(self, value):
        return value.lower() in ("yes", "true", "t", "1")

    def str2num(self, value):
        try:
            return int(value)
        except ValueError:
            return float(value)

    def temp():
        if itemType == self.variableTypes["TEMP"][0]:
            pass
        elif itemType == self.variableTypes["HUM"][0]:
            pass
        elif itemType == self.variableTypes["LIGHT"][0]:
            pass
        elif itemType == self.variableTypes["DIMMER"][0]:
            pass
        elif itemType == self.variableTypes["PRESSURE"][0]:
            pass
        elif itemType == self.variableTypes["FORECAST"][0]:
            pass
        elif itemType == self.variableTypes["RAIN"][0]:
            pass
        elif itemType == self.variableTypes["RAINRATE"][0]:
            pass
        elif itemType == self.variableTypes["WIND"][0]:
            pass
        elif itemType == self.variableTypes["GUST"][0]:
            pass
        elif itemType == self.variableTypes["DIRECTION"][0]:
            pass
        elif itemType == self.variableTypes["UV"][0]:
            pass
        elif itemType == self.variableTypes["WEIGHT"][0]:
            pass
        elif itemType == self.variableTypes["DISTANCE"][0]:
            pass
        elif itemType == self.variableTypes["IMPEDANCE"][0]:
            pass
        elif itemType == self.variableTypes["ARMED"][0]:
            pass
        elif itemType == self.variableTypes["TRIPPED"][0]:
            pass
        elif itemType == self.variableTypes["WATT"][0]:
            pass
        elif itemType == self.variableTypes["KWH"][0]:
            pass
        elif itemType == self.variableTypes["SCENE_ON"][0]:
            pass
        elif itemType == self.variableTypes["SCENE_OFF"][0]:
            pass
        elif itemType == self.variableTypes["HEATER"][0]:
            pass
        elif itemType == self.variableTypes["HEATER_SW"][0]:
            pass
        elif itemType == self.variableTypes["LIGHT_LEVEL"][0]:
            pass
        elif itemType == self.variableTypes["VAR_1"][0]:
            pass
        elif itemType == self.variableTypes["VAR_2"][0]:
            pass
        elif itemType == self.variableTypes["VAR_3"][0]:
            pass
        elif itemType == self.variableTypes["VAR_4"][0]:
            pass
        elif itemType == self.variableTypes["VAR_5"][0]:
            pass
        elif itemType == self.variableTypes["UP"][0]:
            pass
        elif itemType == self.variableTypes["DOWN"][0]:
            pass
        elif itemType == self.variableTypes["STOP"][0]:
            pass
        elif itemType == self.variableTypes["IR_SEND"][0]:
            pass
        elif itemType == self.variableTypes["IR_RECEIVE"][0]:
            pass
        elif itemType == self.variableTypes["FLOW"][0]:
            pass
        elif itemType == self.variableTypes["VOLUME"][0]:
            pass
        elif itemType == self.variableTypes["LOCK_STATUS"][0]:
            pass